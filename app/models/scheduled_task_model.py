from sqlalchemy.sql import func

from app.database.session import db
from app.models.base import BaseModel


class ScheduledTaskModel(BaseModel):
    __tablename__ = "scheduled_tasks"

    id              = db.Column(db.Integer,     primary_key=True)
    name            = db.Column(db.String(200), nullable=False)
    script_path     = db.Column(db.String(500), nullable=False)
    cron_expression = db.Column(db.String(100), nullable=False)
    enabled         = db.Column(db.Boolean,     nullable=False, default=True)
    created_at      = db.Column(db.TIMESTAMP,   server_default=func.current_timestamp())

    executions = db.relationship("TaskExecutionModel", back_populates="scheduled_task", lazy="dynamic")
