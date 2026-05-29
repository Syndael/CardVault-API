from sqlalchemy.sql import func

from app.database.session import db
from app.models.base import BaseModel


class InventoryUrlModel(BaseModel):
    __tablename__ = "inventory_urls"

    id = db.Column(db.Integer, primary_key=True)
    inventory_id = db.Column(
        db.Integer,
        db.ForeignKey("inventory.id", ondelete="CASCADE"),
        nullable=False
    )
    url = db.Column(db.String(500), nullable=False)
    name = db.Column(db.String(255))
    created_at = db.Column(
        db.TIMESTAMP,
        server_default=func.current_timestamp()
    )

    inventory = db.relationship("InventoryModel", backref="urls", lazy=True)
