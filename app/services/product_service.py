from app.models.type_model import TypeModel
from app.repositories.product_repository import ProductRepository
from app.services.crud_service import CrudService


VALID_COMPLETION_GROUPS = {"standard", "secret", "optional"}


def _normalize_completion_group(data):
    if "completion_group" not in data:
        return data
    value = (data.get("completion_group") or "standard").strip().lower()
    if value not in VALID_COMPLETION_GROUPS:
        value = "standard"
    return {**data, "completion_group": value}


class ProductService(CrudService):
    repository = ProductRepository

    @classmethod
    def create(cls, data):
        data = _normalize_completion_group(data)
        if "product_format_id" not in data:
            carta = TypeModel.query.filter_by(type="product_format", name="carta").first()
            if carta:
                data = {**data, "product_format_id": carta.id}
        return super().create(data)

    @classmethod
    def update(cls, entity_id, data):
        return super().update(entity_id, _normalize_completion_group(data))
