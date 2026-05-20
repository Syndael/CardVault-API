from sqlalchemy.sql import func

from app.database.session import db
from app.models.base import BaseModel


class PurchaseItemModel(BaseModel):
    __tablename__ = "purchase_items"

    id = db.Column(db.Integer, primary_key=True)
    purchase_id = db.Column(
        db.Integer,
        db.ForeignKey("purchases.id", ondelete="RESTRICT"),
        nullable=False
    )
    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id", ondelete="RESTRICT"),
        nullable=False
    )
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    quantity = db.Column(
        db.Integer,
        nullable=False,
        server_default="1"
    )
    created_at = db.Column(
        db.TIMESTAMP,
        server_default=func.current_timestamp()
    )

    purchase = db.relationship(
        "PurchaseModel",
        backref="items",
        lazy=True
    )
    product = db.relationship("ProductModel", backref="purchase_items", lazy=True)
