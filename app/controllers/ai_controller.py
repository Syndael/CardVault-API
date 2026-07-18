from flask import Blueprint, jsonify, request

from app.controllers.crud_controller import _roles_guard
from app.services import ai_service

ai_blueprint = Blueprint("ai", __name__)


@ai_blueprint.route("/publications/<int:publication_id>/generate-text", methods=["POST"], strict_slashes=False)
def generate_text(publication_id):
    if _roles_guard(None, ["inventory_manage", "admin"], "POST"):
        return jsonify({"message": "Forbidden"}), 403

    from app.services.publication_schedule_service import PublicationScheduleService
    pub = PublicationScheduleService.get_by_id(publication_id)
    if not pub:
        return jsonify({"message": "Publication not found"}), 404

    body = request.get_json(silent=True) or {}
    user_text = (body.get("user_text") or "").strip()

    text = ai_service.generate_caption(pub.inventory_id, user_text)
    return jsonify({"text": text})
