from app.models.wishlist_item_model import WishlistItemModel
from app.repositories.crud_repository import CrudRepository


class WishlistItemRepository(CrudRepository):
    model = WishlistItemModel
    order_by = (WishlistItemModel.created_at.desc(),)
    create_fields = (
        "user_id",
        "product_id",
        "target_price",
        "language_id",
        "condition_id",
        "w_state",
        "notes",
    )
    update_fields = (
        "product_id",
        "target_price",
        "language_id",
        "condition_id",
        "w_state",
        "notes",
    )
