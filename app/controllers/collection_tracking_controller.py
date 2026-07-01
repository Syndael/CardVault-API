from flask import Blueprint, g, jsonify, request
from sqlalchemy import text

from app.database.session import db
from app.models.collection_model import CollectionModel
from app.models.user_collection_tracking_model import UserCollectionTrackingModel


collection_tracking_blueprint = Blueprint("collection_tracking", __name__)

VALID_TRACKING_MODES = {"standard", "master"}


def _current_user_id():
    user = getattr(g, "current_user", None)
    return user.id if user else None


def _normalize_tracking_mode(value):
    value = (value or "standard").strip().lower()
    return value if value in VALID_TRACKING_MODES else "standard"


def _progress_payload(row):
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
    }


@collection_tracking_blueprint.route("", methods=["GET"], strict_slashes=False)
def list_progress():
    user_id = _current_user_id()
    if not user_id:
        return jsonify({"message": "Unauthorized"}), 401

    rows = db.session.execute(
        text(
            """
            SELECT
                uct.collection_id,
                c.code AS collection_code,
                ct.name AS collection_name,
                uct.tracking_mode,
                COUNT(DISTINCT CASE
                    WHEN p.completion_group = 'standard' THEN p.id
                END) AS standard_total,
                COUNT(DISTINCT CASE
                    WHEN p.completion_group = 'standard' AND i.id IS NOT NULL THEN p.id
                END) AS standard_owned,
                COUNT(DISTINCT CASE
                    WHEN p.completion_group IN ('standard', 'secret') THEN p.id
                END) AS master_total,
                COUNT(DISTINCT CASE
                    WHEN p.completion_group IN ('standard', 'secret') AND i.id IS NOT NULL THEN p.id
                END) AS master_owned
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
        ),
        {"user_id": user_id},
    ).mappings().all()

    items = [_progress_payload(row) for row in rows]
    items.sort(key=lambda item: (item["missing"], -item["percent"], item["collection_code"]))
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
