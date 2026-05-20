from sqlalchemy.sql import func

from app.database.session import db
from app.models.base import BaseModel


class UserSessionModel(BaseModel):
    __tablename__ = "user_sessions"

    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    token_hash = db.Column(db.String(64), nullable=False)
    user_agent = db.Column(db.String(255))
    ip_address = db.Column(db.String(45))
    expires_at = db.Column(db.DateTime, nullable=False)
    revoked_at = db.Column(db.DateTime)
    created_at = db.Column(
        db.TIMESTAMP,
        server_default=func.current_timestamp()
    )

    user = db.relationship("UserModel", backref="sessions", lazy=True)

    __table_args__ = (
        db.UniqueConstraint(
            "token_hash",
            name="uq_user_sessions_token_hash"
        ),
        db.Index("idx_user_sessions_user", "user_id"),
        db.Index("idx_user_sessions_expires", "expires_at"),
    )
