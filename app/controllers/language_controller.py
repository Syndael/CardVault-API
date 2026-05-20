from flask import Blueprint, jsonify, request

from app.schemas.language_schema import LanguageSchema
from app.services.language_service import LanguageService
from app.utils.pagination import get_pagination_params, paginated_response

language_blueprint = Blueprint("languages", __name__)
schema = LanguageSchema()
schema_many = LanguageSchema(many=True)


@language_blueprint.route("/", methods=["GET"])
def get_all():
    page, per_page = get_pagination_params()
    data = LanguageService.get_paginated(page, per_page)
    return jsonify(paginated_response(data, schema_many))


@language_blueprint.route("/<int:language_id>", methods=["GET"])
def get_by_id(language_id):
    data = LanguageService.get_by_id(language_id)
    if not data:
        return jsonify({"message": "Not found"}), 404

    return jsonify(schema.dump(data))


@language_blueprint.route("/", methods=["POST"])
def create():
    body = request.get_json()
    entity = LanguageService.create(body)
    return jsonify(schema.dump(entity)), 201


@language_blueprint.route("/<int:language_id>", methods=["PATCH"])
def update(language_id):
    body = request.get_json()
    entity = LanguageService.update(language_id, body)
    if not entity:
        return jsonify({"message": "Not found"}), 404

    return jsonify(schema.dump(entity))


@language_blueprint.route("/<int:language_id>", methods=["DELETE"])
def delete(language_id):
    deleted = LanguageService.delete(language_id)
    if not deleted:
        return jsonify({"message": "Not found"}), 404

    return jsonify({"success": True})
