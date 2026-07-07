from flask import Blueprint, jsonify, request

import app.auth as auth
from app.services.notification_service import send_email, send_telegram

notification_blueprint = Blueprint("notifications", __name__)


@notification_blueprint.route("/email", methods=["POST"], strict_slashes=False)
@auth.require_role("admin")
def notify_email():
    body = request.get_json() or {}
    to_addr = body.get("to")
    subject = body.get("subject", "CardVault Notification")
    message = body.get("message", "")
    if not to_addr or not message:
        return jsonify({"message": "to and message are required"}), 400
    ok = send_email(to_addr, subject, message)
    return jsonify({"sent": ok})


@notification_blueprint.route("/telegram", methods=["POST"], strict_slashes=False)
@auth.require_role("admin")
def notify_telegram():
    body = request.get_json() or {}
    message = body.get("message", "")
    if not message:
        return jsonify({"message": "message is required"}), 400
    ok = send_telegram(message)
    return jsonify({"sent": ok})