from flask import jsonify

from app.controllers.crud_controller import create_crud_blueprint
from app.schemas.task_execution_schema import TaskExecutionSchema
from app.services.task_execution_service import TaskExecutionService


task_execution_blueprint = create_crud_blueprint(
    "task-executions",
    TaskExecutionService,
    TaskExecutionSchema,
    "task_execution_id",
)


@task_execution_blueprint.route("/pending", methods=["GET"], strict_slashes=False)
def get_pending():
    schema = TaskExecutionSchema(many=True)
    data = TaskExecutionService.get_pending()
    return jsonify(schema.dump(data))


@task_execution_blueprint.route("/last/<int:task_id>", methods=["GET"], strict_slashes=False)
def get_last(task_id):
    data = TaskExecutionService.get_last_for_task(task_id)
    if not data:
        return jsonify(None), 200
    schema = TaskExecutionSchema()
    return jsonify(schema.dump(data))
