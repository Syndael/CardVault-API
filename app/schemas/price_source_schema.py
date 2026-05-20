from marshmallow import Schema, fields


class PriceSourceSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    base_url = fields.Str(allow_none=True)
    language_param = fields.Str(allow_none=True)
    condition_param = fields.Str(allow_none=True)
