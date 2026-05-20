from marshmallow import Schema, fields

from app.schemas.price_source_schema import PriceSourceSchema
from app.schemas.product_schema import ProductSchema


class ProductPriceTrackingSchema(Schema):
    id = fields.Int(dump_only=True)
    product_id = fields.Int(load_only=True, required=True)
    price_source_id = fields.Int(load_only=True, required=True)
    url = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)
    product = fields.Nested(ProductSchema, dump_only=True)
    price_source = fields.Nested(PriceSourceSchema, dump_only=True)
