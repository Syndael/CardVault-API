from sqlalchemy.sql import func

from app.database.session import db
from app.models.base import BaseModel


class WishlistPriceModel(BaseModel):
    __tablename__ = "wishlist_prices"

    id = db.Column(db.BigInteger, primary_key=True)
    wishlist_item_id = db.Column(db.Integer, db.ForeignKey("wishlist_items.id", ondelete="CASCADE"), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    min_price = db.Column(db.Numeric(10, 2), nullable=True)
    max_price = db.Column(db.Numeric(10, 2), nullable=True)
    min_price_recorded_at = db.Column(db.TIMESTAMP, nullable=True)
    max_price_recorded_at = db.Column(db.TIMESTAMP, nullable=True)
    source = db.Column(db.String(100), nullable=True)
    recorded_at = db.Column(db.TIMESTAMP, server_default=func.current_timestamp())
