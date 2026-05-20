from marshmallow import Schema, fields


class EntitySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    entity_type = fields.Int(required=True)
    parent_id = fields.Int(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
