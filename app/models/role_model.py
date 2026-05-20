from sqlalchemy.sql import func

from app.database.session import db
from app.models.base import BaseModel


class RoleModel(BaseModel):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(
        db.TIMESTAMP,
        server_default=func.current_timestamp()
    )

    __table_args__ = (
        db.UniqueConstraint("name", name="uq_roles_name"),
    )
