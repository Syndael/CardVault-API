from app.repositories.collection_translation_repository import (
    CollectionTranslationRepository
)

class CollectionTranslationService:
    @staticmethod
    def get_all():
        return CollectionTranslationRepository.get_all()

    @staticmethod
    def get_paginated(page, per_page):
        return CollectionTranslationRepository.get_paginated(
            page,
            per_page
        )

    @staticmethod
    def get_by_id(translation_id):
        return CollectionTranslationRepository.get_by_id(
            translation_id
        )

    @staticmethod
    def create(data):
        return CollectionTranslationRepository.create(
            data
        )

    @staticmethod
    def update(translation_id, data):
        entity = (
            CollectionTranslationRepository.get_by_id(
                translation_id
            )
        )
        if not entity:
            return None
        return CollectionTranslationRepository.update(
            entity,
            data
        )

    @staticmethod
    def delete(translation_id):
        entity = (
            CollectionTranslationRepository.get_by_id(
                translation_id
            )
        )
        if not entity:
            return None
        CollectionTranslationRepository.delete(
            entity
        )
        return True
