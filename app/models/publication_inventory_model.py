from app.database.session import db


class PublicationInventoryModel(db.Model):
    __tablename__ = "publication_inventory"

    publication_id = db.Column(
        db.Integer,
        db.ForeignKey("publication_schedule.id", ondelete="CASCADE"),
        primary_key=True
    )
    inventory_id = db.Column(
        db.Integer,
        db.ForeignKey("inventory.id", ondelete="RESTRICT"),
        primary_key=True
    )
