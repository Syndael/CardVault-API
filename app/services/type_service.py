from app.repositories.type_repository import TypeRepository

class TypeService:
    @staticmethod
    def get_all():
        return TypeRepository.get_all()

    @staticmethod
    def get_paginated(page, per_page):
        return TypeRepository.get_paginated(
            page,
            per_page
        )

    @staticmethod
    def get_by_id(type_id):
        return TypeRepository.get_by_id(type_id)

    @staticmethod
    def create(data):
        return TypeRepository.create(data)

    @staticmethod
    def update(type_id, data):
        entity = TypeRepository.get_by_id(type_id)
        if not entity:
            return None
        return TypeRepository.update(entity, data)

    @staticmethod
    def delete(type_id):
        entity = TypeRepository.get_by_id(type_id)
        if not entity:
            return None
        TypeRepository.delete(entity)
        return True
