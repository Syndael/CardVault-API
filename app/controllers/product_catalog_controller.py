import mimetypes
import os
from math import ceil

from flask import Blueprint, g, jsonify, request, send_file, make_response
from sqlalchemy import text

import app.auth as auth
from app.database.session import db
from app.utils.pagination import get_pagination_params

product_catalog_blueprint = Blueprint("product_catalog", __name__)

CATALOG_FROM_SQL = """
FROM products p
INNER JOIN collections c ON c.id = p.collection_id
LEFT JOIN product_translations pt
    ON pt.id = (
        SELECT pt2.id
        FROM product_translations pt2
        INNER JOIN languages l2 ON l2.id = pt2.language_id
        WHERE pt2.product_id = p.id
        ORDER BY l2.priority_order, l2.id, pt2.id
        LIMIT 1
    )
LEFT JOIN collection_translations ct
    ON ct.id = (
        SELECT ct2.id
        FROM collection_translations ct2
        INNER JOIN languages l3 ON l3.id = ct2.language_id
        WHERE ct2.collection_id = c.id
        ORDER BY l3.priority_order, l3.id, ct2.id
        LIMIT 1
    )
LEFT JOIN files f
    ON f.id = (
        SELECT f2.id
        FROM files f2
        LEFT JOIN languages lfile ON lfile.id = f2.language_id
        WHERE f2.product_id = p.id
        ORDER BY (lfile.priority_order IS NULL), lfile.priority_order, f2.id
        LIMIT 1
    )
WHERE (
    :search = ''
    OR c.code LIKE :search_like
    OR p.product_number LIKE :search_like
    OR pt.name LIKE :search_like
    OR pt.name_alter LIKE :search_like
    OR ct.name LIKE :search_like
    OR ct.name_alter LIKE :search_like
)
AND (:is_verified = -1 OR p.is_verified = :is_verified)
AND (:is_manual = -1 OR c.is_manual = :is_manual)
AND (:product_type_id = -1 OR p.product_type_id = :product_type_id)
AND (:collection_code = '' OR c.code LIKE :collection_code_like)
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


def format_name(name, name_alter):
    if name and name_alter:
        return f"{name_alter} ({name})"
    if name_alter:
        return name_alter

    return name


@product_catalog_blueprint.route("/", methods=["GET"])
@auth.require_role("product_read", "admin")
def get_products():
    page, per_page = get_pagination_params()
    search = (request.args.get("q") or "").strip()
    raw_verified = request.args.get("is_verified")
    raw_manual = request.args.get("is_manual")
    raw_type_id = request.args.get("product_type_id")
    raw_pending = request.args.get("pending_sync")
    raw_col_code = (request.args.get("collection_code") or "").strip()
    raw_prod_number = (request.args.get("product_number") or "").strip()
    raw_prod_name = (request.args.get("product_name") or "").strip()
    params = {
        "search": search,
        "search_like": f"%{search}%",
        "is_verified": int(raw_verified) if raw_verified in ("0", "1") else -1,
        "is_manual": int(raw_manual) if raw_manual in ("0", "1") else -1,
        "product_type_id": int(raw_type_id) if raw_type_id else -1,
        "pending_sync": 1 if raw_pending == "1" else 0,
        "collection_code": raw_col_code,
        "collection_code_like": f"%{raw_col_code}%",
        "product_number": raw_prod_number,
        "product_number_like": f"%{raw_prod_number}%",
        "product_name": raw_prod_name,
        "product_name_like": f"%{raw_prod_name}%",
        "limit": per_page,
        "offset": (page - 1) * per_page
    }

    total = db.session.execute(
        text(f"SELECT COUNT(*) {CATALOG_FROM_SQL}"),
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
                ct.name AS collection_name,
                ct.name_alter AS collection_name_alter,
                p.product_number AS product_number,
                pt.name AS product_name,
                pt.name_alter AS product_name_alter,
                CAST(p.is_verified AS UNSIGNED) AS is_verified,
                f.id AS file_id,
                (
                    SELECT ppt.url
                    FROM product_price_tracking ppt
                    WHERE ppt.product_id = p.id
                    ORDER BY ppt.id DESC
                    LIMIT 1
                ) AS tracker_url
            {CATALOG_FROM_SQL}
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
                "is_verified": row["is_verified"] == 1,
                "collection_name": format_name(
                    row["collection_name"],
                    row["collection_name_alter"]
                ),
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

    # Serve the file inline (not forced attachment). The blueprint is protected
    # so Authorization is required; CORS headers are set globally in app.after_request.
    # Disable conditional responses to avoid accidental 304 Not Modified replies
    # when clients use conditional headers — the frontend expects a response
    # body to create a blob URL. Also set Cache-Control to avoid browser
    # revalidation for protected resources.
    resp = send_file(
        resolved_path,
        download_name=row["original_name"],
        as_attachment=False,
        mimetype=mime_type,
        conditional=False,
    )
    resp.headers['Cache-Control'] = 'no-store'
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
