from flask import request

from app.models.entity_model import EntityModel
from app.repositories.crud_repository import CrudRepository
from app.utils.pagination import paginate_query


class EntityRepository(CrudRepository):
    model = EntityModel
    order_by = (EntityModel.id,)
    create_fields = (
        "name",
        "url",
        "entity_type",
        "parent_id"
    )
    update_fields = create_fields

    @classmethod
    def get_paginated(cls, page, per_page):
        query = cls.model.query.order_by(*cls.order_by)
        try:
            entity_type = request.args.get("entity_type")
        except RuntimeError:
            entity_type = None
        if entity_type is not None:
            try:
                query = query.filter(
                    cls.model.entity_type == int(entity_type)
                )
            except ValueError:
                pass
        return paginate_query(query, page, per_page)
