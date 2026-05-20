from app.repositories.scheduled_task_repository import ScheduledTaskRepository
from app.services.crud_service import CrudService


class ScheduledTaskService(CrudService):
    repository = ScheduledTaskRepository

    @classmethod
    def get_enabled(cls):
        return cls.repository.get_enabled()
