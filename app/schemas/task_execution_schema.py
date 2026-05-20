from marshmallow import Schema, fields, validate

from app.schemas.scheduled_task_schema import ScheduledTaskSchema


class TaskExecutionSchema(Schema):
    id                = fields.Int(dump_only=True)
    scheduled_task_id = fields.Int(required=True)
    status            = fields.Str(
        load_default="pending",
        validate=validate.OneOf(["pending", "running", "completed", "error"]),
    )
    scheduled_date    = fields.DateTime(required=True)
    started_at        = fields.DateTime(dump_only=True)
    finished_at       = fields.DateTime(dump_only=True)
    output            = fields.Str(dump_only=True)
    created_at        = fields.DateTime(dump_only=True)
    scheduled_task    = fields.Nested(ScheduledTaskSchema, dump_only=True)
