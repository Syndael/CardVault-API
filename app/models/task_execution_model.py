from sqlalchemy.sql import func

from app.database.session import db
from app.models.base import BaseModel


class TaskExecutionModel(BaseModel):
    __tablename__ = "task_executions"

    id                = db.Column(db.Integer,   primary_key=True)
    scheduled_task_id = db.Column(db.Integer,   db.ForeignKey("scheduled_tasks.id"), nullable=False)
    status            = db.Column(db.String(20), nullable=False, default="pending")
    scheduled_date    = db.Column(db.DateTime,  nullable=False)
    started_at        = db.Column(db.DateTime,  nullable=True)
    finished_at       = db.Column(db.DateTime,  nullable=True)
    output            = db.Column(db.Text,      nullable=True)
    log_file_path     = db.Column(db.String(500), nullable=True)
    created_at        = db.Column(db.TIMESTAMP, server_default=func.current_timestamp())

    scheduled_task = db.relationship("ScheduledTaskModel", back_populates="executions")
