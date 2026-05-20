from marshmallow import Schema, fields

class TypeSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    short_name = fields.Str(allow_none=True)
    type = fields.Str(required=True)
