from flask import request, g
from sqlalchemy import and_, exists, func, select
from sqlalchemy.orm import joinedload, selectinload

from app.models.collection_model import CollectionModel
from app.models.inventory_model import InventoryModel
from app.models.inventory_price_history_model import InventoryPriceHistoryModel
from app.models.inventory_tag_model import InventoryTagModel
from app.models.language_model import LanguageModel
from app.models.product_model import ProductModel
from app.models.product_translation_model import ProductTranslationModel
from app.models.purchase_item_model import PurchaseItemModel
from app.models.tag_model import TagModel
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
        "purchase_item_id",
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

        try:
            tag_name = request.args.get("tag_name", "").strip()
        except RuntimeError:
            tag_name = ""
        if tag_name:
            tag_names = [t.strip() for t in tag_name.split(",") if t.strip()]
            for tn in tag_names:
                query = query.filter(
                    exists(
                        select(1)
                        .select_from(InventoryTagModel)
                        .join(TagModel)
                        .where(
                            and_(
                                InventoryTagModel.inventory_id == InventoryModel.id,
                                TagModel.name.ilike(f"%{tn}%")
                            )
                        )
                    )
                )

        try:
            raw_sort = (request.args.get("sort") or "newest").strip()
        except RuntimeError:
            raw_sort = "newest"

        query = query.order_by(None)
        if raw_sort == "oldest":
            query = query.order_by(InventoryModel.id.asc())
        elif raw_sort == "name_collection":
            pt_subq = (
                select(ProductTranslationModel.name)
                .where(ProductTranslationModel.product_id == ProductModel.id)
                .order_by(ProductTranslationModel.id)
                .limit(1)
                .correlate(ProductModel)
                .scalar_subquery()
            )
            if not _joined_product:
                query = query.join(InventoryModel.product)
                _joined_product = True
            if not _joined_collection:
                query = query.join(InventoryModel.collection)
                _joined_collection = True
            query = query.order_by(pt_subq, CollectionModel.code)
        elif raw_sort == "collection_name":
            pt_subq = (
                select(ProductTranslationModel.name)
                .where(ProductTranslationModel.product_id == ProductModel.id)
                .order_by(ProductTranslationModel.id)
                .limit(1)
                .correlate(ProductModel)
                .scalar_subquery()
            )
            if not _joined_product:
                query = query.join(InventoryModel.product)
                _joined_product = True
            if not _joined_collection:
                query = query.join(InventoryModel.collection)
                _joined_collection = True
            query = query.order_by(CollectionModel.code, pt_subq)
        elif raw_sort == "collection_product_number_name":
            pt_subq = (
                select(ProductTranslationModel.name)
                .where(ProductTranslationModel.product_id == ProductModel.id)
                .order_by(ProductTranslationModel.id)
                .limit(1)
                .correlate(ProductModel)
                .scalar_subquery()
            )
            if not _joined_product:
                query = query.join(InventoryModel.product)
                _joined_product = True
            if not _joined_collection:
                query = query.join(InventoryModel.collection)
                _joined_collection = True
            query = query.order_by(CollectionModel.code, func.length(ProductModel.product_number), ProductModel.product_number, pt_subq)
        elif raw_sort == "price_collection_product_number_name":
            latest_price_subq = (
                select(InventoryPriceHistoryModel.price)
                .where(InventoryPriceHistoryModel.inventory_id == InventoryModel.id)
                .order_by(InventoryPriceHistoryModel.recorded_at.desc())
                .limit(1)
                .correlate(InventoryModel)
                .scalar_subquery()
            )
            pt_subq = (
                select(ProductTranslationModel.name)
                .where(ProductTranslationModel.product_id == ProductModel.id)
                .order_by(ProductTranslationModel.id)
                .limit(1)
                .correlate(ProductModel)
                .scalar_subquery()
            )
            if not _joined_product:
                query = query.join(InventoryModel.product)
                _joined_product = True
            if not _joined_collection:
                query = query.join(InventoryModel.collection)
                _joined_collection = True
            query = query.order_by(latest_price_subq.is_(None), latest_price_subq.desc(), CollectionModel.code, func.length(ProductModel.product_number), ProductModel.product_number, pt_subq)
        elif raw_sort == "language_collection_product_number_name":
            lang_subq = (
                select(LanguageModel.name)
                .where(LanguageModel.id == InventoryModel.language_id)
                .correlate(InventoryModel)
                .scalar_subquery()
            )
            pt_subq = (
                select(ProductTranslationModel.name)
                .where(ProductTranslationModel.product_id == ProductModel.id)
                .order_by(ProductTranslationModel.id)
                .limit(1)
                .correlate(ProductModel)
                .scalar_subquery()
            )
            if not _joined_product:
                query = query.join(InventoryModel.product)
                _joined_product = True
            if not _joined_collection:
                query = query.join(InventoryModel.collection)
                _joined_collection = True
            query = query.order_by(lang_subq.is_(None), lang_subq, CollectionModel.code, func.length(ProductModel.product_number), ProductModel.product_number, pt_subq)
        elif raw_sort == "difference_collection_product_number_name":
            latest_price_subq = (
                select(InventoryPriceHistoryModel.price)
                .where(InventoryPriceHistoryModel.inventory_id == InventoryModel.id)
                .order_by(InventoryPriceHistoryModel.recorded_at.desc())
                .limit(1)
                .correlate(InventoryModel)
                .scalar_subquery()
            )
            acq_price_subq = (
                select(PurchaseItemModel.unit_price)
                .where(PurchaseItemModel.id == InventoryModel.purchase_item_id)
                .correlate(InventoryModel)
                .scalar_subquery()
            )
            pt_subq = (
                select(ProductTranslationModel.name)
                .where(ProductTranslationModel.product_id == ProductModel.id)
                .order_by(ProductTranslationModel.id)
                .limit(1)
                .correlate(ProductModel)
                .scalar_subquery()
            )
            if not _joined_product:
                query = query.join(InventoryModel.product)
                _joined_product = True
            if not _joined_collection:
                query = query.join(InventoryModel.collection)
                _joined_collection = True
            diff = latest_price_subq - acq_price_subq
            query = query.order_by(diff.is_(None), diff.desc(), CollectionModel.code, func.length(ProductModel.product_number), ProductModel.product_number, pt_subq)
        else:
            query = query.order_by(InventoryModel.id.desc())

        query = query.options(
            joinedload(InventoryModel.collection),
            joinedload(InventoryModel.language),
            joinedload(InventoryModel.condition),
            joinedload(InventoryModel.extra_type),
            joinedload(InventoryModel.product).selectinload(ProductModel.translations),
            joinedload(InventoryModel.product).joinedload(ProductModel.product_type),
            joinedload(InventoryModel.purchase),
            joinedload(InventoryModel.purchase_item),
        )

        return paginate_query(query, page, per_page)
