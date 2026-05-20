from marshmallow import Schema, fields


class ScheduledTaskSchema(Schema):
    id              = fields.Int(dump_only=True)
    name            = fields.Str(required=True)
    script_path     = fields.Str(required=True)
    cron_expression = fields.Str(required=True)
    enabled         = fields.Bool(load_default=True)
    created_at      = fields.DateTime(dump_only=True)
