from marshmallow import Schema, fields


class EntitySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    url = fields.Str(allow_none=True, load_default=None)
    entity_type = fields.Int(required=True)
    parent_id = fields.Int(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
