from sqlalchemy.sql import func

from app.database.session import db
from app.models.base import BaseModel
from app.models.type_model import TypeModel
from app.models.publication_inventory_model import PublicationInventoryModel
from app.models.publication_purchase_model import PublicationPurchaseModel


class PublicationScheduleModel(BaseModel):
    __tablename__ = "publication_schedule"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=True)
    scheduled_at = db.Column(db.DateTime, nullable=True)
    published_at = db.Column(db.DateTime, nullable=True)
    status_id = db.Column(
        db.Integer,
        db.ForeignKey("types.id"),
        nullable=False
    )
    caption = db.Column(db.Text)
    instagram_media_id = db.Column(db.String(100))
    instagram_permalink = db.Column(db.String(500))
    error_message = db.Column(db.Text)
    created_at = db.Column(
        db.TIMESTAMP,
        server_default=func.current_timestamp()
    )
    updated_at = db.Column(
        db.TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )

    status_type = db.relationship("TypeModel", foreign_keys=[status_id], lazy=True)

    inventories = db.relationship(
        "InventoryModel",
        secondary="publication_inventory",
        backref="publications",
        lazy=True
    )

    purchases = db.relationship(
        "PurchaseModel",
        secondary="publication_purchases",
        backref="publications",
        lazy=True
    )

    files = db.relationship(
        "FileModel",
        backref="publication",
        lazy=True,
        primaryjoin="PublicationScheduleModel.id == foreign(FileModel.publication_id)"
    )

    @property
    def status(self):
        return self.status_type.name if self.status_type else None

    @status.setter
    def status(self, value):
        if value is None:
            self.status_id = None
        else:
            t = TypeModel.query.filter_by(type="publication_status", name=value).first()
            self.status_id = t.id if t else self.status_id

    @property
    def inventory_id(self):
        invs = self.inventories
        return invs[0].id if invs else None

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "inventory_id": self.inventory_id,
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "status": self.status,
            "caption": self.caption,
            "instagram_media_id": self.instagram_media_id,
            "instagram_permalink": self.instagram_permalink,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
