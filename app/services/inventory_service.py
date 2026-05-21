from flask import g
from sqlalchemy import text

from app.database.session import db
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
                ORDER BY f2.id
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
