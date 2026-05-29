from app.models.inventory_price_history_archive_model import (
    InventoryPriceHistoryArchiveModel
)
from app.repositories.crud_repository import CrudRepository


class InventoryPriceHistoryArchiveRepository(CrudRepository):
    model = InventoryPriceHistoryArchiveModel
    order_by = (InventoryPriceHistoryArchiveModel.id,)
    create_fields = (
        "inventory_id",
        "product_price_tracking_id",
        "price",
        "min_price",
        "max_price",
        "min_price_recorded_at",
        "max_price_recorded_at"
    )
    update_fields = create_fields
