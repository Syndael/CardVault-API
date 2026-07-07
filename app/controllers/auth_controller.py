from flask import Blueprint, request, jsonify, g

import app.auth as auth
from app.schemas.user_schema import UserSchema
from app.services.user_service import UserService

auth_blueprint = Blueprint("auth", __name__)


@auth_blueprint.route("/login", methods=["POST"])  # /api/auth/login
def login():
    body = request.get_json(silent=True) or {}
    identifier = body.get("username") or body.get("email")
    password = body.get("password")

    if not identifier or not password:
        return jsonify({"message": "username/email and password are required"}), 400

    token, session, user = auth.login_user(
        identifier,
        password,
        user_agent=request.headers.get("User-Agent"),
        ip_address=request.remote_addr,
    )

    if not token:
        return jsonify({"message": "Invalid credentials"}), 401

    schema = UserSchema()
    return jsonify({
        "token": token,
        "expires_at": session.expires_at.isoformat(),
        "user": schema.dump(user)
    })


@auth_blueprint.route("/user/<int:user_id>/", methods=["GET"])  # /api/auth/user/<id>
@auth.require_auth
def get_user(user_id):
    user = UserService.get_by_id(user_id)
    if not user:
        return jsonify({"message": "Not found"}), 404
    return jsonify({"email": user.email, "telegram_id": user.telegram_id})


@auth_blueprint.route("/users", methods=["GET"])  # /api/auth/users
@auth.require_role("admin")
def list_users():
    users = UserService.get_all()
    schema = UserSchema(many=True)
    return jsonify(schema.dump(users))


@auth_blueprint.route("/logout", methods=["POST"])  # /api/auth/logout
def logout():
    token = auth.get_token_from_header()
    if not token:
        return jsonify({"message": "Unauthorized"}), 401

    revoked = auth.revoke_token(token)
    if not revoked:
        return jsonify({"message": "Invalid token"}), 401

    return jsonify({"success": True})


@auth_blueprint.route("/me", methods=["GET"])  # /api/auth/me
@auth.require_auth
def me():
    user = g.current_user
    schema = UserSchema()
    return jsonify(schema.dump(user))


@auth_blueprint.route("/me", methods=["PATCH"])  # /api/auth/me
@auth.require_auth
def update_me():
    user = g.current_user
    data = request.get_json(silent=True) or {}

    allowed_fields = {"display_name", "email", "telegram_id"}
    update_data = {k: v for k, v in data.items() if k in allowed_fields}

    if update_data:
        UserService.update(user.id, update_data)

    schema = UserSchema()
    return jsonify(schema.dump(user))
