from flask import jsonify, request

from app.controllers.crud_controller import create_crud_blueprint
from app.schemas.setting_schema import SettingSchema
from app.services.setting_service import SettingService


setting_blueprint = create_crud_blueprint(
    "settings",
    SettingService,
    SettingSchema,
    "setting_id"
)


@setting_blueprint.route("/by-key/<path:key>/", methods=["GET"], strict_slashes=False)
def get_setting_by_key(key):
    entity = SettingService.get_by_key(key)
    if not entity:
        return jsonify({"message": "Not found"}), 404
    return jsonify(SettingSchema().dump(entity))


@setting_blueprint.route("/by-key/<path:key>/", methods=["PATCH"], strict_slashes=False)
def upsert_setting_by_key(key):
    body = request.get_json() or {}
    value = body.get("setting_value")
    entity = SettingService.upsert_by_key(key, value)
    return jsonify(SettingSchema().dump(entity))
