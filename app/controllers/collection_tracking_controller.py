from flask import Blueprint, g, jsonify, request
from sqlalchemy import text
import logging

from app.database.session import db
from app.models.collection_model import CollectionModel
from app.models.type_model import TypeModel
from app.models.user_collection_tracking_model import UserCollectionTrackingModel


logger = logging.getLogger(__name__)
collection_tracking_blueprint = Blueprint("collection_tracking", __name__)

VALID_TRACKING_MODES = {"standard", "master"}


def _current_user_id():
    user = getattr(g, "current_user", None)
    return user.id if user else None


def _normalize_tracking_mode(value):
    value = (value or "standard").strip().lower()
    return value if value in VALID_TRACKING_MODES else "standard"


def _build_progress_sql(group_types, mode):
    group_cols = []
    owned_cols = []
    master_sets = []
    standard_sets = []

    for gt in group_types:
        col = gt["name"].lower()
        param = f"gid_{col}"
        group_cols.append(
            f"COUNT(DISTINCT CASE WHEN p.completion_group_id = :{param} THEN p.id END) AS {col}_total"
        )
        owned_cols.append(
            f"COUNT(DISTINCT CASE WHEN p.completion_group_id = :{param} AND i.id IS NOT NULL THEN p.id END) AS {col}_owned"
        )

        if col == "standard":
            standard_sets.append(f"p.completion_group_id = :{param}")
        if col in ("standard", "reverse", "holo", "secret", "alternativa"):
            master_sets.append(f"p.completion_group_id = :{param}")

    standard_expr = " OR ".join(standard_sets) if standard_sets else "1=0"
    master_expr = " OR ".join(master_sets) if master_sets else "1=0"

    extra_cols = (
        f"COUNT(DISTINCT CASE WHEN ({standard_expr}) THEN p.id END) AS standard_total,\n"
        f"COUNT(DISTINCT CASE WHEN ({standard_expr}) AND i.id IS NOT NULL THEN p.id END) AS standard_owned,\n"
        f"COUNT(DISTINCT CASE WHEN ({master_expr}) THEN p.id END) AS master_total,\n"
        f"COUNT(DISTINCT CASE WHEN ({master_expr}) AND i.id IS NOT NULL THEN p.id END) AS master_owned"
    )

    return extra_cols, group_cols + owned_cols


def _progress_payload(row, group_types):
    mode = _normalize_tracking_mode(row["tracking_mode"])
    standard_total = int(row["standard_total"] or 0)
    standard_owned = int(row["standard_owned"] or 0)
    master_total = int(row["master_total"] or 0)
    master_owned = int(row["master_owned"] or 0)

    if mode == "master":
        target_total = master_total
        owned = master_owned
    else:
        target_total = standard_total
        owned = standard_owned

    missing = max(target_total - owned, 0)
    percent = round((owned / target_total) * 100, 2) if target_total else 0

    groups = {}
    for gt in group_types:
        col = gt["name"].lower()
        groups[col] = {
            "name": gt["name"],
            "short_name": gt.get("short_name"),
            "total": int(row.get(f"{col}_total") or 0),
            "owned": int(row.get(f"{col}_owned") or 0),
        }

    return {
        "collection_id": row["collection_id"],
        "collection_code": row["collection_code"],
        "collection_name": row["collection_name"],
        "tracking_mode": mode,
        "target_total": target_total,
        "owned": owned,
        "missing": missing,
        "percent": percent,
        "standard_total": standard_total,
        "standard_owned": standard_owned,
        "master_total": master_total,
        "master_owned": master_owned,
        "groups": groups,
    }


@collection_tracking_blueprint.route("", methods=["GET"], strict_slashes=False)
def list_progress():
    user_id = _current_user_id()
    if not user_id:
        return jsonify({"message": "Unauthorized"}), 401

    try:
        group_types = db.session.execute(
            text("SELECT id, name, short_name FROM types WHERE type = 'completion_group' ORDER BY id")
        ).mappings().all()

        if not group_types:
            logger.info("No completion_group types found, using fallback")
            return _list_progress_fallback(user_id)

        has_col = db.session.execute(
            text("SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='products' AND COLUMN_NAME='completion_group_id'")
        ).scalar()

        if not has_col:
            logger.info("completion_group_id column not found, using fallback")
            return _list_progress_fallback(user_id)

        extra_cols, per_group_cols = _build_progress_sql(group_types, "standard")

        all_cols = ",\n                ".join(per_group_cols)
        sql = f"""
            SELECT
                uct.collection_id,
                c.code AS collection_code,
                ct.name AS collection_name,
                uct.tracking_mode,
                {all_cols},
                {extra_cols}
            FROM user_collection_tracking uct
            INNER JOIN collections c ON c.id = uct.collection_id
            LEFT JOIN products p ON p.collection_id = c.id
            LEFT JOIN inventory i
                ON i.product_id = p.id
               AND i.user_id = uct.user_id
            LEFT JOIN (
                SELECT collection_id, name
                FROM collection_translations
                WHERE id IN (
                    SELECT MIN(id)
                    FROM collection_translations
                    GROUP BY collection_id
                )
            ) ct ON ct.collection_id = c.id
            WHERE uct.user_id = :user_id
            GROUP BY uct.collection_id, c.code, ct.name, uct.tracking_mode
        """

        params = {"user_id": user_id}
        for gt in group_types:
            params[f"gid_{gt['name'].lower()}"] = gt["id"]

        rows = db.session.execute(text(sql), params).mappings().all()
        items = [_progress_payload(row, group_types) for row in rows]
        items.sort(key=lambda item: (item["missing"], -item["percent"], item["collection_code"]))
        return jsonify({"items": items})

    except Exception as e:
        logger.exception("Error in collection tracking list_progress")
        return jsonify({"items": [], "error": str(e)}), 500


def _list_progress_fallback(user_id):
    try:
        rows = db.session.execute(
            text("""
                SELECT
                    uct.collection_id,
                    c.code AS collection_code,
                    ct.name AS collection_name,
                    uct.tracking_mode,
                    COUNT(DISTINCT p.id) AS standard_total,
                    COUNT(DISTINCT CASE WHEN i.id IS NOT NULL THEN p.id END) AS standard_owned,
                    COUNT(DISTINCT p.id) AS master_total,
                    COUNT(DISTINCT CASE WHEN i.id IS NOT NULL THEN p.id END) AS master_owned
                FROM user_collection_tracking uct
                INNER JOIN collections c ON c.id = uct.collection_id
                LEFT JOIN products p ON p.collection_id = c.id
                LEFT JOIN inventory i
                    ON i.product_id = p.id
                   AND i.user_id = uct.user_id
                LEFT JOIN (
                    SELECT collection_id, name
                    FROM collection_translations
                    WHERE id IN (
                        SELECT MIN(id)
                        FROM collection_translations
                        GROUP BY collection_id
                    )
                ) ct ON ct.collection_id = c.id
                WHERE uct.user_id = :user_id
                GROUP BY uct.collection_id, c.code, ct.name, uct.tracking_mode
                ORDER BY uct.tracking_mode, c.code
            """),
            {"user_id": user_id},
        ).mappings().all()
    except Exception as e:
        logger.exception("Fallback query failed")
        return jsonify({"items": [], "error": str(e)}), 500

    items = []
    for row in rows:
        mode = _normalize_tracking_mode(row["tracking_mode"])
        total = int(row["master_total"] or 0)
        owned = int(row["master_owned"] or 0)
        missing = max(total - owned, 0)
        percent = round((owned / total) * 100, 2) if total else 0
        items.append({
            "collection_id": row["collection_id"],
            "collection_code": row["collection_code"],
            "collection_name": row["collection_name"],
            "tracking_mode": mode,
            "target_total": total,
            "owned": owned,
            "missing": missing,
            "percent": percent,
            "standard_total": total,
            "standard_owned": owned,
            "master_total": total,
            "master_owned": owned,
            "groups": {},
        })

    return jsonify({"items": items})


@collection_tracking_blueprint.route("", methods=["POST"], strict_slashes=False)
def track_collection():
    user_id = _current_user_id()
    if not user_id:
        return jsonify({"message": "Unauthorized"}), 401

    data = request.get_json(silent=True) or {}
    collection_id = data.get("collection_id")
    if not collection_id:
        return jsonify({"message": "collection_id is required"}), 400

    collection = CollectionModel.query.get(collection_id)
    if not collection:
        return jsonify({"message": "Collection not found"}), 404

    tracking_mode = _normalize_tracking_mode(data.get("tracking_mode"))
    entity = UserCollectionTrackingModel.query.get((user_id, collection.id))
    if entity:
        entity.tracking_mode = tracking_mode
    else:
        entity = UserCollectionTrackingModel(
            user_id=user_id,
            collection_id=collection.id,
            tracking_mode=tracking_mode,
        )
        db.session.add(entity)

    db.session.commit()
    return jsonify({
        "user_id": user_id,
        "collection_id": collection.id,
        "tracking_mode": tracking_mode,
    }), 201


@collection_tracking_blueprint.route("/<int:collection_id>", methods=["PATCH"], strict_slashes=False)
def update_tracking(collection_id):
    user_id = _current_user_id()
    if not user_id:
        return jsonify({"message": "Unauthorized"}), 401

    entity = UserCollectionTrackingModel.query.get((user_id, collection_id))
    if not entity:
        return jsonify({"message": "Not found"}), 404

    data = request.get_json(silent=True) or {}
    entity.tracking_mode = _normalize_tracking_mode(data.get("tracking_mode"))
    db.session.commit()
    return jsonify({
        "user_id": user_id,
        "collection_id": collection_id,
        "tracking_mode": entity.tracking_mode,
    })


@collection_tracking_blueprint.route("/<int:collection_id>", methods=["DELETE"], strict_slashes=False)
def untrack_collection(collection_id):
    user_id = _current_user_id()
    if not user_id:
        return jsonify({"message": "Unauthorized"}), 401

    entity = UserCollectionTrackingModel.query.get((user_id, collection_id))
    if not entity:
        return jsonify({"message": "Not found"}), 404

    db.session.delete(entity)
    db.session.commit()
    return jsonify({"success": True})
