from flask import jsonify, request

from app.controllers.crud_controller import _roles_guard, create_crud_blueprint
from app.schemas.inventory_schema import InventoryListSchema, InventorySchema
from app.services.inventory_service import InventoryService


inventory_blueprint = create_crud_blueprint(
    "inventory",
    InventoryService,
    InventorySchema,
    "inventory_id",
    read_roles=["inventory_manage", "admin"],
    write_roles=["inventory_manage", "admin"],
    list_schema_class=InventoryListSchema
)


@inventory_blueprint.route("/bulk", methods=["POST"], strict_slashes=False)
def bulk_create():
    if _roles_guard(None, ["inventory_manage", "admin"], "POST"):
        return jsonify({"message": "Forbidden"}), 403
    body = request.get_json() or {}
    result = InventoryService.bulk_create(body)
    if not result.get("success"):
        return jsonify(result), 400
    return jsonify(result), 200


@inventory_blueprint.route("/batch-tags", methods=["POST"], strict_slashes=False)
def batch_tags():
    if _roles_guard(None, ["inventory_manage", "admin"], "POST"):
        return jsonify({"message": "Forbidden"}), 403
    body = request.get_json() or {}
    inventory_ids = body.get("inventory_ids") or []
    tag_ids = body.get("tag_ids") or []
    action = body.get("action", "add")
    if action not in ("add", "remove", "set"):
        return jsonify({"success": False, "error": "action must be add, remove, or set"}), 400
    if not isinstance(inventory_ids, list) or not isinstance(tag_ids, list):
        return jsonify({"success": False, "error": "inventory_ids and tag_ids must be arrays"}), 400
    if not inventory_ids:
        return jsonify({"success": False, "error": "inventory_ids is required"}), 400
    result = InventoryService.batch_tags(inventory_ids, tag_ids, action)
    if not result.get("success"):
        return jsonify(result), 400
    return jsonify(result), 200
