from sqlalchemy.sql import func

from app.database.session import db
from app.models.base import BaseModel


class WishlistNotificationModel(BaseModel):
    __tablename__ = "wishlist_notifications"

    id = db.Column(db.Integer, primary_key=True)
    wishlist_item_id = db.Column(db.Integer, db.ForeignKey("wishlist_items.id", ondelete="CASCADE"), nullable=False)
    notified_at = db.Column(db.TIMESTAMP, server_default=func.current_timestamp())
    type = db.Column(db.String(20), nullable=False, default="email")
    price = db.Column(db.Numeric(10, 2), nullable=False)
