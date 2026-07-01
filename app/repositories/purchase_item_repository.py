from app.models.purchase_item_model import PurchaseItemModel
from app.repositories.crud_repository import CrudRepository


class PurchaseItemRepository(CrudRepository):
    model = PurchaseItemModel
    order_by = (PurchaseItemModel.id,)
    create_fields = (
        "purchase_id",
        "product_id",
        "unit_price",
        "quantity",
        "split_quantity",
        "conversion_rate",
        "original_unit_price",
        "original_currency"
    )
    update_fields = create_fields
