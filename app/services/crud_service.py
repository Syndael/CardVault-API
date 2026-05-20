class CrudService:
    repository = None

    @classmethod
    def get_all(cls):
        return cls.repository.get_all()

    @classmethod
    def get_paginated(cls, page, per_page):
        return cls.repository.get_paginated(
            page,
            per_page
        )

    @classmethod
    def get_by_id(cls, entity_id):
        return cls.repository.get_by_id(entity_id)

    @classmethod
    def create(cls, data):
        return cls.repository.create(data)

    @classmethod
    def update(cls, entity_id, data):
        entity = cls.repository.get_by_id(entity_id)
        if not entity:
            return None
        return cls.repository.update(entity, data)

    @classmethod
    def delete(cls, entity_id):
        entity = cls.repository.get_by_id(entity_id)
        if not entity:
            return None
        cls.repository.delete(entity)
        return True
