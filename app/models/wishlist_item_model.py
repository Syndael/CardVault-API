from sqlalchemy.sql import func

from app.database.session import db
from app.models.base import BaseModel


class WishlistItemModel(BaseModel):
    __tablename__ = "wishlist_items"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id", ondelete="RESTRICT"), nullable=False)
    target_price = db.Column(db.Numeric(10, 2), nullable=True)
    language_id = db.Column(db.Integer, db.ForeignKey("languages.id", ondelete="RESTRICT"), nullable=True)
    condition_id = db.Column(db.Integer, db.ForeignKey("product_conditions.id", ondelete="RESTRICT"), nullable=True)
    w_state = db.Column(db.String(20), nullable=False, default="buscando")
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.TIMESTAMP, server_default=func.current_timestamp())
    updated_at = db.Column(db.TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    user = db.relationship("UserModel", backref="wishlist_items", lazy=True)
    product = db.relationship("ProductModel", backref="wishlist_items", lazy=True)
    language = db.relationship("LanguageModel", backref="wishlist_items", lazy=True)
    condition = db.relationship("ProductConditionModel", backref="wishlist_items", lazy=True)
    prices = db.relationship("WishlistPriceModel", backref="wishlist_item", lazy=True, passive_deletes=True, order_by="WishlistPriceModel.recorded_at.desc()")
    notifications = db.relationship("WishlistNotificationModel", backref="wishlist_item", lazy=True, passive_deletes=True)
