from app.controllers.crud_controller import create_crud_blueprint
from app.schemas.purchase_item_schema import PurchaseItemSchema
from app.services.purchase_item_service import PurchaseItemService


purchase_item_blueprint = create_crud_blueprint(
    "purchase_items",
    PurchaseItemService,
    PurchaseItemSchema,
    "purchase_item_id"
)
