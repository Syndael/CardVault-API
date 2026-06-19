from app.database.session import db
from app.models.product_translation_model import ProductTranslationModel
from app.repositories.product_translation_repository import (
    ProductTranslationRepository
)
from app.services.crud_service import CrudService


class ProductTranslationService(CrudService):
    repository = ProductTranslationRepository

    @classmethod
    def create(cls, data):
        product_id = data.get("product_id")
        language_id = data.get("language_id")
        if product_id and language_id:
            existing = ProductTranslationModel.query.filter_by(
                product_id=product_id,
                language_id=language_id
            ).first()
            if existing:
                for field in cls.repository.update_fields:
                    if field in data:
                        setattr(existing, field, data[field])
                db.session.commit()
                return existing
        return cls.repository.create(data)
