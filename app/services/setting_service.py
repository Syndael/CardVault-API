from app.repositories.setting_repository import SettingRepository
from app.services.crud_service import CrudService


class SettingService(CrudService):
    repository = SettingRepository
