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
    purchase_date = db.Column(db.DateTime, nullable=True)
    delivery_date = db.Column(db.DateTime, nullable=True)
    total_amount = db.Column(db.Numeric(10, 2))
    shipping_cost = db.Column(
        db.Numeric(10, 2),
        server_default="0"
    )
    currency = db.Column(
        db.String(10),
        server_default="EUR"
    )
    conversion_rate = db.Column(db.Numeric(10, 4))
    original_amount = db.Column(db.Numeric(10, 2))
    original_currency = db.Column(db.String(10))
    external_reference = db.Column(db.String(255))
    tracking_code = db.Column(db.String(255))
    shipping_status_id = db.Column(
        db.Integer,
        db.ForeignKey("types.id", ondelete="RESTRICT")
    )
    shipping_company_id = db.Column(
        db.Integer,
        db.ForeignKey("entities.id", ondelete="RESTRICT")
    )
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
        foreign_keys=[entity_id],
        backref="purchases",
        lazy=True
    )
    user = db.relationship("UserModel", backref="purchases", lazy=True)
    shipping_status = db.relationship(
        "TypeModel",
        foreign_keys=[shipping_status_id],
        lazy=True
    )
    shipping_company = db.relationship(
        "EntityModel",
        foreign_keys=[shipping_company_id],
        lazy=True
    )
