from sqlalchemy.sql import func

from app.database.session import db
from app.models.base import BaseModel


class EntityModel(BaseModel):
    __tablename__ = "entities"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    entity_type = db.Column(db.Integer, nullable=False)
    parent_id = db.Column(
        db.Integer,
        db.ForeignKey("entities.id", ondelete="RESTRICT")
    )
    created_at = db.Column(
        db.TIMESTAMP,
        server_default=func.current_timestamp()
    )

    parent = db.relationship(
        "EntityModel",
        remote_side=[id],
        backref="children",
        lazy=True
    )
