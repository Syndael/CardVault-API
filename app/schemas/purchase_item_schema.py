from marshmallow import Schema, fields

from app.schemas.product_schema import ProductSchema
from app.schemas.purchase_schema import PurchaseSchema


class PurchaseItemSchema(Schema):
    id = fields.Int(dump_only=True)
    purchase_id = fields.Int(load_only=True, required=True)
    product_id = fields.Int(load_only=True, required=True)
    unit_price = fields.Decimal(
        places=2,
        as_string=True,
        required=True
    )
    quantity = fields.Int(load_default=1)
    created_at = fields.DateTime(dump_only=True)
    purchase = fields.Nested(PurchaseSchema, dump_only=True)
    product = fields.Nested(ProductSchema, dump_only=True)
