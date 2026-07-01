from sqlalchemy.sql import func

from app.database.session import db
from app.models.base import BaseModel


class UserCollectionTrackingModel(BaseModel):
    __tablename__ = "user_collection_tracking"

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    collection_id = db.Column(
        db.Integer,
        db.ForeignKey("collections.id", ondelete="CASCADE"),
        primary_key=True,
    )
    tracking_mode = db.Column(
        db.String(20),
        nullable=False,
        server_default="standard",
    )
    created_at = db.Column(
        db.TIMESTAMP,
        server_default=func.current_timestamp(),
    )

    user = db.relationship("UserModel", backref="collection_tracking")
    collection = db.relationship("CollectionModel", backref="user_tracking")
