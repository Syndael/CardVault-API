from app.controllers.crud_controller import create_crud_blueprint
from app.schemas.product_price_tracking_schema import (
    ProductPriceTrackingSchema
)
from app.services.product_price_tracking_service import (
    ProductPriceTrackingService
)


product_price_tracking_blueprint = create_crud_blueprint(
    "product_price_tracking",
    ProductPriceTrackingService,
    ProductPriceTrackingSchema,
    "tracking_id",
    read_roles=["product_read", "admin"],
    write_roles=["product_write", "admin"]
)
