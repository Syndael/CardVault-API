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
        if "completion_group_id" not in data:
            std = TypeModel.query.filter_by(type="completion_group", name="Standard").first()
            if std:
                data = {**data, "completion_group_id": std.id}
        return super().create(data)

    @classmethod
    def update(cls, entity_id, data):
        return super().update(entity_id, data)
