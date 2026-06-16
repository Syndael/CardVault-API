from app.models.wishlist_price_model import WishlistPriceModel
from app.repositories.crud_repository import CrudRepository


class WishlistPriceRepository(CrudRepository):
    model = WishlistPriceModel
    order_by = (WishlistPriceModel.recorded_at.desc(),)
    create_fields = (
        "wishlist_item_id",
        "price",
        "min_price",
        "max_price",
        "min_price_recorded_at",
        "max_price_recorded_at",
        "source",
    )
    update_fields = ()
