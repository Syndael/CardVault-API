from collections import defaultdict

from flask import g
from sqlalchemy import func as sa_func, text

from app.database.session import db
from app.models.collection_model import CollectionModel
from app.models.collection_translation_model import CollectionTranslationModel
from app.models.entity_model import EntityModel
from app.models.inventory_model import InventoryModel
from app.models.inventory_price_history_model import InventoryPriceHistoryModel
from app.models.product_model import ProductModel
from app.models.product_translation_model import ProductTranslationModel
from app.models.purchase_item_model import PurchaseItemModel
from app.models.purchase_model import PurchaseModel
from app.models.type_model import TypeModel


def _is_admin():
    user = getattr(g, "current_user", None)
    if not user:
        return False
    return any(ur.role.name == "admin" for ur in getattr(user, "user_roles", []))


def _user_filter(query, model, user_id_col="user_id"):
    if _is_admin():
        return query
    user = getattr(g, "current_user", None)
    if user:
        return query.filter(getattr(model, user_id_col) == user.id)
    return query.filter(text("1=0"))


def summary():
    user = getattr(g, "current_user", None)
    is_admin = _is_admin()

    total_inventory = _user_filter(
        db.session.query(sa_func.coalesce(sa_func.sum(InventoryModel.quantity), 0)),
        InventoryModel
    ).scalar()

    total_products = _user_filter(
        db.session.query(sa_func.count(InventoryModel.id.distinct())),
        InventoryModel
    ).scalar()

    total_purchases = _user_filter(
        db.session.query(sa_func.count(PurchaseModel.id)),
        PurchaseModel
    ).scalar()

    total_purchase_amount = _user_filter(
        db.session.query(sa_func.coalesce(sa_func.sum(PurchaseModel.total_amount), 0)),
        PurchaseModel
    ).scalar()

    total_shipping = _user_filter(
        db.session.query(sa_func.coalesce(sa_func.sum(PurchaseModel.shipping_cost), 0)),
        PurchaseModel
    ).scalar()

    total_commission = _user_filter(
        db.session.query(sa_func.coalesce(sa_func.sum(PurchaseModel.commission), 0)),
        PurchaseModel
    ).scalar()

    price_tracked = db.session.query(
        sa_func.count(InventoryPriceHistoryModel.inventory_id.distinct())
    ).scalar()

    latest_price_subq = (
        db.session.query(
            InventoryPriceHistoryModel.inventory_id,
            InventoryPriceHistoryModel.price,
            sa_func.row_number().over(
                partition_by=InventoryPriceHistoryModel.inventory_id,
                order_by=InventoryPriceHistoryModel.recorded_at.desc(),
            ).label("rn"),
        )
        .subquery()
    )
    latest_price_subq = (
        db.session.query(latest_price_subq)
        .filter(latest_price_subq.c.rn == 1)
        .subquery()
    )

    balance_query = db.session.query(
        sa_func.coalesce(sa_func.sum(latest_price_subq.c.price * InventoryModel.quantity), 0)
    ).select_from(InventoryModel).outerjoin(
        latest_price_subq,
        latest_price_subq.c.inventory_id == InventoryModel.id,
    )

    if not is_admin and user:
        balance_query = balance_query.filter(InventoryModel.user_id == user.id)
    elif not is_admin:
        balance_query = balance_query.filter(text("1=0"))

    total_balance = balance_query.scalar()

    return {
        "total_inventory_items": int(total_inventory),
        "total_products": int(total_products),
        "total_purchases": int(total_purchases),
        "total_purchase_amount": float(total_purchase_amount),
        "total_shipping_costs": float(total_shipping),
        "total_commission": float(total_commission),
        "total_spent": float(total_purchase_amount) + float(total_shipping) + float(total_commission),
        "total_balance": float(total_balance),
        "price_tracked_items": int(price_tracked),
    }


def inventory_value_by_type():
    user = getattr(g, "current_user", None)
    is_admin = _is_admin()

    latest_price_subq = (
        db.session.query(
            InventoryPriceHistoryModel.inventory_id,
            InventoryPriceHistoryModel.price,
            sa_func.row_number().over(
                partition_by=InventoryPriceHistoryModel.inventory_id,
                order_by=InventoryPriceHistoryModel.recorded_at.desc(),
            ).label("rn"),
        )
        .subquery()
    )
    latest_price_subq = (
        db.session.query(latest_price_subq)
        .filter(latest_price_subq.c.rn == 1)
        .subquery()
    )

    query = db.session.query(
        TypeModel.id.label("type_id"),
        TypeModel.name.label("type_name"),
        TypeModel.short_name.label("type_short"),
        sa_func.count(InventoryModel.id).label("item_count"),
        sa_func.coalesce(sa_func.sum(InventoryModel.quantity), 0).label("total_quantity"),
        sa_func.coalesce(sa_func.sum(PurchaseItemModel.unit_price * InventoryModel.quantity / sa_func.coalesce(PurchaseItemModel.split_quantity, 1)), 0).label("acquisition_value"),
        sa_func.coalesce(sa_func.sum(latest_price_subq.c.price * InventoryModel.quantity), 0).label("current_value"),
    ).select_from(InventoryModel)
    query = query.join(ProductModel, InventoryModel.product_id == ProductModel.id)
    query = query.join(TypeModel, ProductModel.product_type_id == TypeModel.id)
    query = query.outerjoin(PurchaseItemModel, InventoryModel.purchase_item_id == PurchaseItemModel.id)
    query = query.outerjoin(
        latest_price_subq,
        latest_price_subq.c.inventory_id == InventoryModel.id,
    )

    if not is_admin and user:
        query = query.filter(InventoryModel.user_id == user.id)
    elif not is_admin:
        query = query.filter(text("1=0"))

    query = query.group_by(TypeModel.id, TypeModel.name, TypeModel.short_name)
    query = query.order_by(sa_func.sum(PurchaseItemModel.unit_price * InventoryModel.quantity / sa_func.coalesce(PurchaseItemModel.split_quantity, 1)).desc())

    rows = query.all()
    total_acq = sum(float(r.acquisition_value) for r in rows)
    total_cur = sum(float(r.current_value) for r in rows)
    total_qty = sum(int(r.total_quantity) for r in rows)

    types = []
    for r in rows:
        types.append({
            "type_id": r.type_id,
            "type_name": r.type_name,
            "type_short": r.type_short,
            "item_count": int(r.item_count),
            "total_quantity": int(r.total_quantity),
            "acquisition_value": float(r.acquisition_value),
            "current_value": float(r.current_value),
            "percentage": round(float(r.acquisition_value) / total_acq * 100, 1) if total_acq else 0,
        })

    return {
        "types": types,
        "total_acquisition": float(total_acq),
        "total_current": float(total_cur),
        "total_quantity": int(total_qty),
    }


def inventory_value_detail():
    user = getattr(g, "current_user", None)
    is_admin = _is_admin()

    cols = [
        InventoryModel.id.label("inv_id"),
        InventoryModel.quantity,
        CollectionModel.code.label("col_code"),
        ProductModel.product_number,
        TypeModel.name.label("type_name"),
        TypeModel.short_name.label("type_short"),
        (PurchaseItemModel.unit_price / sa_func.coalesce(PurchaseItemModel.split_quantity, 1)).label("unit_price"),
        PurchaseItemModel.quantity.label("item_qty"),
    ]

    query = db.session.query(*cols).select_from(InventoryModel)
    query = query.join(ProductModel, InventoryModel.product_id == ProductModel.id)
    query = query.join(TypeModel, ProductModel.product_type_id == TypeModel.id)
    query = query.join(CollectionModel, InventoryModel.collection_id == CollectionModel.id)
    query = query.outerjoin(PurchaseItemModel, InventoryModel.purchase_item_id == PurchaseItemModel.id)

    if not is_admin and user:
        query = query.filter(InventoryModel.user_id == user.id)
    elif not is_admin:
        query = query.filter(text("1=0"))

    latest_price_subq = (
        db.session.query(
            InventoryPriceHistoryModel.inventory_id,
            InventoryPriceHistoryModel.price,
            InventoryPriceHistoryModel.recorded_at,
            sa_func.row_number().over(
                partition_by=InventoryPriceHistoryModel.inventory_id,
                order_by=InventoryPriceHistoryModel.recorded_at.desc(),
            ).label("rn"),
        )
        .subquery()
    )

    latest_price_subq = (
        db.session.query(latest_price_subq)
        .filter(latest_price_subq.c.rn == 1)
        .subquery()
    )

    query = query.outerjoin(
        latest_price_subq,
        latest_price_subq.c.inventory_id == InventoryModel.id,
    )

    pt_subq = (
        db.session.query(
            ProductTranslationModel.name,
            ProductTranslationModel.product_id,
        )
        .where(ProductTranslationModel.id.in_(
            db.session.query(sa_func.min(ProductTranslationModel.id))
            .group_by(ProductTranslationModel.product_id)
        ))
        .subquery()
    )

    ct_subq = (
        db.session.query(
            CollectionTranslationModel.name,
            CollectionTranslationModel.collection_id,
        )
        .where(CollectionTranslationModel.id.in_(
            db.session.query(sa_func.min(CollectionTranslationModel.id))
            .group_by(CollectionTranslationModel.collection_id)
        ))
        .subquery()
    )

    query = query.outerjoin(pt_subq, pt_subq.c.product_id == ProductModel.id)
    query = query.outerjoin(ct_subq, ct_subq.c.collection_id == CollectionModel.id)

    rows = query.all()

    items = []
    for r in rows:
        acq = float(r.unit_price) if r.unit_price else None
        current = float(r.price) if r.price is not None else None
        items.append({
            "inv_id": r.inv_id,
            "quantity": int(r.quantity),
            "collection_code": r.col_code,
            "product_number": r.product_number,
            "type_name": r.type_name,
            "acquisition_price": acq,
            "current_price": current,
            "acquisition_total": round(acq * int(r.quantity), 2) if acq else None,
            "current_total": round(current * int(r.quantity), 2) if current else None,
        })

    total_acq = sum(i["acquisition_total"] or 0 for i in items)
    total_cur = sum(i["current_total"] or 0 for i in items)
    total_diff = round(total_cur - total_acq, 2)

    return {
        "items": items,
        "total_acquisition": round(total_acq, 2),
        "total_current": round(total_cur, 2),
        "total_difference": total_diff,
    }


def collections_top(limit=20):
    user = getattr(g, "current_user", None)
    is_admin = _is_admin()

    from app.models.language_model import LanguageModel

    latest_price_subq = (
        db.session.query(
            InventoryPriceHistoryModel.inventory_id,
            InventoryPriceHistoryModel.price,
            sa_func.row_number().over(
                partition_by=InventoryPriceHistoryModel.inventory_id,
                order_by=InventoryPriceHistoryModel.recorded_at.desc(),
            ).label("rn"),
        )
        .subquery()
    )
    latest_price_subq = (
        db.session.query(latest_price_subq)
        .filter(latest_price_subq.c.rn == 1)
        .subquery()
    )

    trans_subq = (
        db.session.query(
            CollectionTranslationModel.name,
            CollectionTranslationModel.collection_id,
            sa_func.row_number().over(
                partition_by=CollectionTranslationModel.collection_id,
                order_by=sa_func.coalesce(LanguageModel.priority_order, 999).asc(),
            ).label("rn"),
        )
        .join(LanguageModel, CollectionTranslationModel.language_id == LanguageModel.id, isouter=True)
        .subquery()
    )
    trans_subq = (
        db.session.query(trans_subq)
        .filter(trans_subq.c.rn == 1)
        .subquery()
    )

    cols = [
        CollectionModel.id.label("col_id"),
        CollectionModel.code,
        sa_func.count(InventoryModel.id).label("item_count"),
        sa_func.coalesce(sa_func.sum(InventoryModel.quantity), 0).label("total_qty"),
        trans_subq.c.name.label("col_name"),
        sa_func.coalesce(sa_func.sum(PurchaseItemModel.unit_price * InventoryModel.quantity / sa_func.coalesce(PurchaseItemModel.split_quantity, 1)), 0).label("acquisition_cost"),
        sa_func.coalesce(sa_func.sum(latest_price_subq.c.price * InventoryModel.quantity), 0).label("current_value"),
    ]

    query = db.session.query(*cols).select_from(CollectionModel)
    query = query.join(InventoryModel, InventoryModel.collection_id == CollectionModel.id)
    query = query.outerjoin(
        trans_subq,
        trans_subq.c.collection_id == CollectionModel.id,
    )
    query = query.outerjoin(
        PurchaseItemModel,
        PurchaseItemModel.id == InventoryModel.purchase_item_id,
    )
    query = query.outerjoin(
        latest_price_subq,
        latest_price_subq.c.inventory_id == InventoryModel.id,
    )

    if not is_admin and user:
        query = query.filter(InventoryModel.user_id == user.id)
    elif not is_admin:
        query = query.filter(text("1=0"))

    query = query.group_by(CollectionModel.id, CollectionModel.code, trans_subq.c.name)
    query = query.order_by(sa_func.count(InventoryModel.id).desc())
    query = query.limit(limit)

    rows = query.all()

    return [
        {
            "collection_id": r.col_id,
            "code": r.code,
            "name": r.col_name or r.code,
            "item_count": int(r.item_count),
            "total_quantity": int(r.total_qty),
            "acquisition_cost": float(r.acquisition_cost),
            "current_value": float(r.current_value),
        }
        for r in rows
    ]


def purchases_by_entity():
    user = getattr(g, "current_user", None)
    is_admin = _is_admin()

    def _entity_query(parent_col=None):
        if parent_col:
            entity_expr = parent_col
        else:
            entity_expr = EntityModel.id

        cols = [
            entity_expr.label("entity_id"),
            EntityModel.name,
            EntityModel.parent_id,
            sa_func.count(PurchaseModel.id).label("purchase_count"),
            sa_func.coalesce(sa_func.sum(PurchaseModel.total_amount), 0).label("total_amount"),
            sa_func.coalesce(sa_func.sum(PurchaseModel.shipping_cost), 0).label("total_shipping"),
            sa_func.coalesce(sa_func.sum(PurchaseModel.commission), 0).label("total_commission"),
        ]
        query = db.session.query(*cols).select_from(EntityModel)
        query = query.join(PurchaseModel, PurchaseModel.entity_id == entity_expr)

        if not is_admin and user:
            query = query.filter(PurchaseModel.user_id == user.id)
        elif not is_admin:
            query = query.filter(text("1=0"))

        query = query.group_by(entity_expr, EntityModel.name, EntityModel.parent_id)
        query = query.order_by(EntityModel.name.asc())
        return query.all()

    entities = _entity_query()

    # Group by parent
    parent_children = defaultdict(list)
    for e in entities:
        pid = e.parent_id
        if pid:
            parent_children[pid].append(e)

    entity_map = {e.entity_id: e for e in entities}

    children_value = defaultdict(lambda: {"count": 0, "amount": 0.0, "shipping": 0.0, "commission": 0.0})
    for pid, children in parent_children.items():
        for c in children:
            children_value[pid]["count"] += int(c.purchase_count)
            children_value[pid]["amount"] += float(c.total_amount)
            children_value[pid]["shipping"] += float(c.total_shipping)
            children_value[pid]["commission"] += float(c.total_commission)

    result = []
    for e in entities:
        if e.parent_id:
            continue

        cv = children_value.get(e.entity_id, {})
        total_count = int(e.purchase_count) + cv.get("count", 0)
        total_amount = float(e.total_amount) + cv.get("amount", 0.0)
        total_shipping = float(e.total_shipping) + cv.get("shipping", 0.0)
        total_commission = float(e.total_commission) + cv.get("commission", 0.0)

        children_list = []
        child_entities = parent_children.get(e.entity_id, [])
        for child in child_entities:
            children_list.append({
                "entity_id": child.entity_id,
                "name": child.name,
                "purchase_count": int(child.purchase_count),
                "total_amount": float(child.total_amount),
                "total_shipping": float(child.total_shipping),
                "total_commission": float(child.total_commission),
            })

        result.append({
            "entity_id": e.entity_id,
            "name": e.name,
            "purchase_count": total_count,
            "total_amount": round(total_amount, 2),
            "total_shipping": round(total_shipping, 2),
            "total_commission": round(total_commission, 2),
            "total_spent": round(total_amount + total_shipping + total_commission, 2),
            "children": children_list,
        })

    total = sum(r["total_spent"] for r in result)
    return {"entities": result, "total_spent": round(total, 2)}


def purchases_by_month():
    user = getattr(g, "current_user", None)
    is_admin = _is_admin()

    cols = [
        sa_func.date_format(PurchaseModel.purchase_date, "%Y-%m").label("month"),
        sa_func.count(PurchaseModel.id).label("count"),
        sa_func.coalesce(sa_func.sum(PurchaseModel.total_amount), 0).label("total_amount"),
        sa_func.coalesce(sa_func.sum(PurchaseModel.shipping_cost), 0).label("total_shipping"),
        sa_func.coalesce(sa_func.sum(PurchaseModel.commission), 0).label("total_commission"),
    ]

    query = db.session.query(*cols).select_from(PurchaseModel)
    query = query.filter(PurchaseModel.purchase_date.isnot(None))

    if not is_admin and user:
        query = query.filter(PurchaseModel.user_id == user.id)
    elif not is_admin:
        query = query.filter(text("1=0"))

    query = query.group_by(text("month"))
    query = query.order_by(text("month desc"))

    rows = query.all()

    months = []
    for r in rows:
        months.append({
            "month": r.month,
            "count": int(r.count),
            "total_amount": float(r.total_amount),
            "total_shipping": float(r.total_shipping),
            "total_commission": float(r.total_commission),
            "total_spent": float(r.total_amount) + float(r.total_shipping) + float(r.total_commission),
        })

    return months


def language_distribution():
    user = getattr(g, "current_user", None)
    is_admin = _is_admin()

    from app.models.language_model import LanguageModel

    cols = [
        LanguageModel.id.label("lang_id"),
        LanguageModel.name.label("lang_name"),
        sa_func.count(InventoryModel.id).label("item_count"),
        sa_func.coalesce(sa_func.sum(InventoryModel.quantity), 0).label("total_qty"),
    ]

    query = db.session.query(*cols).select_from(InventoryModel)
    query = query.join(LanguageModel, InventoryModel.language_id == LanguageModel.id, isouter=True)

    if not is_admin and user:
        query = query.filter(InventoryModel.user_id == user.id)
    elif not is_admin:
        query = query.filter(text("1=0"))

    query = query.group_by(LanguageModel.id, LanguageModel.name)
    query = query.order_by(sa_func.count(InventoryModel.id).desc())

    rows = query.all()
    total = sum(int(r.item_count) for r in rows)

    return [
        {
            "language_id": r.lang_id,
            "language_name": r.lang_name or "(sin idioma)",
            "item_count": int(r.item_count),
            "total_quantity": int(r.total_qty),
            "percentage": round(int(r.item_count) / total * 100, 1) if total else 0,
        }
        for r in rows
    ]


def condition_distribution():
    user = getattr(g, "current_user", None)
    is_admin = _is_admin()

    from app.models.product_condition_model import ProductConditionModel

    cols = [
        ProductConditionModel.id.label("cond_id"),
        ProductConditionModel.name.label("cond_name"),
        sa_func.count(InventoryModel.id).label("item_count"),
        sa_func.coalesce(sa_func.sum(InventoryModel.quantity), 0).label("total_qty"),
    ]

    query = db.session.query(*cols).select_from(InventoryModel)
    query = query.join(ProductConditionModel, InventoryModel.condition_id == ProductConditionModel.id, isouter=True)

    if not is_admin and user:
        query = query.filter(InventoryModel.user_id == user.id)
    elif not is_admin:
        query = query.filter(text("1=0"))

    query = query.group_by(ProductConditionModel.id, ProductConditionModel.name)
    query = query.order_by(sa_func.count(InventoryModel.id).desc())

    rows = query.all()
    total = sum(int(r.item_count) for r in rows)

    return [
        {
            "condition_id": r.cond_id,
            "condition_name": r.cond_name or "(sin estado)",
            "item_count": int(r.item_count),
            "total_quantity": int(r.total_qty),
            "percentage": round(int(r.item_count) / total * 100, 1) if total else 0,
        }
        for r in rows
    ]


def _latest_price_subq():
    q = db.session.query(
        InventoryPriceHistoryModel.inventory_id,
        InventoryPriceHistoryModel.price,
        sa_func.row_number().over(
            partition_by=InventoryPriceHistoryModel.inventory_id,
            order_by=InventoryPriceHistoryModel.recorded_at.desc(),
        ).label("rn"),
    ).subquery()
    return db.session.query(q).filter(q.c.rn == 1).subquery()


def _best_translation_subq(model, fk_col, lang_model, order_col):
    q = db.session.query(
        model.name,
        fk_col,
        sa_func.row_number().over(
            partition_by=fk_col,
            order_by=sa_func.coalesce(order_col, 999).asc(),
        ).label("rn"),
    ).join(lang_model, model.language_id == lang_model.id, isouter=True).subquery()
    return db.session.query(q).filter(q.c.rn == 1).subquery()


def top_valuable_items(limit=10):
    user = getattr(g, "current_user", None)
    is_admin = _is_admin()
    from app.models.language_model import LanguageModel

    latest = _latest_price_subq()
    pt = _best_translation_subq(ProductTranslationModel, ProductTranslationModel.product_id, LanguageModel, LanguageModel.priority_order)

    query = db.session.query(
        InventoryModel.id.label("inv_id"),
        InventoryModel.quantity,
        ProductModel.product_number,
        CollectionModel.code.label("col_code"),
        pt.c.name.label("product_name"),
        TypeModel.short_name.label("type_short"),
        latest.c.price,
        (latest.c.price * InventoryModel.quantity).label("total_value"),
    ).select_from(InventoryModel)
    query = query.join(ProductModel, InventoryModel.product_id == ProductModel.id)
    query = query.join(TypeModel, ProductModel.product_type_id == TypeModel.id)
    query = query.join(CollectionModel, InventoryModel.collection_id == CollectionModel.id)
    query = query.outerjoin(latest, latest.c.inventory_id == InventoryModel.id)
    query = query.outerjoin(pt, pt.c.product_id == ProductModel.id)

    if not is_admin and user:
        query = query.filter(InventoryModel.user_id == user.id)
    elif not is_admin:
        query = query.filter(text("1=0"))

    query = query.filter(latest.c.price.isnot(None))
    query = query.order_by((latest.c.price * InventoryModel.quantity).desc())
    query = query.limit(limit)

    rows = query.all()
    return [
        {
            "inv_id": r.inv_id,
            "quantity": int(r.quantity),
            "product_number": r.product_number,
            "collection_code": r.col_code,
            "product_name": r.product_name or "",
            "type": r.type_short or "",
            "unit_price": float(r.price),
            "total_value": float(r.total_value),
        }
        for r in rows
    ]


def top_profit_items(limit=10):
    user = getattr(g, "current_user", None)
    is_admin = _is_admin()
    from app.models.language_model import LanguageModel

    latest = _latest_price_subq()
    pt = _best_translation_subq(ProductTranslationModel, ProductTranslationModel.product_id, LanguageModel, LanguageModel.priority_order)

    query = db.session.query(
        InventoryModel.id.label("inv_id"),
        InventoryModel.quantity,
        ProductModel.product_number,
        CollectionModel.code.label("col_code"),
        pt.c.name.label("product_name"),
        TypeModel.short_name.label("type_short"),
        (PurchaseItemModel.unit_price / sa_func.coalesce(PurchaseItemModel.split_quantity, 1)).label("unit_price"),
        latest.c.price,
        (sa_func.coalesce(latest.c.price, 0) - sa_func.coalesce(PurchaseItemModel.unit_price / sa_func.coalesce(PurchaseItemModel.split_quantity, 1), 0)).label("unit_profit"),
        ((sa_func.coalesce(latest.c.price, 0) - sa_func.coalesce(PurchaseItemModel.unit_price / sa_func.coalesce(PurchaseItemModel.split_quantity, 1), 0)) * InventoryModel.quantity).label("total_profit"),
    ).select_from(InventoryModel)
    query = query.join(ProductModel, InventoryModel.product_id == ProductModel.id)
    query = query.join(TypeModel, ProductModel.product_type_id == TypeModel.id)
    query = query.join(CollectionModel, InventoryModel.collection_id == CollectionModel.id)
    query = query.outerjoin(PurchaseItemModel, InventoryModel.purchase_item_id == PurchaseItemModel.id)
    query = query.outerjoin(latest, latest.c.inventory_id == InventoryModel.id)
    query = query.outerjoin(pt, pt.c.product_id == ProductModel.id)

    if not is_admin and user:
        query = query.filter(InventoryModel.user_id == user.id)
    elif not is_admin:
        query = query.filter(text("1=0"))

    query = query.filter(PurchaseItemModel.unit_price.isnot(None))
    query = query.filter(latest.c.price.isnot(None))
    query = query.order_by(((sa_func.coalesce(latest.c.price, 0) - sa_func.coalesce(PurchaseItemModel.unit_price / sa_func.coalesce(PurchaseItemModel.split_quantity, 1), 0)) * InventoryModel.quantity).desc())
    query = query.limit(limit)

    rows = query.all()
    return [
        {
            "inv_id": r.inv_id,
            "quantity": int(r.quantity),
            "product_number": r.product_number,
            "collection_code": r.col_code,
            "product_name": r.product_name or "",
            "type": r.type_short or "",
            "unit_price": float(r.unit_price) if r.unit_price else 0,
            "current_price": float(r.price) if r.price else 0,
            "unit_profit": float(r.unit_profit),
            "total_profit": float(r.total_profit),
        }
        for r in rows
    ]


def untracked_items():
    user = getattr(g, "current_user", None)
    is_admin = _is_admin()

    query = db.session.query(
        InventoryModel.id.label("inv_id"),
        InventoryModel.quantity,
        ProductModel.product_number,
        CollectionModel.code.label("col_code"),
    ).select_from(InventoryModel)
    query = query.join(ProductModel, InventoryModel.product_id == ProductModel.id)
    query = query.join(CollectionModel, InventoryModel.collection_id == CollectionModel.id)
    query = query.outerjoin(InventoryPriceHistoryModel, InventoryPriceHistoryModel.inventory_id == InventoryModel.id)
    query = query.filter(InventoryPriceHistoryModel.id.is_(None))

    if not is_admin and user:
        query = query.filter(InventoryModel.user_id == user.id)
    elif not is_admin:
        query = query.filter(text("1=0"))

    query = query.order_by(InventoryModel.id)
    rows = query.all()

    return [
        {
            "inv_id": r.inv_id,
            "quantity": int(r.quantity),
            "product_number": r.product_number,
            "collection_code": r.col_code,
        }
        for r in rows
    ]


def avg_monthly_spending():
    user = getattr(g, "current_user", None)
    is_admin = _is_admin()

    cols = [
        sa_func.date_format(PurchaseModel.purchase_date, "%Y-%m").label("month"),
        sa_func.avg(PurchaseModel.total_amount + sa_func.coalesce(PurchaseModel.shipping_cost, 0) + sa_func.coalesce(PurchaseModel.commission, 0)).label("avg_spent"),
        sa_func.count(PurchaseModel.id).label("count"),
        sa_func.coalesce(sa_func.sum(PurchaseModel.total_amount), 0).label("total_amount"),
        sa_func.coalesce(sa_func.sum(PurchaseModel.shipping_cost), 0).label("total_shipping"),
        sa_func.coalesce(sa_func.sum(PurchaseModel.commission), 0).label("total_commission"),
    ]

    query = db.session.query(*cols).select_from(PurchaseModel)
    query = query.filter(PurchaseModel.purchase_date.isnot(None))

    if not is_admin and user:
        query = query.filter(PurchaseModel.user_id == user.id)
    elif not is_admin:
        query = query.filter(text("1=0"))

    query = query.group_by(text("month"))
    query = query.order_by(text("month desc"))

    rows = query.all()
    return [
        {
            "month": r.month,
            "count": int(r.count),
            "avg_spent": round(float(r.avg_spent), 2),
            "total_amount": float(r.total_amount),
            "total_shipping": float(r.total_shipping),
            "total_commission": float(r.total_commission),
        }
        for r in rows
    ]


def best_investment_entities(limit=None):
    user = getattr(g, "current_user", None)
    is_admin = _is_admin()

    latest = _latest_price_subq()

    query = db.session.query(
        EntityModel.id.label("entity_id"),
        EntityModel.name,
        sa_func.count(InventoryModel.id).label("items_count"),
        sa_func.coalesce(sa_func.sum(PurchaseItemModel.unit_price * InventoryModel.quantity / sa_func.coalesce(PurchaseItemModel.split_quantity, 1)), 0).label("acquisition_cost"),
        sa_func.coalesce(sa_func.sum(latest.c.price * InventoryModel.quantity), 0).label("current_value"),
    ).select_from(EntityModel)
    query = query.join(PurchaseModel, PurchaseModel.entity_id == EntityModel.id)
    query = query.join(PurchaseItemModel, PurchaseItemModel.purchase_id == PurchaseModel.id)
    query = query.join(InventoryModel, InventoryModel.purchase_item_id == PurchaseItemModel.id)
    query = query.outerjoin(latest, latest.c.inventory_id == InventoryModel.id)

    if not is_admin and user:
        query = query.filter(PurchaseModel.user_id == user.id)
    elif not is_admin:
        query = query.filter(text("1=0"))

    query = query.group_by(EntityModel.id, EntityModel.name)
    query = query.order_by((sa_func.coalesce(sa_func.sum(latest.c.price * InventoryModel.quantity), 0) - sa_func.coalesce(sa_func.sum(PurchaseItemModel.unit_price * InventoryModel.quantity / sa_func.coalesce(PurchaseItemModel.split_quantity, 1)), 0)).desc())
    if limit is not None:
        query = query.limit(limit)

    rows = query.all()
    result = []
    for r in rows:
        diff = float(r.current_value) - float(r.acquisition_cost)
        pct = round(diff / float(r.acquisition_cost) * 100, 1) if float(r.acquisition_cost) else 0
        result.append({
            "entity_id": r.entity_id,
            "name": r.name,
            "items_count": int(r.items_count),
            "acquisition_cost": float(r.acquisition_cost),
            "current_value": float(r.current_value),
            "profit": round(diff, 2),
            "profit_pct": pct,
        })
    return result
