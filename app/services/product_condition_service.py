from app.repositories.product_condition_repository import (
    ProductConditionRepository
)
from app.services.crud_service import CrudService


class ProductConditionService(CrudService):
    repository = ProductConditionRepository
