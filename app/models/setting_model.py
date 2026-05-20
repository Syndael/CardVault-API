from sqlalchemy.sql import func

from app.database.session import db
from app.models.base import BaseModel


class SettingModel(BaseModel):
    __tablename__ = "settings"

    id = db.Column(db.Integer, primary_key=True)
    setting_key = db.Column(db.String(150), nullable=False)
    setting_value = db.Column(db.Text)
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
        db.UniqueConstraint(
            "setting_key",
            name="uq_settings_key"
        ),
    )
