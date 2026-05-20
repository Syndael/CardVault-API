from sqlalchemy.sql import func

from app.database.session import db
from app.models.base import BaseModel
from app.models.column_types import BitBoolean


class CollectionModel(BaseModel):
    __tablename__ = "collections"

    id = db.Column(db.Integer, primary_key=True)
    card_type_id = db.Column(
        db.Integer,
        db.ForeignKey("types.id", ondelete="RESTRICT"),
        nullable=False
    )
    code = db.Column(db.String(50), nullable=False)
    is_manual = db.Column(
        BitBoolean,
        nullable=False,
        server_default="0"
    )
    release_date = db.Column(db.Date)
    created_at = db.Column(
        db.TIMESTAMP,
        server_default=func.current_timestamp()
    )
    card_type = db.relationship(
        "TypeModel",
        backref="collections",
        lazy=True
    )
    __table_args__ = (
        db.UniqueConstraint(
            "card_type_id",
            "code",
            "is_manual",
            name="uq_type_code_manual"
        ),
    )
