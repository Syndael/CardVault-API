from sqlalchemy.sql import func

from app.database.session import db
from app.models.base import BaseModel


class TypeModel(BaseModel):
    __tablename__ = "types"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    short_name = db.Column(db.String(10))
    type = db.Column(db.String(20), nullable=False)
    created_at = db.Column(
        db.TIMESTAMP,
        server_default=func.current_timestamp()
    )

    __table_args__ = (
        db.UniqueConstraint(
            "type",
            "name",
            name="uq_type_name"
        ),
    )
