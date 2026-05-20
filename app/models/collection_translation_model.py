from sqlalchemy.sql import func

from app.database.session import db
from app.models.base import BaseModel


class CollectionTranslationModel(BaseModel):
    __tablename__ = "collection_translations"

    id = db.Column(db.Integer, primary_key=True)
    collection_id = db.Column(
        db.Integer,
        db.ForeignKey("collections.id", ondelete="RESTRICT"),
        nullable=False
    )
    language_id = db.Column(
        db.Integer,
        db.ForeignKey("languages.id", ondelete="RESTRICT"),
        nullable=False
    )
    name = db.Column(
        db.String(255),
        nullable=False
    )
    name_alter = db.Column(
        db.String(255)
    )
    created_at = db.Column(
        db.TIMESTAMP,
        server_default=func.current_timestamp()
    )
    collection = db.relationship(
        "CollectionModel",
        backref="translations",
        lazy=True
    )
    language = db.relationship(
        "LanguageModel",
        backref="collection_translations",
        lazy=True
    )
    __table_args__ = (
        db.UniqueConstraint(
            "collection_id",
            "language_id",
            name="uq_collection_lang"
        ),
    )
