from marshmallow import Schema, fields

from app.schemas.inventory_schema import InventorySchema
from app.schemas.language_schema import LanguageSchema
from app.schemas.product_schema import ProductSchema
from app.schemas.type_schema import TypeSchema


class FileSchema(Schema):
    id = fields.Int(dump_only=True)
    product_id = fields.Int(load_only=True, allow_none=True)
    inventory_id = fields.Int(load_only=True, allow_none=True)
    language_id = fields.Int(load_only=True, allow_none=True)
    original_name = fields.Str(required=True)
    stored_name = fields.Str(required=True)
    file_path = fields.Str(required=True)
    file_type_id = fields.Int(load_only=True, allow_none=True)
    file_size = fields.Int(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    product = fields.Nested(ProductSchema, dump_only=True)
    inventory = fields.Nested(InventorySchema, dump_only=True)
    language = fields.Nested(LanguageSchema, dump_only=True)
    file_type = fields.Nested(TypeSchema, dump_only=True)
