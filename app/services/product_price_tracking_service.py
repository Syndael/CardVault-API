from app.repositories.product_price_tracking_repository import (
    ProductPriceTrackingRepository
)
from app.services.crud_service import CrudService


class ProductPriceTrackingService(CrudService):
    repository = ProductPriceTrackingRepository
