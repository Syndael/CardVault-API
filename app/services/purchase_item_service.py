from app.repositories.purchase_item_repository import PurchaseItemRepository
from app.services.crud_service import CrudService


class PurchaseItemService(CrudService):
    repository = PurchaseItemRepository
