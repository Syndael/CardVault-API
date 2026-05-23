from app.controllers.crud_controller import create_crud_blueprint
from app.schemas.inventory_schema import InventoryListSchema, InventorySchema
from app.services.inventory_service import InventoryService


inventory_blueprint = create_crud_blueprint(
    "inventory",
    InventoryService,
    InventorySchema,
    "inventory_id",
    read_roles=["inventory_manage", "admin"],
    write_roles=["inventory_manage", "admin"],
    list_schema_class=InventoryListSchema
)
