from app.repositories.inventory_price_history_repository import (
    InventoryPriceHistoryRepository
)
from app.services.crud_service import CrudService


class InventoryPriceHistoryService(CrudService):
    repository = InventoryPriceHistoryRepository
