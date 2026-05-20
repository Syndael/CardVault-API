from app.database.session import db

class BaseModel(db.Model):
    __abstract__ = True