from flask import request, g

from app.models.collection_model import CollectionModel
from app.models.inventory_model import InventoryModel
from app.models.product_model import ProductModel
from app.models.product_translation_model import ProductTranslationModel
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
        show_all = False
        try:
            show_all = request.args.get("all", "").lower() in ("1", "true", "yes")
        except RuntimeError:
            pass
        if _is_admin() and show_all:
            pass
        elif not _is_admin():
            user = getattr(g, "current_user", None)
            if user:
                query = query.filter(cls.model.user_id == user.id)
        else:
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

        _joined_collection = False
        _joined_product = False

        try:
            collection_code = request.args.get("collection_code", "").strip()
        except RuntimeError:
            collection_code = ""
        if collection_code:
            if not _joined_collection:
                query = query.join(cls.model.collection)
                _joined_collection = True
            query = query.filter(CollectionModel.code.ilike(f"%{collection_code}%"))

        try:
            card_type_id = request.args.get("card_type_id", "").strip()
        except RuntimeError:
            card_type_id = ""
        if card_type_id:
            try:
                cid = int(card_type_id)
                if not _joined_product:
                    query = query.join(cls.model.product)
                    _joined_product = True
                query = query.filter(ProductModel.product_type_id == cid)
            except ValueError:
                pass

        try:
            product_number = request.args.get("product_number", "").strip()
        except RuntimeError:
            product_number = ""
        if product_number:
            if not _joined_product:
                query = query.join(cls.model.product)
                _joined_product = True
            query = query.filter(ProductModel.product_number.ilike(f"%{product_number}%"))

        try:
            product_name = request.args.get("product_name", "").strip()
        except RuntimeError:
            product_name = ""
        if product_name:
            if not _joined_product:
                query = query.join(cls.model.product)
                _joined_product = True
            query = query.join(ProductModel.translations).filter(
                ProductTranslationModel.name.ilike(f"%{product_name}%")
            )

        return paginate_query(query, page, per_page)
