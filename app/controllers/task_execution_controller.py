from flask import jsonify

import app.auth as auth
from app.controllers.crud_controller import create_crud_blueprint
from app.schemas.task_execution_schema import TaskExecutionSchema
from app.services.task_execution_service import TaskExecutionService

READ_ROLES = ["scheduled_task_read", "admin"]
WRITE_ROLES = ["scheduled_task_write", "admin"]

task_execution_blueprint = create_crud_blueprint(
    "task-executions",
    TaskExecutionService,
    TaskExecutionSchema,
    "task_execution_id",
    read_roles=READ_ROLES,
    write_roles=WRITE_ROLES,
)


@task_execution_blueprint.route("/pending", methods=["GET"], strict_slashes=False)
def get_pending():
    if not auth.has_any_role(*READ_ROLES):
        return jsonify({"message": "Forbidden"}), 403
    schema = TaskExecutionSchema(many=True)
    data = TaskExecutionService.get_pending()
    return jsonify(schema.dump(data))


@task_execution_blueprint.route("/last/<int:task_id>", methods=["GET"], strict_slashes=False)
def get_last(task_id):
    if not auth.has_any_role(*READ_ROLES):
        return jsonify({"message": "Forbidden"}), 403
    data = TaskExecutionService.get_last_for_task(task_id)
    if not data:
        return jsonify(None), 200
    schema = TaskExecutionSchema()
    return jsonify(schema.dump(data))
