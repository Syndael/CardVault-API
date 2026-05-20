from marshmallow import Schema, fields


class SettingSchema(Schema):
    id = fields.Int(dump_only=True)
    setting_key = fields.Str(required=True)
    setting_value = fields.Str(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
