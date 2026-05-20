from app.database.session import db
from app.models.language_model import LanguageModel
from app.utils.pagination import paginate_query


class LanguageRepository:
    @staticmethod
    def get_all():
        return LanguageModel.query.order_by(
            LanguageModel.priority_order,
            LanguageModel.name
        ).all()

    @staticmethod
    def get_paginated(page, per_page):
        return paginate_query(
            LanguageModel.query.order_by(
                LanguageModel.priority_order,
                LanguageModel.name
            ),
            page,
            per_page
        )

    @staticmethod
    def get_by_id(language_id):
        return LanguageModel.query.get(language_id)

    @staticmethod
    def create(data):
        entity = LanguageModel(
            name=data["name"],
            abbreviation=data["abbreviation"],
            cardmarket_code=data.get("cardmarket_code"),
            tcgdex_language_code=data.get("tcgdex_language_code"),
            priority_order=data.get("priority_order", 999)
        )
        db.session.add(entity)
        db.session.commit()
        return entity

    @staticmethod
    def update(entity, data):
        entity.name = data.get("name", entity.name)
        entity.abbreviation = data.get(
            "abbreviation",
            entity.abbreviation
        )
        entity.cardmarket_code = data.get(
            "cardmarket_code",
            entity.cardmarket_code
        )
        entity.tcgdex_language_code = data.get(
            "tcgdex_language_code",
            entity.tcgdex_language_code
        )
        entity.priority_order = data.get(
            "priority_order",
            entity.priority_order
        )
        db.session.commit()
        return entity

    @staticmethod
    def delete(entity):
        db.session.delete(entity)
        db.session.commit()
