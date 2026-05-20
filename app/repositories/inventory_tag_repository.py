from app.database.session import db
from app.models.inventory_tag_model import InventoryTagModel


class InventoryTagRepository:

    @staticmethod
    def get_by_inventory(inventory_id: int):
        return (
            InventoryTagModel.query
            .filter_by(inventory_id=inventory_id)
            .all()
        )

    @staticmethod
    def get(inventory_id: int, tag_id: int):
        return InventoryTagModel.query.get((inventory_id, tag_id))

    @staticmethod
    def create(inventory_id: int, tag_id: int) -> InventoryTagModel:
        entry = InventoryTagModel(inventory_id=inventory_id, tag_id=tag_id)
        db.session.add(entry)
        db.session.commit()
        return entry

    @staticmethod
    def delete(entry: InventoryTagModel):
        db.session.delete(entry)
        db.session.commit()
