from marshmallow import Schema, fields

from app.schemas.language_schema import LanguageSchema
from app.schemas.product_schema import ProductSchema


class ProductTranslationSchema(Schema):
    id = fields.Int(dump_only=True)
    product_id = fields.Int(load_only=True, required=True)
    language_id = fields.Int(required=True)
    name = fields.Str(required=True)
    name_alter = fields.Str(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    product = fields.Nested(ProductSchema, dump_only=True)
    language = fields.Nested(LanguageSchema, dump_only=True)
