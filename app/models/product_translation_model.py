from sqlalchemy.sql import func

from app.database.session import db
from app.models.base import BaseModel


class ProductTranslationModel(BaseModel):
    __tablename__ = "product_translations"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id", ondelete="RESTRICT"),
        nullable=False
    )
    language_id = db.Column(
        db.Integer,
        db.ForeignKey("languages.id", ondelete="RESTRICT"),
        nullable=False
    )
    name = db.Column(db.String(255), nullable=False)
    name_alter = db.Column(db.String(255))
    created_at = db.Column(
        db.TIMESTAMP,
        server_default=func.current_timestamp()
    )

    product = db.relationship(
        "ProductModel",
        backref="translations",
        lazy=True
    )
    language = db.relationship(
        "LanguageModel",
        backref="product_translations",
        lazy=True
    )

    __table_args__ = (
        db.UniqueConstraint(
            "product_id",
            "language_id",
            name="uq_product_lang"
        ),
    )
