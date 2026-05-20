from flask import request, g

from app.models.inventory_model import InventoryModel
from app.repositories.crud_repository import CrudRepository
from app.utils.pagination import paginate_query


def _is_admin():
    user = getattr(g, "current_user", None)
    if not user:
        return False
    return any(ur.role.name == "admin" for ur in getattr(user, "user_roles", []))


class InventoryRepository(CrudRepository):
    model = InventoryModel
    order_by = (InventoryModel.id,)
    create_fields = (
        "product_id",
        "collection_id",
        "extra_type_id",
        "purchase_id",
        "quantity",
        "is_sealed",
        "posted_instagram",
        "language_id",
        "condition_id",
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
