from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from app.database.session import db
from app.models.collection_model import CollectionModel
from app.models.collection_translation_model import CollectionTranslationModel
from app.models.type_model import TypeModel
from app.utils.pagination import paginate_query


class CollectionRepository:
    @staticmethod
    def get_all():
        return CollectionModel.query.order_by(CollectionModel.id).all()

    @staticmethod
    def _base_query():
        return CollectionModel.query.options(
            joinedload(CollectionModel.translations).joinedload(CollectionTranslationModel.language)
        )

    @staticmethod
    def _apply_sort(query, sort_by=None):
        if not sort_by or sort_by == "type_code_manual":
            return query.order_by(
                CollectionModel.card_type_id, CollectionModel.code, CollectionModel.is_manual
            )
        if sort_by == "code":
            return query.order_by(CollectionModel.code)
        if sort_by == "type_code":
            return query.order_by(CollectionModel.card_type_id, CollectionModel.code)
        if sort_by == "name":
            return query.outerjoin(
                CollectionTranslationModel,
                CollectionModel.id == CollectionTranslationModel.collection_id
            ).order_by(CollectionTranslationModel.name).distinct(CollectionModel.id)
        return query.order_by(CollectionModel.id)

    @staticmethod
    def get_paginated(page, per_page, sort_by=None):
        return paginate_query(
            CollectionRepository._apply_sort(CollectionRepository._base_query(), sort_by),
            page,
            per_page
        )

    @staticmethod
    def get_search_paginated(search, page, per_page, sort_by=None):
        like = f"%{search}%"
        query = CollectionRepository._base_query().filter(
            or_(
                CollectionModel.code.ilike(like),
                CollectionModel.id.cast(db.String).ilike(like)
            )
        )
        query = CollectionRepository._apply_sort(query, sort_by)
        return paginate_query(query, page, per_page)

    @staticmethod
    def get_filtered_paginated(filters, page, per_page, sort_by=None):
        query = CollectionRepository._base_query()
        conditions = []
        code = filters.get("code")
        if code:
            conditions.append(CollectionModel.code.ilike(f"%{code}%"))
        name = filters.get("name")
        if name:
            conditions.append(
                CollectionModel.translations.any(
                    CollectionTranslationModel.name.ilike(f"%{name}%")
                )
            )
        card_type_id = filters.get("card_type_id")
        if card_type_id:
            try:
                conditions.append(CollectionModel.card_type_id == int(card_type_id))
            except ValueError:
                pass
        is_manual = filters.get("is_manual")
        if is_manual is not None and is_manual != "":
            conditions.append(CollectionModel.is_manual == (is_manual in ("1", "true", "True")))
        if conditions:
            query = query.filter(*conditions)
        query = CollectionRepository._apply_sort(query, sort_by)
        return paginate_query(query, page, per_page)

    @staticmethod
    def get_by_id(collection_id):
        return CollectionRepository._base_query().filter(CollectionModel.id == collection_id).first()

    @staticmethod
    def create(data):
        entity = CollectionModel(
            card_type_id=data["card_type_id"],
            code=data["code"],
            is_manual=data.get("is_manual", True),
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
        try:
            db.session.delete(entity)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            return False
