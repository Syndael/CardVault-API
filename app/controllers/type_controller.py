from flask import Blueprint, jsonify, request

from app.schemas.type_schema import TypeSchema
from app.services.type_service import TypeService
from app.utils.pagination import get_pagination_params, paginated_response

type_blueprint = Blueprint("types", __name__)
schema = TypeSchema()
schema_many = TypeSchema(many=True)


@type_blueprint.route("/", methods=["GET"])
def get_all():
    page, per_page = get_pagination_params()
    data = TypeService.get_paginated(page, per_page)
    return jsonify(paginated_response(data, schema_many))


@type_blueprint.route("/<int:type_id>", methods=["GET"])
def get_by_id(type_id):
    data = TypeService.get_by_id(type_id)
    if not data:
        return jsonify({"message": "Not found"}), 404
    return jsonify(schema.dump(data))


@type_blueprint.route("/", methods=["POST"])
def create():
    body = request.get_json()
    entity = TypeService.create(body)
    return jsonify(schema.dump(entity)), 201


@type_blueprint.route("/<int:type_id>", methods=["PATCH"])
def update(type_id):
    body = request.get_json()
    entity = TypeService.update(type_id, body)
    if not entity:
        return jsonify({"message": "Not found"}), 404

    return jsonify(schema.dump(entity))


@type_blueprint.route("/<int:type_id>", methods=["DELETE"])
def delete(type_id):
    deleted = TypeService.delete(type_id)
    if not deleted:
        return jsonify({"message": "Not found"}), 404
    return jsonify({"success": True})
