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
