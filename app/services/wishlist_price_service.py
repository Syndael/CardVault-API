from app.repositories.wishlist_price_repository import WishlistPriceRepository
from app.services.crud_service import CrudService


class WishlistPriceService(CrudService):
    repository = WishlistPriceRepository
