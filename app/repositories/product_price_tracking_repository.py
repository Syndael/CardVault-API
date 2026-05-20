from app.models.product_price_tracking_model import ProductPriceTrackingModel
from app.repositories.crud_repository import CrudRepository


class ProductPriceTrackingRepository(CrudRepository):
    model = ProductPriceTrackingModel
    order_by = (ProductPriceTrackingModel.id,)
    create_fields = (
        "product_id",
        "price_source_id",
        "url"
    )
    update_fields = create_fields
