from flask import jsonify

import app.auth as auth
from app.controllers.crud_controller import create_crud_blueprint
from app.schemas.scheduled_task_schema import ScheduledTaskSchema
from app.services.scheduled_task_service import ScheduledTaskService

READ_ROLES = ["scheduled_task_read", "admin"]
WRITE_ROLES = ["scheduled_task_write", "admin"]

scheduled_task_blueprint = create_crud_blueprint(
    "scheduled-tasks",
    ScheduledTaskService,
    ScheduledTaskSchema,
    "scheduled_task_id",
    read_roles=READ_ROLES,
    write_roles=WRITE_ROLES,
)


@scheduled_task_blueprint.route("/enabled", methods=["GET"], strict_slashes=False)
def get_enabled():
    if not auth.has_any_role(*READ_ROLES):
        return jsonify({"message": "Forbidden"}), 403
    schema = ScheduledTaskSchema(many=True)
    data = ScheduledTaskService.get_enabled()
    return jsonify(schema.dump(data))
