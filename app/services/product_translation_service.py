from app.repositories.product_translation_repository import (
    ProductTranslationRepository
)
from app.services.crud_service import CrudService


class ProductTranslationService(CrudService):
    repository = ProductTranslationRepository
