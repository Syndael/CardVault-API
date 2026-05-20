from app.repositories.language_repository import LanguageRepository


class LanguageService:
    @staticmethod
    def get_all():
        return LanguageRepository.get_all()

    @staticmethod
    def get_paginated(page, per_page):
        return LanguageRepository.get_paginated(
            page,
            per_page
        )

    @staticmethod
    def get_by_id(language_id):
        return LanguageRepository.get_by_id(language_id)

    @staticmethod
    def create(data):
        return LanguageRepository.create(data)

    @staticmethod
    def update(language_id, data):
        entity = LanguageRepository.get_by_id(language_id)
        if not entity:
            return None
        return LanguageRepository.update(entity, data)

    @staticmethod
    def delete(language_id):
        entity = LanguageRepository.get_by_id(language_id)
        if not entity:
            return None
        LanguageRepository.delete(entity)
        return True
