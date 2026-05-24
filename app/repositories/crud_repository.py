from flask import request

from app.database.session import db
from app.utils.pagination import paginate_query


class CrudRepository:
    model = None
    order_by = None
    create_fields = ()
    update_fields = ()

    @classmethod
    def query(cls):
        query = cls.model.query
        if cls.order_by:
            query = query.order_by(*cls.order_by)
        return query

    @classmethod
    def get_all(cls):
        return cls.query().all()

    @classmethod
    def get_paginated(cls, page, per_page):
        query = cls.query()
        try:
            product_id = request.args.get("product_id")
        except RuntimeError:
            product_id = None

        if product_id is not None and hasattr(cls.model, "product_id"):
            try:
                query = query.filter(cls.model.product_id == int(product_id))
            except ValueError:
                pass

        try:
            language_id = request.args.get("language_id")
        except RuntimeError:
            language_id = None

        if language_id is not None and hasattr(cls.model, "language_id"):
            try:
                query = query.filter(cls.model.language_id == int(language_id))
            except ValueError:
                pass

        try:
            purchase_id = request.args.get("purchase_id")
        except RuntimeError:
            purchase_id = None

        if purchase_id is not None and hasattr(cls.model, "purchase_id"):
            try:
                query = query.filter(cls.model.purchase_id == int(purchase_id))
            except ValueError:
                pass

        return paginate_query(query, page, per_page)

    @classmethod
    def get_by_id(cls, entity_id):
        return cls.model.query.get(entity_id)

    @classmethod
    def create(cls, data):
        entity = cls.model(
            **{
                field: data[field]
                for field in cls.create_fields
                if field in data
            }
        )
        db.session.add(entity)
        db.session.commit()
        return entity

    @classmethod
    def update(cls, entity, data):
        for field in cls.update_fields:
            if field in data:
                setattr(entity, field, data[field])

        db.session.commit()
        return entity

    @classmethod
    def delete(cls, entity):
        db.session.delete(entity)
        db.session.commit()
