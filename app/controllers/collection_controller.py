from flask import Blueprint, jsonify, request

import app.auth as auth
from app.schemas.collection_schema import CollectionSchema
from app.services.collection_service import CollectionService
from app.utils.pagination import get_pagination_params, paginated_response

collection_blueprint = Blueprint("collections", __name__)
schema = CollectionSchema()
schema_many = CollectionSchema(many=True)

READ_ROLES = ("collection_read", "admin")
WRITE_ROLES = ("collection_write", "admin")


def _check_role(method):
    method = method.upper()
    if method in ("GET",):
        if not auth.has_any_role(*READ_ROLES):
            return True
    elif method in ("POST", "PATCH", "DELETE"):
        if not auth.has_any_role(*WRITE_ROLES):
            return True
    return False


@collection_blueprint.route("/", methods=["GET"])
def get_all():
    if _check_role("GET"):
        return jsonify({"message": "Forbidden"}), 403
    page, per_page = get_pagination_params()
    sort_by = (request.args.get("sort_by") or "").strip()
    filters = {
        "code": (request.args.get("code") or "").strip(),
        "name": (request.args.get("name") or "").strip(),
        "card_type_id": (request.args.get("card_type_id") or "").strip(),
        "is_manual": (request.args.get("is_manual") or "").strip(),
    }
    filters = {k: v for k, v in filters.items() if v}
    if filters:
        data = CollectionService.get_filtered_paginated(filters, page, per_page, sort_by)
    else:
        search = (request.args.get("q") or "").strip()
        if search:
            data = CollectionService.get_search_paginated(search, page, per_page, sort_by)
        else:
            data = CollectionService.get_paginated(page, per_page, sort_by)
    return jsonify(paginated_response(data, schema_many))


@collection_blueprint.route("/<int:collection_id>", methods=["GET"])
def get_by_id(collection_id):
    if _check_role("GET"):
        return jsonify({"message": "Forbidden"}), 403
    data = CollectionService.get_by_id(collection_id)
    if not data:
        return jsonify({"message": "Not found"}), 404
    return jsonify(schema.dump(data))


@collection_blueprint.route("/", methods=["POST"])
def create():
    if _check_role("POST"):
        return jsonify({"message": "Forbidden"}), 403
    body = request.get_json()
    entity = CollectionService.create(body)
    return jsonify(schema.dump(entity)), 201


@collection_blueprint.route("/<int:collection_id>", methods=["PATCH"])
def update(collection_id):
    if _check_role("PATCH"):
        return jsonify({"message": "Forbidden"}), 403
    body = request.get_json()
    entity = CollectionService.update(collection_id, body)
    if not entity:
        return jsonify({"message": "Not found"}), 404

    return jsonify(schema.dump(entity))


@collection_blueprint.route("/<int:collection_id>", methods=["DELETE"])
def delete(collection_id):
    if _check_role("DELETE"):
        return jsonify({"message": "Forbidden"}), 403
    try:
        deleted = CollectionService.delete(collection_id)
        if not deleted:
            return jsonify({"message": "Not found"}), 404
        return jsonify({"success": True})
    except ValueError as e:
        return jsonify({"message": str(e)}), 409
