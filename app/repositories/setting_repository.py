from app.models.setting_model import SettingModel
from app.repositories.crud_repository import CrudRepository


class SettingRepository(CrudRepository):
    model = SettingModel
    order_by = (SettingModel.setting_key,)
    create_fields = (
        "setting_key",
        "setting_value"
    )
    update_fields = create_fields
