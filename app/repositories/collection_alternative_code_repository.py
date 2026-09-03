from flask import request

from app.database.session import db
from app.models.collection_alternative_code_model import CollectionAlternativeCodeModel
from app.utils.pagination import paginate_query


class CollectionAlternativeCodeRepository:
    @staticmethod
    def get_all():
        return CollectionAlternativeCodeModel.query.order_by(
            CollectionAlternativeCodeModel.id
        ).all()

    @staticmethod
    def get_paginated(page, per_page):
        query = CollectionAlternativeCodeModel.query.order_by(
            CollectionAlternativeCodeModel.id
        )
        try:
            collection_id = request.args.get("collection_id")
        except RuntimeError:
            collection_id = None
        if collection_id is not None:
            try:
                query = query.filter(
                    CollectionAlternativeCodeModel.collection_id == int(collection_id)
                )
            except ValueError:
                pass

        return paginate_query(query, page, per_page)

    @staticmethod
    def get_by_id(alternative_code_id):
        return CollectionAlternativeCodeModel.query.get(
            alternative_code_id
        )

    @staticmethod
    def create(data):
        entity = CollectionAlternativeCodeModel(
            collection_id=data["collection_id"],
            code=data["code"]
        )
        db.session.add(entity)
        db.session.commit()
        return entity

    @staticmethod
    def delete(entity):
        db.session.delete(entity)
        db.session.commit()
