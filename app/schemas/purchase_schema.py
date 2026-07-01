from marshmallow import Schema, fields

from app.schemas.entity_schema import EntitySchema
from app.schemas.type_schema import TypeSchema


class PurchaseSchema(Schema):
    id = fields.Int(dump_only=True)
    entity_id = fields.Int(load_only=True, required=True)
    purchase_date = fields.DateTime(required=False, allow_none=True)
    delivery_date = fields.DateTime(required=False, allow_none=True)
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
    commission = fields.Decimal(
        places=2,
        as_string=True,
        load_default=0
    )
    currency = fields.Str(load_default="EUR")
    conversion_rate = fields.Decimal(
        places=8,
        as_string=True,
        allow_none=True
    )
    original_amount = fields.Decimal(
        places=2,
        as_string=True,
        allow_none=True
    )
    original_currency = fields.Str(allow_none=True)
    external_reference = fields.Str(allow_none=True)
    tracking_code = fields.Str(allow_none=True, load_default=None)
    shipping_status_id = fields.Int(allow_none=True, load_default=None)
    shipping_company_id = fields.Int(allow_none=True, load_default=None)
    notes = fields.Str(allow_none=True)
    user_id = fields.Int(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    entity = fields.Nested(EntitySchema, dump_only=True)
    shipping_status = fields.Nested(TypeSchema, dump_only=True)
    shipping_company = fields.Nested(EntitySchema, dump_only=True)
    has_photos = fields.Function(lambda obj: any(
        f.file_type and f.file_type.name == 'image' for f in getattr(obj, 'files', []) or []
    ))
    has_docs = fields.Function(lambda obj: any(
        f.file_type and f.file_type.name == 'document' for f in getattr(obj, 'files', []) or []
    ))
    items = fields.Nested(
        "app.schemas.purchase_item_schema.PurchaseItemSchema",
        many=True,
        dump_only=True,
        exclude=("purchase",)
    )
