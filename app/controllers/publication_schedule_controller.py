from datetime import datetime

from flask import jsonify, request

import app.auth as auth
from app.controllers.crud_controller import _roles_guard, create_crud_blueprint
from app.schemas.publication_schedule_schema import PublicationScheduleSchema
from app.services.publication_schedule_service import PublicationScheduleService

publication_schedule_blueprint = create_crud_blueprint(
    "publication_schedule",
    PublicationScheduleService,
    PublicationScheduleSchema,
    "publication_id",
    read_roles=["inventory_manage", "admin"],
    write_roles=["inventory_manage", "admin"],
)

schema = PublicationScheduleSchema()


@publication_schedule_blueprint.route("/pending-publish", methods=["GET"], strict_slashes=False)
def get_pending_publish():
    if _roles_guard(["inventory_manage", "admin"], None, "GET"):
        return jsonify({"message": "Forbidden"}), 403
    pending = PublicationScheduleService.get_pending_publish()
    return jsonify(schema.dump(pending, many=True))


@publication_schedule_blueprint.route("/by-status/<status_name>", methods=["GET"], strict_slashes=False)
def get_by_status(status_name):
    if _roles_guard(["inventory_manage", "admin"], None, "GET"):
        return jsonify({"message": "Forbidden"}), 403
    items = PublicationScheduleService.get_by_status(status_name)
    return jsonify(schema.dump(items, many=True))


@publication_schedule_blueprint.route("/<int:publication_id>/approve", methods=["POST"], strict_slashes=False)
def approve_publication(publication_id):
    if _roles_guard(None, ["inventory_manage", "admin"], "POST"):
        return jsonify({"message": "Forbidden"}), 403
    entity = PublicationScheduleService.get_by_id(publication_id)
    if not entity:
        return jsonify({"message": "Not found"}), 404
    if entity.status != "pending_review":
        return jsonify({"message": f"Cannot approve publication with status '{entity.status}'"}), 400
    body = request.get_json() or {}
    scheduled_str = body.get("scheduled_at")
    if not scheduled_str:
        return jsonify({"message": "scheduled_at is required"}), 400
    try:
        entity.scheduled_at = datetime.fromisoformat(scheduled_str)
    except ValueError:
        return jsonify({"message": "Invalid scheduled_at format"}), 400
    entity.status = "pending_publish"
    from app.database.session import db
    db.session.commit()
    return jsonify(schema.dump(entity))


@publication_schedule_blueprint.route("/<int:publication_id>/cancel", methods=["POST"], strict_slashes=False)
def cancel_publication(publication_id):
    if _roles_guard(None, ["inventory_manage", "admin"], "POST"):
        return jsonify({"message": "Forbidden"}), 403
    entity = PublicationScheduleService.get_by_id(publication_id)
    if not entity:
        return jsonify({"message": "Not found"}), 404
    if entity.status not in ("pending_review", "pending_publish"):
        return jsonify({"message": f"Cannot cancel publication with status '{entity.status}'"}), 400
    entity.status = "cancelled"
    from app.database.session import db
    db.session.commit()
    return jsonify(schema.dump(entity))


@publication_schedule_blueprint.route("/create-from-inventory", methods=["POST"], strict_slashes=False)
def create_from_inventory():
    if _roles_guard(None, ["inventory_manage", "admin"], "POST"):
        return jsonify({"message": "Forbidden"}), 403
    body = request.get_json() or {}
    inv_id = body.get("inventory_id")
    if not inv_id:
        return jsonify({"message": "inventory_id is required"}), 400

    from app.services.inventory_service import InventoryService
    inv = InventoryService.get_by_id(inv_id)
    if not inv:
        return jsonify({"message": "Inventory not found"}), 404

    inv_dict = {
        "product": {"name": getattr(getattr(inv, "product", None), "name", None),
                     "product_number": getattr(getattr(inv, "product", None), "product_number", None)},
        "collection": {"code": getattr(getattr(inv, "collection", None), "code", None),
                        "name": getattr(getattr(inv, "collection", None), "name", None),
                        "card_type": {"name": getattr(getattr(getattr(inv, "collection", None), "card_type", None), "name", None)}},
        "language": {"name": getattr(getattr(inv, "language", None), "name", None)},
    }

    caption = PublicationScheduleService.generate_caption(inv_dict)
    entity = PublicationScheduleService.repository.create({
        "inventory_id": inv_id,
        "status": "pending_review",
        "caption": caption,
    })
    return jsonify(schema.dump(entity)), 201