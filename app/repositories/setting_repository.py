from app.database.session import db
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

    @classmethod
    def get_by_key(cls, key):
        return cls.model.query.filter(cls.model.setting_key == key).first()

    @classmethod
    def upsert_by_key(cls, key, value):
        entity = cls.get_by_key(key)
        if entity:
            entity.setting_value = value
        else:
            entity = cls.model(setting_key=key, setting_value=value)
            db.session.add(entity)
        db.session.commit()
        return entity
