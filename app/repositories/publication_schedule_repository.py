from datetime import datetime

from flask import request
from sqlalchemy import or_
from sqlalchemy.orm import selectinload

from app.models.collection_model import CollectionModel
from app.models.inventory_model import InventoryModel
from app.models.product_model import ProductModel
from app.models.product_translation_model import ProductTranslationModel
from app.models.publication_schedule_model import PublicationScheduleModel
from app.models.type_model import TypeModel
from app.repositories.crud_repository import CrudRepository
from app.utils.pagination import paginate_query


class PublicationScheduleRepository(CrudRepository):
    model = PublicationScheduleModel
    order_by = (PublicationScheduleModel.scheduled_at,)
    create_fields = (
        "inventory_id",
        "scheduled_at",
        "status",
        "caption",
    )
    update_fields = (
        "scheduled_at",
        "status",
        "caption",
        "published_at",
        "instagram_media_id",
        "instagram_permalink",
        "error_message",
    )
    _status_cache: dict = {} 

    @classmethod
    def create(cls, data):
        if "status" not in data:
            data = {**data, "status": "pending_review"}
        return super().create(data)

    @classmethod
    def _get_status_id(cls, name):
        if name not in cls._status_cache:
            t = TypeModel.query.filter_by(type="publication_status", name=name).first()
            cls._status_cache[name] = t.id if t else None
        return cls._status_cache[name]

    @classmethod
    def get_paginated(cls, page, per_page):
        query = cls.query()

        _joined_inventory = False
        _joined_product = False
        _joined_collection = False

        try:
            status = request.args.get("status")
        except RuntimeError:
            status = None
        if status:
            status_id = cls._get_status_id(status)
            if status_id:
                query = query.filter(cls.model.status_id == status_id)

        try:
            collection_code = request.args.get("collection_code", "").strip()
        except RuntimeError:
            collection_code = ""
        if collection_code:
            if not _joined_inventory:
                query = query.join(cls.model.inventory)
                _joined_inventory = True
            if not _joined_collection:
                query = query.join(InventoryModel.collection)
                _joined_collection = True
            query = query.filter(CollectionModel.code.ilike(f"%{collection_code}%"))

        try:
            product_number = request.args.get("product_number", "").strip()
        except RuntimeError:
            product_number = ""
        if product_number:
            if not _joined_inventory:
                query = query.join(cls.model.inventory)
                _joined_inventory = True
            if not _joined_product:
                query = query.join(InventoryModel.product)
                _joined_product = True
            query = query.filter(ProductModel.product_number.ilike(f"%{product_number}%"))

        try:
            product_name = request.args.get("product_name", "").strip()
        except RuntimeError:
            product_name = ""
        if product_name:
            if not _joined_inventory:
                query = query.join(cls.model.inventory)
                _joined_inventory = True
            if not _joined_product:
                query = query.join(InventoryModel.product)
                _joined_product = True
            if not _joined_collection:
                query = query.join(InventoryModel.collection)
                _joined_collection = True
            query = query.join(ProductModel.translations).filter(
                or_(
                    ProductTranslationModel.name.ilike(f"%{product_name}%"),
                    CollectionModel.code.ilike(f"%{product_name}%"),
                    ProductModel.product_number.ilike(f"%{product_name}%"),
                )
            )

        try:
            inventory_id = request.args.get("inventory_id")
        except RuntimeError:
            inventory_id = None
        if inventory_id is not None:
            try:
                query = query.filter(cls.model.inventory_id == int(inventory_id))
            except ValueError:
                pass

        try:
            date_from = request.args.get("date_from", "").strip()
        except RuntimeError:
            date_from = ""
        if date_from:
            try:
                dt = datetime.fromisoformat(date_from)
                query = query.filter(cls.model.scheduled_at >= dt)
            except ValueError:
                pass

        try:
            date_to = request.args.get("date_to", "").strip()
        except RuntimeError:
            date_to = ""
        if date_to:
            try:
                dt = datetime.fromisoformat(date_to)
                query = query.filter(cls.model.scheduled_at <= dt)
            except ValueError:
                pass

        try:
            raw_sort = (request.args.get("sort") or "recent").strip()
        except RuntimeError:
            raw_sort = "recent"

        query = query.order_by(None)
        if raw_sort == "oldest":
            query = query.order_by(cls.model.created_at.asc())
        elif raw_sort == "scheduled":
            query = query.order_by(cls.model.scheduled_at.is_(None).asc(), cls.model.scheduled_at.desc())
        else:
            query = query.order_by(cls.model.created_at.desc())

        query = query.options(
            selectinload(cls.model.inventory).options(
                selectinload(InventoryModel.product).options(
                    selectinload(ProductModel.translations),
                    selectinload(ProductModel.collection).options(
                        selectinload(CollectionModel.translations),
                        selectinload(CollectionModel.card_type),
                    ),
                    selectinload(ProductModel.product_type),
                    selectinload(ProductModel.product_format),
                    selectinload(ProductModel.completion_group),
                ),
                selectinload(InventoryModel.collection).options(
                    selectinload(CollectionModel.translations),
                    selectinload(CollectionModel.card_type),
                ),
                selectinload(InventoryModel.language),
                selectinload(InventoryModel.purchase),
                selectinload(InventoryModel.purchase_item),
                selectinload(InventoryModel.extra_type),
                selectinload(InventoryModel.condition),
                selectinload(InventoryModel.files),
            )
        )

        return paginate_query(query, page, per_page)

    @classmethod
    def get_pending_publish(cls):
        now = datetime.now()
        pending_id = cls._get_status_id("pending_publish")
        failed_id = cls._get_status_id("failed")
        status_ids = [sid for sid in [pending_id, failed_id] if sid]
        if not status_ids:
            return []
        return cls.model.query.filter(
            cls.model.status_id.in_(status_ids),
            cls.model.scheduled_at <= now
        ).order_by(cls.model.scheduled_at).all()

    @classmethod
    def get_by_status(cls, status_name):
        status_id = cls._get_status_id(status_name)
        if not status_id:
            return []
        return cls.model.query.filter(cls.model.status_id == status_id).order_by(cls.model.created_at.desc()).all()
