from sqlalchemy.sql import func

from app.database.session import db
from app.models.base import BaseModel


class UserModel(BaseModel):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    display_name = db.Column(db.String(150))
    is_active = db.Column(db.Boolean, nullable=False, server_default="1")
    is_email_verified = db.Column(
        db.Boolean,
        nullable=False,
        server_default="0"
    )
    last_login_at = db.Column(db.DateTime)
    password_changed_at = db.Column(db.DateTime)
    created_at = db.Column(
        db.TIMESTAMP,
        server_default=func.current_timestamp()
    )
    updated_at = db.Column(
        db.TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )

    __table_args__ = (
        db.UniqueConstraint("username", name="uq_users_username"),
        db.UniqueConstraint("email", name="uq_users_email"),
        db.Index("idx_users_active", "is_active"),
    )
