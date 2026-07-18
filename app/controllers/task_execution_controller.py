import os

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


@task_execution_blueprint.route("/running", methods=["GET"], strict_slashes=False)
def get_running():
    if not auth.has_any_role(*READ_ROLES):
        return jsonify({"message": "Forbidden"}), 403
    schema = TaskExecutionSchema(many=True)
    data = TaskExecutionService.get_running()
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


@task_execution_blueprint.route("/<int:exec_id>/log", methods=["GET"], strict_slashes=False)
def get_execution_log(exec_id):
    if not auth.has_any_role(*READ_ROLES):
        return jsonify({"message": "Forbidden"}), 403
    execution = TaskExecutionService.get_by_id(exec_id)
    if not execution or not execution.log_file_path:
        return jsonify({"message": "Log not found"}), 404
    log_path = execution.log_file_path
    if not os.path.isabs(log_path):
        api_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
        log_path = os.path.join(api_root, log_path)
    if not os.path.exists(log_path):
        return jsonify({"message": "Log file not found on disk"}), 404
    with open(log_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
    return jsonify({"content": content})


@task_execution_blueprint.route("/<int:exec_id>/retry", methods=["POST"], strict_slashes=False)
def retry_execution(exec_id):
    if not auth.has_any_role(*WRITE_ROLES):
        return jsonify({"message": "Forbidden"}), 403
    entity = TaskExecutionService.retry_execution(exec_id)
    if not entity:
        return jsonify({"message": "Not found"}), 404
    schema = TaskExecutionSchema()
    return jsonify(schema.dump(entity))
