from app.repositories.collection_alternative_code_repository import (
    CollectionAlternativeCodeRepository
)


class CollectionAlternativeCodeService:
    @staticmethod
    def get_all():
        return CollectionAlternativeCodeRepository.get_all()

    @staticmethod
    def get_paginated(page, per_page):
        return CollectionAlternativeCodeRepository.get_paginated(
            page,
            per_page
        )

    @staticmethod
    def get_by_id(alternative_code_id):
        return CollectionAlternativeCodeRepository.get_by_id(
            alternative_code_id
        )

    @staticmethod
    def create(data):
        return CollectionAlternativeCodeRepository.create(
            data
        )

    @staticmethod
    def delete(alternative_code_id):
        entity = (
            CollectionAlternativeCodeRepository.get_by_id(
                alternative_code_id
            )
        )
        if not entity:
            return None
        CollectionAlternativeCodeRepository.delete(
            entity
        )
        return True
