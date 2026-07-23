from app.database.session import db
from app.models.type_model import TypeModel
from app.utils.pagination import paginate_query


class TypeRepository:
    @staticmethod
    def get_all():
        return TypeModel.query.order_by(TypeModel.id).all()

    @staticmethod
    def get_paginated(page, per_page, type_filter=""):
        query = TypeModel.query.order_by(TypeModel.id)
        if type_filter:
            query = query.filter(TypeModel.type == type_filter)
        return paginate_query(query, page, per_page)

    @staticmethod
    def get_by_id(type_id):
        return TypeModel.query.get(type_id)

    @staticmethod
    def create(data):
        entity = TypeModel(
            name=data["name"],
            short_name=data.get("short_name"),
            type=data["type"]
        )
        db.session.add(entity)
        db.session.commit()
        return entity

    @staticmethod
    def update(entity, data):
        entity.name = data.get("name", entity.name)
        entity.short_name = data.get("short_name", entity.short_name)
        entity.type = data.get("type", entity.type)
        db.session.commit()
        return entity

    @staticmethod
    def delete(entity):
        db.session.delete(entity)
        db.session.commit()
