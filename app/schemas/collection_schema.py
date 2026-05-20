from marshmallow import Schema, fields

from app.schemas.fields import BitBool
from app.schemas.type_schema import TypeSchema


class CollectionSchema(Schema):
    id = fields.Int(dump_only=True)
    card_type_id = fields.Int(load_only=True)
    code = fields.Str(required=True)
    is_manual = BitBool()
    release_date = fields.Date(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    card_type = fields.Nested(
        TypeSchema,
        dump_only=True
    )
