from app.controllers.crud_controller import create_crud_blueprint
from app.schemas.setting_schema import SettingSchema
from app.services.setting_service import SettingService


setting_blueprint = create_crud_blueprint(
    "settings",
    SettingService,
    SettingSchema,
    "setting_id"
)
