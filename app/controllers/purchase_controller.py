from app.controllers.crud_controller import create_crud_blueprint
from app.schemas.purchase_schema import PurchaseSchema
from app.services.purchase_service import PurchaseService


purchase_blueprint = create_crud_blueprint(
    "purchases",
    PurchaseService,
    PurchaseSchema,
    "purchase_id",
    read_roles=["inventory_manage", "admin"],
    write_roles=["inventory_manage", "admin"]
)
