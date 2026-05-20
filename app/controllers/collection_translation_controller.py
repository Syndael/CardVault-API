from flask import Blueprint, jsonify, request

from app.schemas.collection_translation_schema import (CollectionTranslationSchema)
from app.services.collection_translation_service import (CollectionTranslationService)
from app.utils.pagination import get_pagination_params, paginated_response

collection_translation_blueprint = Blueprint("collection_translations", __name__)
schema = CollectionTranslationSchema()
schema_many = CollectionTranslationSchema(many=True)


@collection_translation_blueprint.route("/", methods=["GET"])
def get_all():
    page, per_page = get_pagination_params()
    data = (CollectionTranslationService.get_paginated(page, per_page))
    return jsonify(paginated_response(data, schema_many))


@collection_translation_blueprint.route("/<int:translation_id>", methods=["GET"])
def get_by_id(translation_id):
    data = (CollectionTranslationService.get_by_id(translation_id))
    if not data:
        return jsonify({"message": "Not found"}), 404

    return jsonify(schema.dump(data))


@collection_translation_blueprint.route("/", methods=["POST"])
def create():
    body = request.get_json()
    entity = (CollectionTranslationService.create(body))
    return jsonify(schema.dump(entity)), 201


@collection_translation_blueprint.route("/<int:translation_id>", methods=["PATCH"])
def update(translation_id):
    body = request.get_json()
    entity = (CollectionTranslationService.update(translation_id, body))
    if not entity:
        return jsonify({"message": "Not found"}), 404

    return jsonify(schema.dump(entity))


@collection_translation_blueprint.route("/<int:translation_id>", methods=["DELETE"])
def delete(translation_id):
    deleted = (CollectionTranslationService.delete(translation_id))
    if not deleted:
        return jsonify({"message": "Not found"}), 404

    return jsonify({"success": True})
