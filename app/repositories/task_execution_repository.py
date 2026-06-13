from datetime import datetime

from app.models.task_execution_model import TaskExecutionModel
from app.repositories.crud_repository import CrudRepository


class TaskExecutionRepository(CrudRepository):
    model = TaskExecutionModel
    order_by = (TaskExecutionModel.scheduled_date.desc(),)
    create_fields = ("scheduled_task_id", "status", "scheduled_date")
    update_fields = ("status", "started_at", "finished_at", "output", "log_file_path")

    @classmethod
    def get_pending(cls):
        return cls.model.query.filter(
            cls.model.status == "pending",
            cls.model.scheduled_date <= datetime.now(),
        ).order_by(cls.model.scheduled_date).all()

    @classmethod
    def get_last_for_task(cls, task_id):
        return cls.model.query.filter_by(
            scheduled_task_id=task_id,
        ).order_by(cls.model.scheduled_date.desc()).first()
