from app.database.session import db
from app.models.base import BaseModel


class PriceSourceModel(BaseModel):
    __tablename__ = "price_sources"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    base_url = db.Column(db.String(500))
    language_param = db.Column(db.String(50))
    condition_param = db.Column(db.String(50))
