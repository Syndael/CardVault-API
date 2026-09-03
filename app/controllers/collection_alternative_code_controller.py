from flask import Blueprint, jsonify, request

import app.auth as auth
from app.schemas.collection_alternative_code_schema import CollectionAlternativeCodeSchema
from app.services.collection_alternative_code_service import CollectionAlternativeCodeService
from app.utils.pagination import get_pagination_params, paginated_response

collection_alternative_code_blueprint = Blueprint("collection_alternative_codes", __name__)
schema = CollectionAlternativeCodeSchema()
schema_many = CollectionAlternativeCodeSchema(many=True)

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


@collection_alternative_code_blueprint.route("/", methods=["GET"], strict_slashes=False)
def get_all():
    if _check_role("GET"):
        return jsonify({"message": "Forbidden"}), 403
    page, per_page = get_pagination_params()
    data = CollectionAlternativeCodeService.get_paginated(page, per_page)
    return jsonify(paginated_response(data, schema_many))


@collection_alternative_code_blueprint.route("/<int:alternative_code_id>", methods=["GET"], strict_slashes=False)
def get_by_id(alternative_code_id):
    if _check_role("GET"):
        return jsonify({"message": "Forbidden"}), 403
    data = CollectionAlternativeCodeService.get_by_id(alternative_code_id)
    if not data:
        return jsonify({"message": "Not found"}), 404

    return jsonify(schema.dump(data))


@collection_alternative_code_blueprint.route("/", methods=["POST"], strict_slashes=False)
def create():
    if _check_role("POST"):
        return jsonify({"message": "Forbidden"}), 403
    body = request.get_json()
    entity = CollectionAlternativeCodeService.create(body)
    return jsonify(schema.dump(entity)), 201


@collection_alternative_code_blueprint.route("/<int:alternative_code_id>", methods=["DELETE"], strict_slashes=False)
def delete(alternative_code_id):
    if _check_role("DELETE"):
        return jsonify({"message": "Forbidden"}), 403
    deleted = CollectionAlternativeCodeService.delete(alternative_code_id)
    if not deleted:
        return jsonify({"message": "Not found"}), 404

    return jsonify({"success": True})
