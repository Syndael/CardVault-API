from app.models.product_translation_model import ProductTranslationModel
from app.repositories.crud_repository import CrudRepository


class ProductTranslationRepository(CrudRepository):
    model = ProductTranslationModel
    order_by = (ProductTranslationModel.id,)
    create_fields = (
        "product_id",
        "language_id",
        "name",
        "name_alter"
    )
    update_fields = create_fields
