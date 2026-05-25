from sqlalchemy.sql import func

from app.database.session import db
from app.models.base import BaseModel


class InventoryTagModel(BaseModel):
    __tablename__ = "inventory_tags"

    inventory_id = db.Column(
        db.Integer,
        db.ForeignKey("inventory.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False
    )
    tag_id = db.Column(
        db.Integer,
        db.ForeignKey("tags.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False
    )
    created_at = db.Column(db.TIMESTAMP, server_default=func.current_timestamp())

    tag = db.relationship("TagModel", lazy=True, overlaps="tags")
