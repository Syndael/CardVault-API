from app.models.inventory_price_history_model import (
    InventoryPriceHistoryModel
)
from app.repositories.crud_repository import CrudRepository


class InventoryPriceHistoryRepository(CrudRepository):
    model = InventoryPriceHistoryModel
    order_by = (InventoryPriceHistoryModel.id,)
    create_fields = (
        "inventory_id",
        "product_price_tracking_id",
        "price"
    )
    update_fields = create_fields
