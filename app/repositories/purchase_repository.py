from sqlalchemy import or_, cast, String
from sqlalchemy.orm import subqueryload

from flask import request, g

from app.models.entity_model import EntityModel
from app.models.file_model import FileModel
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
    order_by = (
        PurchaseModel.purchase_date.desc(),
        PurchaseModel.entity_id,
        PurchaseModel.total_amount,
    )
    create_fields = (
        "entity_id",
        "purchase_date",
        "delivery_date",
        "total_amount",
        "shipping_cost",
        "currency",
        "external_reference",
        "tracking_code",
        "shipping_status_id",
        "shipping_company_id",
        "user_id",
        "notes"
    )
    update_fields = create_fields

    @classmethod
    def get_paginated(cls, page, per_page):
        query = cls.model.query.options(
            subqueryload(cls.model.files).subqueryload(FileModel.file_type)
        ).order_by(*cls.order_by)
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

        try:
            date_from = request.args.get("date_from")
        except RuntimeError:
            date_from = None
        if date_from:
            query = query.filter(cls.model.purchase_date >= date_from)

        try:
            date_to = request.args.get("date_to")
        except RuntimeError:
            date_to = None
        if date_to:
            query = query.filter(cls.model.purchase_date <= date_to + " 23:59:59")

        try:
            entity_id = request.args.get("entity_id")
        except RuntimeError:
            entity_id = None
        if entity_id:
            try:
                query = query.filter(cls.model.entity_id == int(entity_id))
            except ValueError:
                pass

        try:
            shipping_status_id = request.args.get("shipping_status_id")
        except RuntimeError:
            shipping_status_id = None
        if shipping_status_id:
            ids = [int(x) for x in shipping_status_id.split(",") if x.strip().isdigit()]
            if ids:
                query = query.filter(cls.model.shipping_status_id.in_(ids))

        try:
            shipping_company_id = request.args.get("shipping_company_id")
        except RuntimeError:
            shipping_company_id = None
        if shipping_company_id:
            try:
                query = query.filter(cls.model.shipping_company_id == int(shipping_company_id))
            except ValueError:
                pass

        try:
            q = request.args.get("q")
        except RuntimeError:
            q = None
        if q:
            search = f"%{q}%"
            query = query.outerjoin(EntityModel, cls.model.entity_id == EntityModel.id)
            query = query.filter(
                or_(
                    cls.model.external_reference.ilike(search),
                    cls.model.tracking_code.ilike(search),
                    EntityModel.name.ilike(search),
                    cast(cls.model.purchase_date, String(19)).ilike(search),
                )
            )

        return paginate_query(query, page, per_page)
