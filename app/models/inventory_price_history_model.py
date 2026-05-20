from sqlalchemy.sql import func

from app.database.session import db
from app.models.base import BaseModel


class InventoryPriceHistoryModel(BaseModel):
    __tablename__ = "inventory_price_history"

    id = db.Column(db.BigInteger, primary_key=True)
    inventory_id = db.Column(
        db.Integer,
        db.ForeignKey("inventory.id", ondelete="RESTRICT"),
        nullable=False
    )
    product_price_tracking_id = db.Column(
        db.Integer,
        db.ForeignKey("product_price_tracking.id", ondelete="RESTRICT"),
        nullable=False
    )
    price = db.Column(db.Numeric(10, 2), nullable=False)
    recorded_at = db.Column(
        db.TIMESTAMP,
        server_default=func.current_timestamp()
    )

    inventory = db.relationship(
        "InventoryModel",
        backref="price_history",
        lazy=True
    )
    product_price_tracking = db.relationship(
        "ProductPriceTrackingModel",
        backref="price_history",
        lazy=True
    )
