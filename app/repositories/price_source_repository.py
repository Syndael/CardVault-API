from app.models.price_source_model import PriceSourceModel
from app.repositories.crud_repository import CrudRepository


class PriceSourceRepository(CrudRepository):
    model = PriceSourceModel
    order_by = (PriceSourceModel.id,)
    create_fields = (
        "name",
        "base_url",
        "language_param",
        "condition_param"
    )
    update_fields = create_fields
