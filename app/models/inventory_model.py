from sqlalchemy.sql import func

from app.database.session import db
from app.models.base import BaseModel
from app.models.column_types import BitBoolean


class InventoryModel(BaseModel):
    __tablename__ = "inventory"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id", ondelete="RESTRICT"),
        nullable=False
    )
    collection_id = db.Column(
        db.Integer,
        db.ForeignKey("collections.id", ondelete="RESTRICT"),
        nullable=False
    )
    extra_type_id = db.Column(
        db.Integer,
        db.ForeignKey("types.id", ondelete="RESTRICT")
    )
    purchase_id = db.Column(
        db.Integer,
        db.ForeignKey("purchases.id", ondelete="RESTRICT")
    )
    purchase_item_id = db.Column(
        db.Integer,
        db.ForeignKey("purchase_items.id", ondelete="SET NULL")
    )
    quantity = db.Column(db.Integer, server_default="1")
    is_sealed = db.Column(BitBoolean, server_default="0")
    posted_instagram = db.Column(BitBoolean, server_default="0")
    language_id = db.Column(
        db.Integer,
        db.ForeignKey("languages.id", ondelete="RESTRICT")
    )
    condition_id = db.Column(
        db.Integer,
        db.ForeignKey("product_conditions.id", ondelete="RESTRICT")
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False
    )
    notes = db.Column(db.Text)
    created_at = db.Column(
        db.TIMESTAMP,
        server_default=func.current_timestamp()
    )
    updated_at = db.Column(
        db.TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )

    product = db.relationship("ProductModel", backref="inventory", lazy=True)
    collection = db.relationship(
        "CollectionModel",
        backref="inventory",
        lazy=True
    )
    extra_type = db.relationship("TypeModel", backref="inventory", lazy=True)
    purchase = db.relationship("PurchaseModel", backref="inventory", lazy=True)
    purchase_item = db.relationship("PurchaseItemModel", backref="inventory_entries", lazy=True)
    language = db.relationship("LanguageModel", backref="inventory", lazy=True)
    condition = db.relationship(
        "ProductConditionModel",
        backref="inventory",
        lazy=True
    )
    user = db.relationship("UserModel", backref="inventory_entries", lazy=True)
