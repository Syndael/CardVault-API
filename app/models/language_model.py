from sqlalchemy.sql import func

from app.database.session import db
from app.models.base import BaseModel


class LanguageModel(BaseModel):
    __tablename__ = "languages"
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    name = db.Column(
        db.String(100),
        nullable=False
    )
    abbreviation = db.Column(
        db.String(10),
        nullable=False
    )
    cardmarket_code = db.Column(
        db.String(10)
    )
    tcgdex_language_code = db.Column(
        db.String(10)
    )
    priority_order = db.Column(
        db.Integer,
        nullable=False,
        server_default="999"
    )
    created_at = db.Column(
        db.TIMESTAMP,
        server_default=func.current_timestamp()
    )

    __table_args__ = (
        db.UniqueConstraint(
            "name",
            name="uq_languages_name"
        ),

        db.UniqueConstraint(
            "abbreviation",
            name="uq_languages_abbr"
        ),
    )
