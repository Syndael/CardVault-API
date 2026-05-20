from sqlalchemy.sql import func

from app.database.session import db
from app.models.base import BaseModel


class ProductConditionModel(BaseModel):
    __tablename__ = "product_conditions"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    abbreviation = db.Column(db.String(10), nullable=False)
    cardmarket_code = db.Column(db.String(10))
    created_at = db.Column(
        db.TIMESTAMP,
        server_default=func.current_timestamp()
    )

    __table_args__ = (
        db.UniqueConstraint(
            "name",
            name="uq_conditions_name"
        ),
        db.UniqueConstraint(
            "abbreviation",
            name="uq_conditions_abbr"
        ),
    )
