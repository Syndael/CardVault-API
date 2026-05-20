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
