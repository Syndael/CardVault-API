from marshmallow import Schema, fields


class LanguageSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    abbreviation = fields.Str(required=True)
    cardmarket_code = fields.Str(allow_none=True)
    tcgdex_language_code = fields.Str(allow_none=True)
    priority_order = fields.Int(load_default=999)
    created_at = fields.DateTime(dump_only=True)
