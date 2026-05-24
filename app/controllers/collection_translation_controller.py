from flask import Blueprint, jsonify, request

import app.auth as auth
from app.schemas.collection_translation_schema import (CollectionTranslationSchema)
from app.services.collection_translation_service import (CollectionTranslationService)
from app.utils.pagination import get_pagination_params, paginated_response

collection_translation_blueprint = Blueprint("collection_translations", __name__)
schema = CollectionTranslationSchema()
schema_many = CollectionTranslationSchema(many=True)

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


@collection_translation_blueprint.route("/", methods=["GET"], strict_slashes=False)
def get_all():
    if _check_role("GET"):
        return jsonify({"message": "Forbidden"}), 403
    page, per_page = get_pagination_params()
    data = (CollectionTranslationService.get_paginated(page, per_page))
    return jsonify(paginated_response(data, schema_many))


@collection_translation_blueprint.route("/<int:translation_id>", methods=["GET"], strict_slashes=False)
def get_by_id(translation_id):
    if _check_role("GET"):
        return jsonify({"message": "Forbidden"}), 403
    data = (CollectionTranslationService.get_by_id(translation_id))
    if not data:
        return jsonify({"message": "Not found"}), 404

    return jsonify(schema.dump(data))


@collection_translation_blueprint.route("/", methods=["POST"], strict_slashes=False)
def create():
    if _check_role("POST"):
        return jsonify({"message": "Forbidden"}), 403
    body = request.get_json()
    entity = (CollectionTranslationService.create(body))
    return jsonify(schema.dump(entity)), 201


@collection_translation_blueprint.route("/<int:translation_id>", methods=["PATCH"], strict_slashes=False)
def update(translation_id):
    if _check_role("PATCH"):
        return jsonify({"message": "Forbidden"}), 403
    body = request.get_json()
    entity = (CollectionTranslationService.update(translation_id, body))
    if not entity:
        return jsonify({"message": "Not found"}), 404

    return jsonify(schema.dump(entity))


@collection_translation_blueprint.route("/<int:translation_id>", methods=["DELETE"], strict_slashes=False)
def delete(translation_id):
    if _check_role("DELETE"):
        return jsonify({"message": "Forbidden"}), 403
    deleted = (CollectionTranslationService.delete(translation_id))
    if not deleted:
        return jsonify({"message": "Not found"}), 404

    return jsonify({"success": True})
