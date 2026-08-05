from app.database.session import db


class PublicationPurchaseModel(db.Model):
    __tablename__ = "publication_purchases"

    publication_id = db.Column(
        db.Integer,
        db.ForeignKey("publication_schedule.id", ondelete="CASCADE"),
        primary_key=True
    )
    purchase_id = db.Column(
        db.Integer,
        db.ForeignKey("purchases.id", ondelete="RESTRICT"),
        primary_key=True
    )
