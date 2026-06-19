from app.models.type_model import TypeModel
from app.repositories.product_repository import ProductRepository
from app.services.crud_service import CrudService


class ProductService(CrudService):
    repository = ProductRepository

    @classmethod
    def create(cls, data):
        if "product_format_id" not in data:
            carta = TypeModel.query.filter_by(type="product_format", name="carta").first()
            if carta:
                data = {**data, "product_format_id": carta.id}
        return super().create(data)
