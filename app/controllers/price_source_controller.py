from app.controllers.crud_controller import create_crud_blueprint
from app.schemas.price_source_schema import PriceSourceSchema
from app.services.price_source_service import PriceSourceService


price_source_blueprint = create_crud_blueprint(
    "price_sources",
    PriceSourceService,
    PriceSourceSchema,
    "price_source_id"
)
