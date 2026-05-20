from flask import Blueprint, jsonify, request

from app.utils.pagination import get_pagination_params, paginated_response


def create_crud_blueprint(name, service, schema_class, id_name):
    blueprint = Blueprint(name, __name__)
    schema = schema_class()
    schema_many = schema_class(many=True)

    @blueprint.route("/", methods=["GET"], strict_slashes=False)
    def get_all():
        page, per_page = get_pagination_params()
        data = service.get_paginated(page, per_page)
        return jsonify(paginated_response(data, schema_many))

    @blueprint.route(f"/<int:{id_name}>", methods=["GET"], strict_slashes=False)
    def get_by_id(**kwargs):
        data = service.get_by_id(kwargs[id_name])
        if not data:
            return jsonify({"message": "Not found"}), 404

        return jsonify(schema.dump(data))

    @blueprint.route("/", methods=["POST"], strict_slashes=False)
    def create():
        body = request.get_json()
        entity = service.create(body)
        return jsonify(schema.dump(entity)), 201

    @blueprint.route(f"/<int:{id_name}>", methods=["PATCH"], strict_slashes=False)
    def update(**kwargs):
        body = request.get_json()
        entity = service.update(kwargs[id_name], body)
        if not entity:
            return jsonify({"message": "Not found"}), 404

        return jsonify(schema.dump(entity))

    @blueprint.route(f"/<int:{id_name}>", methods=["DELETE"], strict_slashes=False)
    def delete(**kwargs):
        deleted = service.delete(kwargs[id_name])
        if not deleted:
            return jsonify({"message": "Not found"}), 404

        return jsonify({"success": True})

    return blueprint
