from app.models.inventory_url_model import InventoryUrlModel
from app.repositories.crud_repository import CrudRepository


class InventoryUrlRepository(CrudRepository):
    model = InventoryUrlModel
    order_by = (InventoryUrlModel.id,)
    create_fields = ("inventory_id", "url", "name")
    update_fields = ("url", "name")
