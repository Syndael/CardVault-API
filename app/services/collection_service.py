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
    def get_filtered_paginated(filters, page, per_page):
        return CollectionRepository.get_filtered_paginated(filters, page, per_page)

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
        if not CollectionRepository.delete(entity):
            raise ValueError("No se puede eliminar la colección porque tiene productos o traducciones asociados")
        return True
