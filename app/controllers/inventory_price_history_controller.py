from app.controllers.crud_controller import create_crud_blueprint
from app.schemas.inventory_price_history_schema import (
    InventoryPriceHistorySchema
)
from app.services.inventory_price_history_service import (
    InventoryPriceHistoryService
)


inventory_price_history_blueprint = create_crud_blueprint(
    "inventory_price_history",
    InventoryPriceHistoryService,
    InventoryPriceHistorySchema,
    "history_id",
    read_roles=["inventory_manage", "admin"],
    write_roles=["inventory_manage", "admin"]
)
