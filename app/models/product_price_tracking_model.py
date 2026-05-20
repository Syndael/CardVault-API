from sqlalchemy.sql import func

from app.database.session import db
from app.models.base import BaseModel


class ProductPriceTrackingModel(BaseModel):
    __tablename__ = "product_price_tracking"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id", ondelete="RESTRICT"),
        nullable=False
    )
    price_source_id = db.Column(
        db.Integer,
        db.ForeignKey("price_sources.id", ondelete="RESTRICT"),
        nullable=False
    )
    url = db.Column(db.String(500), nullable=False)
    created_at = db.Column(
        db.TIMESTAMP,
        server_default=func.current_timestamp()
    )

    product = db.relationship(
        "ProductModel",
        backref="price_tracking",
        lazy=True
    )
    price_source = db.relationship(
        "PriceSourceModel",
        backref="product_tracking",
        lazy=True
    )
