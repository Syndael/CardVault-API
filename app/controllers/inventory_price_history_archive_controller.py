from app.controllers.crud_controller import create_crud_blueprint
from app.schemas.inventory_price_history_archive_schema import (
    InventoryPriceHistoryArchiveSchema
)
from app.services.inventory_price_history_archive_service import (
    InventoryPriceHistoryArchiveService
)

inventory_price_history_archive_blueprint = create_crud_blueprint(
    "inventory_price_history_archive",
    InventoryPriceHistoryArchiveService,
    InventoryPriceHistoryArchiveSchema,
    "history_id",
    read_roles=["inventory_manage", "admin"],
    write_roles=["inventory_manage", "admin"]
)
