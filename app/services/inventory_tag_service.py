from app.database.session import db
from app.models.inventory_model import InventoryModel
from app.models.inventory_tag_model import InventoryTagModel
from app.models.tag_model import TagModel
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.inventory_tag_repository import InventoryTagRepository
from app.repositories.tag_repository import TagRepository


class InventoryTagService:

    @staticmethod
    def get_by_inventory(inventory_id: int):
        return InventoryTagRepository.get_by_inventory(inventory_id)

    @staticmethod
    def add(inventory_id: int, tag_id: int):
        if not InventoryRepository.get_by_id(inventory_id):
            return None, "inventory_not_found"
        if not TagRepository.get_by_id(tag_id):
            return None, "tag_not_found"
        existing = InventoryTagRepository.get(inventory_id, tag_id)
        if existing:
            return existing, "already_exists"
        entry = InventoryTagRepository.create(inventory_id, tag_id)
        return entry, None

    @staticmethod
    def remove(inventory_id: int, tag_id: int):
        entry = InventoryTagRepository.get(inventory_id, tag_id)
        if not entry:
            return False
        InventoryTagRepository.delete(entry)
        return True

    @staticmethod
    def batch_tags(inventory_ids: list[int], tag_ids: list[int], action: str):
        affected = 0
        skipped = 0
        errors = []

        inv_entries = InventoryModel.query.filter(InventoryModel.id.in_(inventory_ids)).all()
        inv_map = {inv.id: inv for inv in inv_entries}
        tags = TagModel.query.filter(TagModel.id.in_(tag_ids)).all() if tag_ids else []
        for inv_id in inventory_ids:
            inv = inv_map.get(inv_id)
            if not inv:
                skipped += 1
                continue

            if action == "set":
                InventoryTagModel.query.filter_by(inventory_id=inv_id).delete()
                for t in tags:
                    db.session.add(InventoryTagModel(inventory_id=inv_id, tag_id=t.id))
                affected += 1

            elif action == "remove":
                if not tag_ids:
                    skipped += 1
                    continue
                existing_ids = {row.tag_id for row in InventoryTagModel.query.filter_by(inventory_id=inv_id).all()}
                to_remove = existing_ids & set(tag_ids)
                if to_remove:
                    InventoryTagModel.query.filter(
                        InventoryTagModel.inventory_id == inv_id,
                        InventoryTagModel.tag_id.in_(to_remove)
                    ).delete(synchronize_session=False)
                    affected += 1
                else:
                    skipped += 1

            elif action == "add":
                if not tag_ids:
                    skipped += 1
                    continue
                existing_ids = {row.tag_id for row in InventoryTagModel.query.filter_by(inventory_id=inv_id).all()}
                added_any = False
                for t in tags:
                    if t.id not in existing_ids:
                        db.session.add(InventoryTagModel(inventory_id=inv_id, tag_id=t.id))
                        added_any = True
                if added_any:
                    affected += 1
                else:
                    skipped += 1

        db.session.commit()
        return {
            "success": True,
            "affected": affected,
            "skipped": skipped,
            "errors": errors
        }
