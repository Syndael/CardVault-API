from sqlalchemy import or_

from app.database.session import db
from app.models.collection_model import CollectionModel
from app.utils.pagination import paginate_query


class CollectionRepository:
    @staticmethod
    def get_all():
        return CollectionModel.query.order_by(CollectionModel.id).all()

    @staticmethod
    def get_paginated(page, per_page):
        return paginate_query(
            CollectionModel.query.order_by(CollectionModel.id),
            page,
            per_page
        )

    @staticmethod
    def get_search_paginated(search, page, per_page):
        like = f"%{search}%"
        query = CollectionModel.query.filter(
            or_(
                CollectionModel.code.ilike(like),
                CollectionModel.id.cast(db.String).ilike(like)
            )
        ).order_by(CollectionModel.id)
        return paginate_query(query, page, per_page)

    @staticmethod
    def get_by_id(collection_id):
        return CollectionModel.query.get(collection_id)

    @staticmethod
    def create(data):
        entity = CollectionModel(
            card_type_id=data["card_type_id"],
            code=data["code"],
            is_manual=data.get("is_manual", False),
            release_date=data.get("release_date")
        )
        db.session.add(entity)
        db.session.commit()
        return entity

    @staticmethod
    def update(entity, data):
        entity.card_type_id = data.get(
            "card_type_id",
            entity.card_type_id
        )
        entity.code = data.get("code", entity.code)
        entity.is_manual = data.get("is_manual", entity.is_manual)
        entity.release_date = data.get("release_date", entity.release_date)
        db.session.commit()
        return entity

    @staticmethod
    def delete(entity):
        db.session.delete(entity)
        db.session.commit()
