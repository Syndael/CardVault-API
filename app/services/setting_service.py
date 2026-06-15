from app.repositories.setting_repository import SettingRepository
from app.services.crud_service import CrudService


class SettingService(CrudService):
    repository = SettingRepository

    @classmethod
    def get_by_key(cls, key):
        return cls.repository.get_by_key(key)

    @classmethod
    def upsert_by_key(cls, key, value):
        return cls.repository.upsert_by_key(key, value)
