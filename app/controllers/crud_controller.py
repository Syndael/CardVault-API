from flask import Blueprint, jsonify, request

import app.auth as auth
from app.utils.pagination import get_pagination_params, paginated_response


def _roles_guard(read_roles, write_roles, method):
    method = method.upper()
    roles = None
    if method in ("GET",) and read_roles:
        roles = read_roles
    elif method in ("POST", "PATCH", "DELETE") and write_roles:
        roles = write_roles
    if roles and not auth.has_any_role(*roles):
        return True  # forbidden
    return False  # allowed


def create_crud_blueprint(name, service, schema_class, id_name,
                          read_roles=None, write_roles=None,
                          list_schema_class=None):
    blueprint = Blueprint(name, __name__)
    schema = schema_class()
    schema_many = schema_class(many=True)
    list_schema = list_schema_class(many=True) if list_schema_class else schema_many

    def _check_role(method):
        return _roles_guard(read_roles, write_roles, method)

    @blueprint.route("/", methods=["GET"], strict_slashes=False)
    def get_all():
        if _check_role("GET"):
            return jsonify({"message": "Forbidden"}), 403
        page, per_page = get_pagination_params()
        data = service.get_paginated(page, per_page)
        return jsonify(paginated_response(data, list_schema))

    @blueprint.route(f"/<int:{id_name}>", methods=["GET"], strict_slashes=False)
    def get_by_id(**kwargs):
        if _check_role("GET"):
            return jsonify({"message": "Forbidden"}), 403
        data = service.get_by_id(kwargs[id_name])
        if not data:
            return jsonify({"message": "Not found"}), 404

        return jsonify(schema.dump(data))

    @blueprint.route("/", methods=["POST"], strict_slashes=False)
    def create():
        if _check_role("POST"):
            return jsonify({"message": "Forbidden"}), 403
        body = request.get_json()
        entity = service.create(body)
        return jsonify(schema.dump(entity)), 201

    @blueprint.route(f"/<int:{id_name}>", methods=["PATCH"], strict_slashes=False)
    def update(**kwargs):
        if _check_role("PATCH"):
            return jsonify({"message": "Forbidden"}), 403
        body = request.get_json()
        entity = service.update(kwargs[id_name], body)
        if not entity:
            return jsonify({"message": "Not found"}), 404

        return jsonify(schema.dump(entity))

    @blueprint.route(f"/<int:{id_name}>", methods=["DELETE"], strict_slashes=False)
    def delete(**kwargs):
        if _check_role("DELETE"):
            return jsonify({"message": "Forbidden"}), 403
        deleted = service.delete(kwargs[id_name])
        if not deleted:
            return jsonify({"message": "Not found"}), 404

        return jsonify({"success": True})

    return blueprint
