from flask import Blueprint, jsonify, request

from app.schemas.inventory_tag_schema import InventoryTagSchema
from app.services.inventory_tag_service import InventoryTagService

inventory_tag_blueprint = Blueprint("inventory_tags", __name__)

schema      = InventoryTagSchema()
schema_many = InventoryTagSchema(many=True)


@inventory_tag_blueprint.route(
    "/<int:inventory_id>/tags",
    methods=["GET"],
    strict_slashes=False
)
def get_tags(inventory_id):
    tags = InventoryTagService.get_by_inventory(inventory_id)
    return jsonify(schema_many.dump(tags))


@inventory_tag_blueprint.route(
    "/<int:inventory_id>/tags",
    methods=["POST"],
    strict_slashes=False
)
def add_tag(inventory_id):
    body   = request.get_json() or {}
    tag_id = body.get("tag_id")
    if not tag_id:
        return jsonify({"message": "tag_id is required"}), 400

    entry, error = InventoryTagService.add(inventory_id, tag_id)
    if error == "inventory_not_found":
        return jsonify({"message": "Inventory not found"}), 404
    if error == "tag_not_found":
        return jsonify({"message": "Tag not found"}), 404
    if error == "already_exists":
        return jsonify(schema.dump(entry)), 200

    return jsonify(schema.dump(entry)), 201


@inventory_tag_blueprint.route(
    "/<int:inventory_id>/tags/<int:tag_id>",
    methods=["DELETE"],
    strict_slashes=False
)
def remove_tag(inventory_id, tag_id):
    deleted = InventoryTagService.remove(inventory_id, tag_id)
    if not deleted:
        return jsonify({"message": "Not found"}), 404
    return jsonify({"success": True})
