from sqlalchemy.sql import func

from app.database.session import db
from app.models.base import BaseModel
from app.models.column_types import BitBoolean


class FileModel(BaseModel):
    __tablename__ = "files"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id", ondelete="RESTRICT")
    )
    inventory_id = db.Column(
        db.Integer,
        db.ForeignKey("inventory.id", ondelete="RESTRICT")
    )
    purchase_id = db.Column(
        db.Integer,
        db.ForeignKey("purchases.id", ondelete="RESTRICT")
    )
    publication_id = db.Column(
        db.Integer,
        db.ForeignKey("publication_schedule.id", ondelete="SET NULL"),
        nullable=True
    )
    language_id = db.Column(
        db.Integer,
        db.ForeignKey("languages.id", ondelete="RESTRICT")
    )
    original_name = db.Column(db.String(255), nullable=False)
    stored_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type_id = db.Column(
        db.Integer,
        db.ForeignKey("types.id", ondelete="RESTRICT")
    )
    file_size = db.Column(db.Integer)
    sort_order = db.Column(db.Integer, server_default="0")
    is_primary = db.Column(BitBoolean, server_default="0")
    instagram_sort_order = db.Column(db.Integer, nullable=True, server_default=None)
    created_at = db.Column(
        db.TIMESTAMP,
        server_default=func.current_timestamp()
    )

    product = db.relationship("ProductModel", backref="files", lazy=True)
    inventory = db.relationship("InventoryModel", backref="files", lazy=True, order_by="FileModel.sort_order")
    purchase = db.relationship("PurchaseModel", backref="files", lazy=True)
    language = db.relationship("LanguageModel", backref="files", lazy=True)
    file_type = db.relationship("TypeModel", backref="files", lazy=True)
