from flask import request, g

from app.models.purchase_model import PurchaseModel
from app.repositories.crud_repository import CrudRepository
from app.utils.pagination import paginate_query


def _is_admin():
    user = getattr(g, "current_user", None)
    if not user:
        return False
    return any(ur.role.name == "admin" for ur in getattr(user, "user_roles", []))


class PurchaseRepository(CrudRepository):
    model = PurchaseModel
    order_by = (PurchaseModel.id,)
    create_fields = (
        "entity_id",
        "purchase_date",
        "total_amount",
        "shipping_cost",
        "currency",
        "external_reference",
        "user_id",
        "notes"
    )
    update_fields = create_fields

    @classmethod
    def get_paginated(cls, page, per_page):
        query = cls.query()
        if not _is_admin():
            user = getattr(g, "current_user", None)
            if user:
                query = query.filter(cls.model.user_id == user.id)
        try:
            product_id = request.args.get("product_id")
        except RuntimeError:
            product_id = None
        if product_id and hasattr(cls.model, "product_id"):
            try:
                pid = int(product_id)
                query = query.filter(cls.model.product_id == pid)
            except ValueError:
                pass
        return paginate_query(query, page, per_page)
