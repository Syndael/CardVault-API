from marshmallow import Schema, fields

from app.schemas.collection_schema import CollectionSchema
from app.schemas.fields import BitBool
from app.schemas.type_schema import TypeSchema


class ProductSchema(Schema):
    id                = fields.Int(dump_only=True)
    collection_id     = fields.Int(load_only=True, required=True)
    product_type_id   = fields.Int(load_only=True, required=True)
    product_format_id = fields.Int(load_only=True)
    product_number    = fields.Str(allow_none=True)
    force_download    = BitBool(allow_none=True)
    is_verified       = BitBool(load_default=False)
    is_manual         = BitBool(load_default=False)
    completion_group  = fields.Str(load_default="standard")
    created_at        = fields.DateTime(dump_only=True)
    collection        = fields.Nested(CollectionSchema, dump_only=True)
    product_type      = fields.Nested(TypeSchema,       dump_only=True)
    product_format    = fields.Nested(TypeSchema,        dump_only=True)
    translations      = fields.Nested(
        "app.schemas.product_translation_schema.ProductTranslationSchema",
        many=True,
        dump_only=True,
        exclude=("product",)
    )
