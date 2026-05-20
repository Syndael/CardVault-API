from app.controllers.crud_controller import create_crud_blueprint
from app.schemas.inventory_schema import InventorySchema
from app.services.inventory_service import InventoryService


inventory_blueprint = create_crud_blueprint(
    "inventory",
    InventoryService,
    InventorySchema,
    "inventory_id"
)
