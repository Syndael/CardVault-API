from flask import Blueprint, jsonify, request

from app.controllers.crud_controller import _roles_guard
from app.services import ai_service

ai_blueprint = Blueprint("ai", __name__)


@ai_blueprint.route("/publications/<int:publication_id>/generate-text", methods=["POST"], strict_slashes=False)
def generate_text(publication_id):
    if _roles_guard(None, ["inventory_manage", "admin"], "POST"):
        return jsonify({"message": "Forbidden"}), 403

    body = request.get_json(silent=True) or {}
    user_text = (body.get("user_text") or "").strip()
    body_inv_ids = body.get("inventory_ids") or []
    body_pur_ids = body.get("purchase_ids") or []

    inventory_ids = [int(x) for x in body_inv_ids]
    purchase_ids = [int(x) for x in body_pur_ids]

    if not inventory_ids and not purchase_ids:
        from app.services.publication_schedule_service import PublicationScheduleService
        pub = PublicationScheduleService.get_by_id(publication_id)
        if pub:
            inventory_ids = [inv.id for inv in (pub.inventories or [])]
            purchase_ids = [pur.id for pur in (pub.purchases or [])]

    text = ai_service.generate_caption_for_publication(inventory_ids, purchase_ids, user_text)
    return jsonify({"text": text})


@ai_blueprint.route("/publications/generate-text", methods=["POST"], strict_slashes=False)
def generate_text_no_publication():
    if _roles_guard(None, ["inventory_manage", "admin"], "POST"):
        return jsonify({"message": "Forbidden"}), 403

    body = request.get_json(silent=True) or {}
    user_text = (body.get("user_text") or "").strip()
    inventory_ids = body.get("inventory_ids") or []
    purchase_ids = body.get("purchase_ids") or []

    text = ai_service.generate_caption_for_publication(
        [int(x) for x in inventory_ids],
        [int(x) for x in purchase_ids],
        user_text
    )
    return jsonify({"text": text})
