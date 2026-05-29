from sqlalchemy.sql import func

from app.database.session import db
from app.models.base import BaseModel


class InventoryPriceHistoryArchiveModel(BaseModel):
    __tablename__ = "inventory_price_history_archive"

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
    min_price = db.Column(db.Numeric(10, 2), nullable=True)
    max_price = db.Column(db.Numeric(10, 2), nullable=True)
    min_price_recorded_at = db.Column(db.TIMESTAMP, nullable=True)
    max_price_recorded_at = db.Column(db.TIMESTAMP, nullable=True)
    recorded_at = db.Column(
        db.TIMESTAMP,
        server_default=func.current_timestamp()
    )
    archived_at = db.Column(
        db.TIMESTAMP,
        server_default=func.current_timestamp()
    )

    inventory = db.relationship(
        "InventoryModel",
        backref="price_history_archive",
        lazy=True
    )
    product_price_tracking = db.relationship(
        "ProductPriceTrackingModel",
        backref="price_history_archive",
        lazy=True
    )
