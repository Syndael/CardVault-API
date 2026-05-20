from marshmallow import Schema, fields

from app.schemas.entity_schema import EntitySchema


class PurchaseSchema(Schema):
    id = fields.Int(dump_only=True)
    entity_id = fields.Int(load_only=True, required=True)
    purchase_date = fields.DateTime(required=True)
    total_amount = fields.Decimal(
        places=2,
        as_string=True,
        allow_none=True
    )
    shipping_cost = fields.Decimal(
        places=2,
        as_string=True,
        load_default=0
    )
    currency = fields.Str(load_default="EUR")
    external_reference = fields.Str(allow_none=True)
    notes = fields.Str(allow_none=True)
    user_id = fields.Int(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    entity = fields.Nested(EntitySchema, dump_only=True)
    items = fields.Nested(
        "app.schemas.purchase_item_schema.PurchaseItemSchema",
        many=True,
        dump_only=True,
        exclude=("purchase",)
    )
