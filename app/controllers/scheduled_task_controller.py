from flask import jsonify

from app.controllers.crud_controller import create_crud_blueprint
from app.schemas.scheduled_task_schema import ScheduledTaskSchema
from app.services.scheduled_task_service import ScheduledTaskService


scheduled_task_blueprint = create_crud_blueprint(
    "scheduled-tasks",
    ScheduledTaskService,
    ScheduledTaskSchema,
    "scheduled_task_id",
)


@scheduled_task_blueprint.route("/enabled", methods=["GET"], strict_slashes=False)
def get_enabled():
    schema = ScheduledTaskSchema(many=True)
    data = ScheduledTaskService.get_enabled()
    return jsonify(schema.dump(data))
