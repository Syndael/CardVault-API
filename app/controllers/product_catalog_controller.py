import mimetypes
import os
import re
from io import BytesIO
from math import ceil
from urllib.parse import quote

import requests
from flask import Blueprint, g, jsonify, request, send_file, make_response
from sqlalchemy import text

import app.auth as auth
from app.database.session import db
from app.utils.pagination import get_pagination_params

_FT_SPECIAL = re.compile(r'[+\-~*()"@><]')

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

product_catalog_blueprint = Blueprint("product_catalog", __name__)

def _search_clause(search_terms):
    if not search_terms:
        return "", False

    like_clauses = []
    for i in range(len(search_terms)):
        like_clauses.append(f"(c.code LIKE :q_{i} OR p.product_number LIKE :q_{i} OR pt.name LIKE :q_{i})")

    clean = [_FT_SPECIAL.sub(" ", t).strip() for t in search_terms]
    clean = [t for t in clean if t]

    parts = []
    has_ft = False
    if clean:
        has_ft = True
        parts.append(
            "EXISTS (SELECT 1 FROM product_translations pt_ft "
            "WHERE pt_ft.product_id = p.id "
            "AND MATCH(pt_ft.name, pt_ft.name_alter) AGAINST(:ft_q IN BOOLEAN MODE))"
        )
        parts.append(
            "EXISTS (SELECT 1 FROM collection_translations ct_ft "
            "WHERE ct_ft.collection_id = c.id "
            "AND MATCH(ct_ft.name, ct_ft.name_alter) AGAINST(:ft_q IN BOOLEAN MODE))"
        )

    if like_clauses:
        parts.append(f"({' AND '.join(like_clauses)})")

    return "AND (" + " OR ".join(parts) + ")", has_ft

CATALOG_BASE_FROM = """
FROM products p
INNER JOIN collections c ON c.id = p.collection_id
"""

CATALOG_TEXT_JOINS = """
LEFT JOIN (
    SELECT pt2.id, pt2.product_id, pt2.name, pt2.name_alter,
           ROW_NUMBER() OVER (
               PARTITION BY pt2.product_id
               ORDER BY l2.priority_order, l2.id, pt2.id
           ) AS rn
    FROM product_translations pt2
    INNER JOIN languages l2 ON l2.id = pt2.language_id
    WHERE (:product_type_id = -1) OR (pt2.product_id IN (
        SELECT id FROM products WHERE product_type_id = :product_type_id
    ))
) pt ON pt.product_id = p.id AND pt.rn = 1
LEFT JOIN (
    SELECT ct2.id, ct2.collection_id, ct2.name, ct2.name_alter,
           ROW_NUMBER() OVER (
               PARTITION BY ct2.collection_id
               ORDER BY l3.priority_order, l3.id, ct2.id
           ) AS rn
    FROM collection_translations ct2
    INNER JOIN languages l3 ON l3.id = ct2.language_id
    WHERE (:product_type_id = -1) OR (ct2.collection_id IN (
        SELECT DISTINCT p2.collection_id FROM products p2
        WHERE p2.product_type_id = :product_type_id
    ))
) ct ON ct.collection_id = c.id AND ct.rn = 1
"""

CATALOG_FILES_JOIN = """
LEFT JOIN (
    SELECT f2.id, f2.product_id,
           ROW_NUMBER() OVER (
               PARTITION BY f2.product_id
               ORDER BY (lfile.priority_order IS NULL), lfile.priority_order, f2.id
           ) AS rn
    FROM files f2
    LEFT JOIN languages lfile ON lfile.id = f2.language_id
    WHERE (:product_type_id = -1) OR (f2.product_id IN (
        SELECT id FROM products WHERE product_type_id = :product_type_id
    ))
) f ON f.product_id = p.id AND f.rn = 1
"""

CATALOG_TRACKER_JOIN = """
LEFT JOIN (
    SELECT ppt.product_id, ppt.url,
           ROW_NUMBER() OVER (
               PARTITION BY ppt.product_id
               ORDER BY ppt.id DESC
           ) AS rn
    FROM product_price_tracking ppt
    WHERE (:product_type_id = -1) OR (ppt.product_id IN (
        SELECT id FROM products WHERE product_type_id = :product_type_id
    ))
) tracker ON tracker.product_id = p.id AND tracker.rn = 1
"""

CATALOG_WHERE = """
WHERE 1=1
AND (:is_verified = -1 OR p.is_verified = :is_verified)
AND (:is_manual = -1 OR c.is_manual = :is_manual)
AND (:product_type_id = -1 OR p.product_type_id = :product_type_id)
AND (:product_format_id = -1 OR p.product_format_id = :product_format_id)
AND (:collection_code = '' OR c.code = :collection_code)
AND (:product_number = '' OR p.product_number LIKE :product_number_like)
AND (:product_name = '' OR pt.name LIKE :product_name_like OR pt.name_alter LIKE :product_name_like)
AND (
    :pending_sync = 0
    OR (
        c.is_manual = 0
        AND (
            p.force_download = 1
            OR NOT EXISTS (
                SELECT 1 FROM product_translations pt2
                WHERE pt2.product_id = p.id
            )
        )
    )
)
"""

CATALOG_SELECT_FROM = (
    CATALOG_BASE_FROM
    + CATALOG_TEXT_JOINS
    + CATALOG_FILES_JOIN
    + CATALOG_TRACKER_JOIN
)


def format_name(name, name_alter):
    if name and name_alter:
        return f"{name} ({name_alter})"
    if name:
        return name
    return name_alter or name


@product_catalog_blueprint.route("/", methods=["GET"])
@auth.require_role("product_read", "admin")
def get_products():
    page, per_page = get_pagination_params()
    raw_q = (request.args.get("q") or "").strip()
    search_terms = [t for t in raw_q.split() if t]
    raw_verified = request.args.get("is_verified")
    raw_manual = request.args.get("is_manual")
    raw_type_id = request.args.get("product_type_id")
    raw_format_id = request.args.get("product_format_id")
    raw_pending = request.args.get("pending_sync")
    raw_col_code = (request.args.get("collection_code") or "").strip()
    raw_prod_number = (request.args.get("product_number") or "").strip()
    raw_prod_name = (request.args.get("product_name") or "").strip()
    params = {
        "is_verified": int(raw_verified) if raw_verified in ("0", "1") else -1,
        "is_manual": int(raw_manual) if raw_manual in ("0", "1") else -1,
        "product_type_id": int(raw_type_id) if raw_type_id else -1,
        "product_format_id": int(raw_format_id) if raw_format_id else -1,
        "pending_sync": 1 if raw_pending == "1" else 0,
        "collection_code": raw_col_code,
        "product_number": raw_prod_number,
        "product_number_like": f"%{raw_prod_number}%",
        "product_name": raw_prod_name,
        "product_name_like": f"%{raw_prod_name}%",
        "limit": per_page,
        "offset": (page - 1) * per_page
    }
    for i, term in enumerate(search_terms):
        params[f"q_{i}"] = f"%{term}%"

    search_sql, has_ft = _search_clause(search_terms)
    if has_ft:
        clean = [_FT_SPECIAL.sub(" ", t).strip() for t in search_terms]
        clean = [t for t in clean if t]
        params["ft_q"] = " ".join(f"+{t}" for t in clean)

    has_text_filters = bool(search_terms) or bool(raw_prod_name)

    # COUNT query: skip window-function joins when possible
    if search_terms:
        total = db.session.execute(
            text(f"SELECT COUNT(*) {CATALOG_SELECT_FROM} {CATALOG_WHERE} {search_sql}"),
            params
        ).scalar()
    elif raw_prod_name:
        total = db.session.execute(
            text(f"SELECT COUNT(*) {CATALOG_SELECT_FROM} {CATALOG_WHERE}"),
            params
        ).scalar()
    else:
        total = db.session.execute(
            text(f"""
                SELECT COUNT(*)
                {CATALOG_BASE_FROM}
                WHERE 1=1
                AND (:is_verified = -1 OR p.is_verified = :is_verified)
                AND (:is_manual = -1 OR c.is_manual = :is_manual)
AND (:product_type_id = -1 OR p.product_type_id = :product_type_id)
AND (:product_format_id = -1 OR p.product_format_id = :product_format_id)
                AND (:collection_code = '' OR c.code = :collection_code)
                AND (:product_number = '' OR p.product_number LIKE :product_number_like)
                AND (
                    :pending_sync = 0
                    OR (
                        c.is_manual = 0
                        AND (
                            p.force_download = 1
                            OR NOT EXISTS (
                                SELECT 1 FROM product_translations pt2
                                WHERE pt2.product_id = p.id
                            )
                        )
                    )
                )
            """),
            params
        ).scalar()

    rows = db.session.execute(
        text(
            f"""
            SELECT
                p.id AS product_id,
                c.id AS collection_id,
                c.code AS collection_code,
                CAST(c.is_manual AS UNSIGNED) AS collection_is_manual,
                CAST(p.is_manual AS UNSIGNED) AS product_is_manual,
                CAST(p.force_download AS UNSIGNED) AS force_download,
                ct.name AS collection_name,
                ct.name_alter AS collection_name_alter,
                p.product_number AS product_number,
                pt.name AS product_name,
                pt.name_alter AS product_name_alter,
                CAST(p.is_verified AS UNSIGNED) AS is_verified,
                f.id AS file_id,
                tracker.url AS tracker_url
            {CATALOG_SELECT_FROM} {CATALOG_WHERE} {search_sql}
            ORDER BY
                c.code,
                c.is_manual,
                CAST(p.product_number AS UNSIGNED),
                p.product_number,
                pt.name
            LIMIT :limit OFFSET :offset
            """
        ),
        params
    ).mappings().all()

    pages = ceil(total / per_page) if total else 0
    items = []

    for row in rows:
        file_id = row["file_id"]
        tracker_url = row.get("tracker_url") if isinstance(row, dict) or hasattr(row, 'get') else None
        items.append(
            {
                "product_id": row["product_id"],
                "collection_id": row["collection_id"],
                "collection_code": row["collection_code"],
                "collection_is_manual": row["collection_is_manual"] == 1,
                "product_is_manual": row["product_is_manual"] == 1,
                "force_download": row["force_download"] == 1,
                "is_verified": row["is_verified"] == 1,
                "collection_name": row["collection_name"],
                "product_number": row["product_number"],
                "product_name": format_name(
                    row["product_name"],
                    row["product_name_alter"]
                ),
                "image_url": (
                    f"/api/product-catalog/files/{file_id}/content"
                    if file_id
                    else None
                ),
                "tracker_url": tracker_url
            }
        )

    return jsonify(
        {
            "items": items,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": pages,
                "has_next": page < pages,
                "has_prev": page > 1 and pages > 0
            }
        }
    )


def resolve_file_path(file_path):
    candidates = []
    if os.path.isabs(file_path):
        candidates.append(file_path)
    else:
        cwd = os.getcwd()
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
        candidates.extend(
            [
                os.path.abspath(os.path.join(cwd, file_path)),
                os.path.abspath(os.path.join(repo_root, file_path)),
                os.path.abspath(os.path.join(repo_root, "Tasks", file_path))
            ]
        )

    for candidate in candidates:
        if os.path.isfile(candidate):
            return candidate

    return None


@product_catalog_blueprint.route("/suggest-urls", methods=["GET"])
def suggest_urls():
    collection_code = request.args.get("collection_code", "").strip()
    product_number = request.args.get("product_number", "").strip()
    product_name = request.args.get("product_name", "").strip()

    parts = [p for p in [collection_code, product_number, product_name] if p]
    if not parts:
        return jsonify({"cardmarket": None, "pricecharting": None})

    base_query = " ".join(parts)

    def search_ddg(query):
        try:
            sess = requests.Session()
            sess.get("https://lite.duckduckgo.com/lite/", timeout=10, headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
            })
            resp = sess.post("https://lite.duckduckgo.com/lite/", data={"q": query}, timeout=15, headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
            })
            if not resp.ok:
                return []
            link_re = re.compile(r'<a[^>]+href="(https?://[^"]+)"')
            return link_re.findall(resp.text)
        except Exception:
            return []

    cm_links = search_ddg(base_query + " cardmarket")
    pc_links = search_ddg(base_query + " pricecharting")

    cardmarket_url = None
    pricecharting_url = None

    for link in cm_links:
        if "cardmarket.com" in link:
            cardmarket_url = link
            break

    for link in pc_links:
        if "pricecharting.com/game/" in link:
            pricecharting_url = link
            break
    if not pricecharting_url:
        for link in pc_links:
            if "pricecharting.com" in link:
                pricecharting_url = link
                break

    return jsonify({"cardmarket": cardmarket_url, "pricecharting": pricecharting_url})


@product_catalog_blueprint.route("/files/<int:file_id>/content", methods=["GET"])
def get_file_content(file_id):
    row = db.session.execute(
        text(
            """
            SELECT file_path, original_name
            FROM files
            WHERE id = :file_id
            """
        ),
        {
            "file_id": file_id
        }
    ).mappings().first()

    if not row:
        return jsonify({"message": "Not found"}), 404

    # Debugging aid: print minimal info about the request and the stored path
    try:
        auth_present = 'Authorization' in request.headers
    except Exception:
        auth_present = False
    print(f"get_file_content: file_id={file_id} auth_present={auth_present} db_file_path={row['file_path']}")

    resolved_path = resolve_file_path(row["file_path"])
    print(f"get_file_content: resolved_path={resolved_path}")
    if not resolved_path:
        return jsonify({"message": "File not found"}), 404

    # Guess mime type for a better Content-Type header when sending the file
    mime_type, _ = mimetypes.guess_type(resolved_path)
    if not mime_type:
        mime_type = "application/octet-stream"

    # Check if a specific size is requested (responsive images)
    size = request.args.get("size")
    if size and HAS_PIL and mime_type and mime_type.startswith("image/"):
        try:
            img = Image.open(resolved_path)
            width_map = {"sm": 200, "md": 400}
            target_width = width_map.get(size)
            if target_width and img.width > target_width:
                ratio = target_width / img.width
                target_height = int(img.height * ratio)
                img = img.resize((target_width, target_height), Image.LANCZOS)
                buf = BytesIO()
                fmt = img.format or "JPEG"
                img.save(buf, fmt, quality=85)
                buf.seek(0)
                resp = send_file(
                    buf,
                    download_name=row["original_name"],
                    as_attachment=False,
                    mimetype=mime_type,
                )
                resp.headers['Cache-Control'] = 'public, max-age=86400'
                return resp
        except Exception:
            pass

    resp = send_file(
        resolved_path,
        download_name=row["original_name"],
        as_attachment=False,
        mimetype=mime_type,
    )
    resp.headers['Cache-Control'] = 'public, max-age=86400'
    return resp


@product_catalog_blueprint.route("/files/<int:file_id>/content", methods=["OPTIONS"])
def get_file_content_options(file_id):
    # Explicitly respond to CORS preflight to ensure browsers receive the
    # expected Access-Control-Allow-* headers (helps some environments).
    resp = make_response(("", 200))
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    resp.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    return resp
