from sqlalchemy.sql import func

from app.database.session import db
from app.models.base import BaseModel


class CollectionAlternativeCodeModel(BaseModel):
    __tablename__ = "collection_alternative_codes"

    id = db.Column(db.Integer, primary_key=True)
    collection_id = db.Column(
        db.Integer,
        db.ForeignKey("collections.id", ondelete="CASCADE"),
        nullable=False
    )
    code = db.Column(
        db.String(50),
        nullable=False
    )
    created_at = db.Column(
        db.TIMESTAMP,
        server_default=func.current_timestamp()
    )
    collection = db.relationship(
        "CollectionModel",
        backref="alternative_codes",
        lazy=True
    )
    __table_args__ = (
        db.UniqueConstraint(
            "collection_id",
            "code",
            name="uq_collection_alt_code"
        ),
    )
