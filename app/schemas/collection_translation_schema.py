from marshmallow import Schema, fields

from app.schemas.language_schema import LanguageSchema


class CollectionTranslationSchema(Schema):
    id = fields.Int(dump_only=True)
    collection_id = fields.Int(required=True)
    language_id = fields.Int(required=True)
    name = fields.Str(required=True)
    name_alter = fields.Str(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    language = fields.Nested(
        LanguageSchema,
        dump_only=True
    )
