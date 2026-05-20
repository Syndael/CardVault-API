from app.models.scheduled_task_model import ScheduledTaskModel
from app.repositories.crud_repository import CrudRepository


class ScheduledTaskRepository(CrudRepository):
    model = ScheduledTaskModel
    order_by = (ScheduledTaskModel.name,)
    create_fields = ("name", "script_path", "cron_expression", "enabled")
    update_fields = create_fields

    @classmethod
    def get_enabled(cls):
        return cls.model.query.filter_by(enabled=True).all()
