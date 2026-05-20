from sqlalchemy.sql import func

from app.database.session import db
from app.models.base import BaseModel
from app.models.column_types import BitBoolean


class ProductModel(BaseModel):
    __tablename__ = "products"

    id              = db.Column(db.Integer,    primary_key=True)
    collection_id   = db.Column(
        db.Integer,
        db.ForeignKey("collections.id", ondelete="RESTRICT"),
        nullable=False
    )
    product_type_id = db.Column(
        db.Integer,
        db.ForeignKey("types.id", ondelete="RESTRICT"),
        nullable=False
    )
    product_number  = db.Column(db.String(50))
    force_download  = db.Column(BitBoolean)
    is_verified     = db.Column(BitBoolean, server_default="0")
    created_at      = db.Column(db.TIMESTAMP, server_default=func.current_timestamp())

    collection   = db.relationship("CollectionModel", backref="products", lazy=True)
    product_type = db.relationship("TypeModel",       backref="products", lazy=True)

    __table_args__ = (
        db.UniqueConstraint(
            "collection_id",
            "product_number",
            "product_type_id",
            name="uq_collection_product"
        ),
    )
