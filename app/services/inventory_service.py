from flask import g
from sqlalchemy import and_, text

from app.database.session import db
from app.models.inventory_model import InventoryModel
from app.models.inventory_tag_model import InventoryTagModel
from app.models.product_model import ProductModel
from app.models.tag_model import TagModel
from app.repositories.inventory_repository import InventoryRepository
from app.services.crud_service import CrudService


def _is_admin():
    user = getattr(g, "current_user", None)
    if not user:
        return False
    return any(ur.role.name == "admin" for ur in getattr(user, "user_roles", []))


def _can_access(entity):
    if not entity:
        return False
    if _is_admin():
        return True
    user = getattr(g, "current_user", None)
    if not user:
        return False
    return entity.user_id == user.id


def _attach_price_data(items):
    inv_ids = [item.id for item in items if item.id]
    if not inv_ids:
        return
    ph = ",".join([f":iid_{i}" for i in range(len(inv_ids))])
    params = {f"iid_{i}": iid for i, iid in enumerate(inv_ids)}
    rows = db.session.execute(
        text(f"""
            SELECT iph.inventory_id, iph.price, iph.min_price, iph.max_price
            FROM inventory_price_history iph
            INNER JOIN (
                SELECT inventory_id, MAX(recorded_at) AS max_ra
                FROM inventory_price_history
                WHERE inventory_id IN ({ph})
                GROUP BY inventory_id
            ) latest ON iph.inventory_id = latest.inventory_id AND iph.recorded_at = latest.max_ra
        """),
        params
    ).mappings().all()
    for row in rows:
        inv_id = row["inventory_id"]
        item = next((it for it in items if it.id == inv_id), None)
        if item:
            item._current_price = float(row["price"]) if row["price"] is not None else None
            item._min_price = float(row["min_price"]) if row["min_price"] is not None else None
            item._max_price = float(row["max_price"]) if row["max_price"] is not None else None


def _attach_image_urls(items):
    product_items = []
    inv_item_map = {}
    for item in items:
        if item.product_id:
            product_items.append(item)
        inv_item_map.setdefault(item.id, item)

    if product_items:
        pids = list(set(it.product_id for it in product_items))
        ph = ",".join([f":pid_{i}" for i in range(len(pids))])
        params = {f"pid_{i}": pids[i] for i in range(len(pids))}
        rows = db.session.execute(
            text(f"""
                SELECT f2.product_id, f2.id AS file_id, f2.language_id
                FROM files f2
                WHERE f2.product_id IN ({ph})
                ORDER BY f2.id
            """),
            params
        ).mappings().all()
        prod_files = {}
        for row in rows:
            prod_files.setdefault(row["product_id"], []).append(row)
        for item in product_items:
            files = prod_files.get(item.product_id, [])
            if not files:
                continue
            inv_lang_id = item.language_id
            if inv_lang_id:
                matched = [f for f in files if f["language_id"] == inv_lang_id]
                if matched:
                    item._product_image_url = f"/api/product-catalog/files/{matched[0]['file_id']}/content"
                    continue
            item._product_image_url = f"/api/product-catalog/files/{files[0]['file_id']}/content"

    if inv_item_map:
        iids = list(inv_item_map.keys())
        ph = ",".join([f":iid_{i}" for i in range(len(iids))])
        params = {f"iid_{i}": iids[i] for i in range(len(iids))}
        rows = db.session.execute(
            text(f"""
                SELECT f2.inventory_id, f2.id AS file_id
                FROM files f2
                WHERE f2.inventory_id IN ({ph})
                ORDER BY f2.is_primary DESC, f2.sort_order ASC, f2.id ASC
            """),
            params
        ).mappings().all()
        seen = set()
        for row in rows:
            iid = row["inventory_id"]
            if iid not in seen:
                seen.add(iid)
                item = inv_item_map.get(iid)
                if item:
                    item._inventory_image_url = f"/api/product-catalog/files/{row['file_id']}/content"


class InventoryService(CrudService):
    repository = InventoryRepository

    @classmethod
    def get_paginated(cls, page, per_page):
        result = super().get_paginated(page, per_page)
        items = result.get("items", [])
        if items:
            _attach_image_urls(items)
            _attach_price_data(items)
        return result

    @classmethod
    def get_by_id(cls, entity_id):
        item = super().get_by_id(entity_id)
        if item:
            _attach_image_urls([item])
        return item

    @classmethod
    def create(cls, data):
        user = getattr(g, "current_user", None)
        if user:
            data["user_id"] = user.id
        return cls.repository.create(data)

    @classmethod
    def update(cls, entity_id, data):
        entity = cls.repository.get_by_id(entity_id)
        if not entity:
            return None
        if not _can_access(entity):
            return None
        return cls.repository.update(entity, data)

    @classmethod
    def delete(cls, entity_id):
        entity = cls.repository.get_by_id(entity_id)
        if not entity:
            return None
        if not _can_access(entity):
            return None
        cls.repository.delete(entity)
        return True

    @classmethod
    def bulk_create(cls, data):
        user = getattr(g, "current_user", None)
        if not user:
            return {"success": False, "error": "No authenticated user"}

        collection_id = data.get("collection_id")
        language_id = data.get("language_id")
        condition_id = data.get("condition_id")
        items = data.get("items", [])

        if not collection_id:
            return {"success": False, "error": "collection_id is required"}
        if not items:
            return {"success": False, "error": "items list is required"}

        # Resolve tag names — support both tag_name (legacy) and tag_names (array)
        tag_names = data.get("tag_names") or []
        if not tag_names and data.get("tag_name"):
            tag_names = [data.get("tag_name")]
        tag_names = [t.strip() for t in tag_names if t and t.strip()]

        tags = []
        for name in tag_names:
            tag = TagModel.query.filter(TagModel.name == name).first()
            if not tag:
                tag = TagModel(name=name)
                db.session.add(tag)
                db.session.flush()
            tags.append(tag)

        results = []
        for item in items:
            product_number = str(item.get("product_number", "")).strip()
            quantity = int(item.get("quantity", 1))

            if not product_number:
                results.append({"product_number": product_number, "status": "error", "error": "product_number is required"})
                continue

            product = ProductModel.query.filter(
                ProductModel.collection_id == collection_id,
                ProductModel.product_number == product_number
            ).first()

            if not product:
                results.append({"product_number": product_number, "status": "error", "error": "Product not found in collection"})
                continue

            lang_cond = [InventoryModel.product_id == product.id]
            if language_id:
                lang_cond.append(InventoryModel.language_id == int(language_id))
            else:
                lang_cond.append(InventoryModel.language_id.is_(None))
            if condition_id:
                lang_cond.append(InventoryModel.condition_id == int(condition_id))
            else:
                lang_cond.append(InventoryModel.condition_id.is_(None))

            # Look for existing entry with same product + language + condition + tags
            requested_tag_ids = {t.id for t in tags}
            existing = None
            for candidate in InventoryModel.query.filter(and_(*lang_cond)).all():
                candidate_tag_ids = {t.id for t in candidate.tags}
                if candidate_tag_ids == requested_tag_ids:
                    existing = candidate
                    break

            if existing:
                existing.quantity = (existing.quantity or 0) + quantity
                results.append({
                    "product_number": product_number,
                    "product_id": product.id,
                    "status": "updated",
                    "inventory_id": existing.id,
                    "total_quantity": existing.quantity
                })
            else:
                new_entry = InventoryModel(
                    product_id=product.id,
                    collection_id=collection_id,
                    quantity=quantity,
                    user_id=user.id
                )
                if language_id:
                    new_entry.language_id = int(language_id)
                if condition_id:
                    new_entry.condition_id = int(condition_id)
                db.session.add(new_entry)
                db.session.flush()

                for t in tags:
                    db.session.add(InventoryTagModel(inventory_id=new_entry.id, tag_id=t.id))
                results.append({
                    "product_number": product_number,
                    "product_id": product.id,
                    "status": "created",
                    "inventory_id": new_entry.id,
                    "total_quantity": quantity
                })

        db.session.commit()
        return {"success": True, "results": results}
