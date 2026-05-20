from app.repositories.collection_repository import CollectionRepository


class CollectionService:
    @staticmethod
    def get_all():
        return CollectionRepository.get_all()

    @staticmethod
    def get_paginated(page, per_page):
        return CollectionRepository.get_paginated(
            page,
            per_page
        )

    @staticmethod
    def get_search_paginated(search, page, per_page):
        return CollectionRepository.get_search_paginated(search, page, per_page)

    @staticmethod
    def get_by_id(collection_id):
        return CollectionRepository.get_by_id(collection_id)

    @staticmethod
    def create(data):
        return CollectionRepository.create(data)

    @staticmethod
    def update(collection_id, data):
        entity = CollectionRepository.get_by_id(collection_id)
        if not entity:
            return None
        return CollectionRepository.update(entity, data)

    @staticmethod
    def delete(collection_id):
        entity = CollectionRepository.get_by_id(collection_id)
        if not entity:
            return None
        CollectionRepository.delete(entity)
        return True
