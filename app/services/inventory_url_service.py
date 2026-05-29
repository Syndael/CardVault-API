from app.repositories.inventory_url_repository import InventoryUrlRepository
from app.services.crud_service import CrudService


class InventoryUrlService(CrudService):
    repository = InventoryUrlRepository
