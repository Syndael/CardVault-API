from app.models.product_model import ProductModel
from app.repositories.crud_repository import CrudRepository


class ProductRepository(CrudRepository):
    model = ProductModel
    order_by = (ProductModel.id,)
    create_fields = (
        "collection_id",
        "product_type_id",
        "product_format_id",
        "product_number",
        "force_download",
        "is_verified",
        "is_manual",
        "completion_group",
    )
    update_fields = create_fields
