from app.database.session import db
from app.models.collection_translation_model import (
    CollectionTranslationModel
)
from app.utils.pagination import paginate_query

class CollectionTranslationRepository:
    @staticmethod
    def get_all():
        return CollectionTranslationModel.query.order_by(
            CollectionTranslationModel.id
        ).all()

    @staticmethod
    def get_paginated(page, per_page):
        return paginate_query(
            CollectionTranslationModel.query.order_by(
                CollectionTranslationModel.id
            ),
            page,
            per_page
        )

    @staticmethod
    def get_by_id(translation_id):
        return CollectionTranslationModel.query.get(
            translation_id
        )

    @staticmethod
    def create(data):
        entity = CollectionTranslationModel(
            collection_id=data["collection_id"],
            language_id=data["language_id"],
            name=data["name"],
            name_alter=data.get("name_alter")
        )
        db.session.add(entity)
        db.session.commit()
        return entity

    @staticmethod
    def update(entity, data):
        entity.name = data.get(
            "name",
            entity.name
        )
        entity.name_alter = data.get(
            "name_alter",
            entity.name_alter
        )
        entity.language_id = data.get(
            "language_id",
            entity.language_id
        )
        db.session.commit()
        return entity

    @staticmethod
    def delete(entity):
        db.session.delete(entity)
        db.session.commit()
