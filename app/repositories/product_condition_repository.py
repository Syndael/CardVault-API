from app.models.product_condition_model import ProductConditionModel
from app.repositories.crud_repository import CrudRepository


class ProductConditionRepository(CrudRepository):
    model = ProductConditionModel
    order_by = (ProductConditionModel.id,)
    create_fields = (
        "name",
        "abbreviation",
        "cardmarket_code"
    )
    update_fields = create_fields
