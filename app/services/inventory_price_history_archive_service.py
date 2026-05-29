from app.repositories.inventory_price_history_archive_repository import (
    InventoryPriceHistoryArchiveRepository
)
from app.services.crud_service import CrudService


class InventoryPriceHistoryArchiveService(CrudService):
    repository = InventoryPriceHistoryArchiveRepository
