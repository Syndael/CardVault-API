from sqlalchemy.sql import func

from app.database.session import db
from app.models.base import BaseModel


class TagModel(BaseModel):
    __tablename__ = "tags"

    id         = db.Column(db.Integer,     primary_key=True)
    name       = db.Column(db.String(100), nullable=False, unique=True)
    color      = db.Column(db.String(7),   nullable=True)
    created_at = db.Column(db.TIMESTAMP,   server_default=func.current_timestamp())
