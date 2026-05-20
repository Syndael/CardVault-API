from sqlalchemy.sql import func

from app.database.session import db
from app.models.base import BaseModel


class UserRoleModel(BaseModel):
    __tablename__ = "user_roles"

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )
    role_id = db.Column(
        db.Integer,
        db.ForeignKey("roles.id", ondelete="RESTRICT"),
        primary_key=True
    )
    created_at = db.Column(
        db.TIMESTAMP,
        server_default=func.current_timestamp()
    )

    user = db.relationship("UserModel", backref="user_roles", lazy=True)
    role = db.relationship("RoleModel", backref="user_roles", lazy=True)

    __table_args__ = (
        db.Index("idx_user_roles_role", "role_id"),
    )
