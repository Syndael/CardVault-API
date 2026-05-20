from marshmallow import Schema, fields


class ProductConditionSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    abbreviation = fields.Str(required=True)
    cardmarket_code = fields.Str(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
