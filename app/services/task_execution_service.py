from app.repositories.task_execution_repository import TaskExecutionRepository
from app.services.crud_service import CrudService


class TaskExecutionService(CrudService):
    repository = TaskExecutionRepository

    @classmethod
    def get_pending(cls):
        return cls.repository.get_pending()

    @classmethod
    def get_running(cls):
        return cls.repository.get_running()

    @classmethod
    def get_last_for_task(cls, task_id):
        return cls.repository.get_last_for_task(task_id)

    @classmethod
    def retry_execution(cls, exec_id):
        """Reset a failed/cancelled execution back to pending."""
        from app.database.session import db
        from datetime import datetime
        entity = cls.repository.get_by_id(exec_id)
        if not entity:
            return None
        entity.status = "pending"
        entity.started_at = None
        entity.finished_at = None
        entity.output = None
        entity.log_file_path = None
        entity.scheduled_date = datetime.now()
        db.session.commit()
        return entity
