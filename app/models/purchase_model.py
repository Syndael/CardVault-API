from sqlalchemy.sql import func

from app.database.session import db
from app.models.base import BaseModel


class PurchaseModel(BaseModel):
    __tablename__ = "purchases"

    id = db.Column(db.Integer, primary_key=True)
    entity_id = db.Column(
        db.Integer,
        db.ForeignKey("entities.id", ondelete="RESTRICT"),
        nullable=False
    )
    purchase_date = db.Column(db.DateTime, nullable=False)
    total_amount = db.Column(db.Numeric(10, 2))
    shipping_cost = db.Column(
        db.Numeric(10, 2),
        server_default="0"
    )
    currency = db.Column(
        db.String(10),
        server_default="EUR"
    )
    external_reference = db.Column(db.String(255))
    notes = db.Column(db.Text)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False
    )
    created_at = db.Column(
        db.TIMESTAMP,
        server_default=func.current_timestamp()
    )

    entity = db.relationship(
        "EntityModel",
        backref="purchases",
        lazy=True
    )
    user = db.relationship("UserModel", backref="purchases", lazy=True)
