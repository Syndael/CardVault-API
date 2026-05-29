from marshmallow import Schema, fields

from app.schemas.inventory_schema import InventorySchema
from app.schemas.product_price_tracking_schema import (
    ProductPriceTrackingSchema
)


class InventoryPriceHistoryArchiveSchema(Schema):
    id = fields.Int(dump_only=True)
    inventory_id = fields.Int(load_only=True, required=True)
    product_price_tracking_id = fields.Int(load_only=True, required=True)
    price = fields.Decimal(
        places=2,
        as_string=True,
        required=True
    )
    min_price = fields.Decimal(
        places=2,
        as_string=True,
        allow_none=True
    )
    max_price = fields.Decimal(
        places=2,
        as_string=True,
        allow_none=True
    )
    min_price_recorded_at = fields.DateTime(allow_none=True)
    max_price_recorded_at = fields.DateTime(allow_none=True)
    recorded_at = fields.DateTime(dump_only=True)
    archived_at = fields.DateTime(dump_only=True)
    inventory = fields.Nested(InventorySchema, dump_only=True)
    product_price_tracking = fields.Nested(
        ProductPriceTrackingSchema,
        dump_only=True
    )
