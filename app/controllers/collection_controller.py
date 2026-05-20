from flask import Blueprint, jsonify, request

from app.schemas.collection_schema import CollectionSchema
from app.services.collection_service import CollectionService
from app.utils.pagination import get_pagination_params, paginated_response

collection_blueprint = Blueprint("collections", __name__)
schema = CollectionSchema()
schema_many = CollectionSchema(many=True)


@collection_blueprint.route("/", methods=["GET"])
def get_all():
    page, per_page = get_pagination_params()
    search = (request.args.get("q") or "").strip()
    if search:
        data = CollectionService.get_search_paginated(search, page, per_page)
    else:
        data = CollectionService.get_paginated(page, per_page)
    return jsonify(paginated_response(data, schema_many))


@collection_blueprint.route("/<int:collection_id>", methods=["GET"])
def get_by_id(collection_id):
    data = CollectionService.get_by_id(collection_id)
    if not data:
        return jsonify({"message": "Not found"}), 404
    return jsonify(schema.dump(data))


@collection_blueprint.route("/", methods=["POST"])
def create():
    body = request.get_json()
    entity = CollectionService.create(body)
    return jsonify(schema.dump(entity)), 201


@collection_blueprint.route("/<int:collection_id>", methods=["PATCH"])
def update(collection_id):
    body = request.get_json()
    entity = CollectionService.update(collection_id, body)
    if not entity:
        return jsonify({"message": "Not found"}), 404

    return jsonify(schema.dump(entity))


@collection_blueprint.route("/<int:collection_id>", methods=["DELETE"])
def delete(collection_id):
    deleted = CollectionService.delete(collection_id)
    if not deleted:
        return jsonify({"message": "Not found"}), 404
    return jsonify({"success": True})
