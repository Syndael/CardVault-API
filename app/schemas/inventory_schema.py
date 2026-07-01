from marshmallow import Schema, fields

from app.schemas.collection_schema import CollectionSchema
from app.schemas.fields import BitBool
from app.schemas.language_schema import LanguageSchema
from app.schemas.product_condition_schema import ProductConditionSchema
from app.schemas.product_schema import ProductSchema
from app.schemas.purchase_item_schema import PurchaseItemSchema
from app.schemas.purchase_schema import PurchaseSchema
from app.schemas.tag_schema import TagSchema
from app.schemas.type_schema import TypeSchema


class InventorySchema(Schema):
    id = fields.Int(dump_only=True)
    product_id = fields.Int(load_only=True, required=True)
    collection_id = fields.Int(load_only=True, required=True)
    extra_type_id = fields.Int(load_only=True, allow_none=True)
    purchase_id = fields.Int(load_only=True, allow_none=True)
    purchase_item_id = fields.Int(load_only=True, allow_none=True)
    quantity = fields.Int(load_default=1)
    is_sealed = BitBool(load_default=False)
    posted_instagram = BitBool(load_default=False)
    language_id = fields.Int(load_only=True, allow_none=True)
    condition_id = fields.Int(load_only=True, allow_none=True)
    user_id = fields.Int(dump_only=True)
    notes = fields.Str(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    product = fields.Nested(ProductSchema, dump_only=True)
    collection = fields.Nested(CollectionSchema, dump_only=True)
    extra_type = fields.Nested(TypeSchema, dump_only=True)
    purchase = fields.Nested(PurchaseSchema, dump_only=True)
    purchase_item = fields.Nested(PurchaseItemSchema, dump_only=True)
    language = fields.Nested(LanguageSchema, dump_only=True)
    condition = fields.Nested(ProductConditionSchema, dump_only=True)
    tags = fields.Nested(TagSchema, dump_only=True, many=True)
    product_image_url = fields.Method("get_product_image_url", dump_only=True)
    inventory_image_url = fields.Method("get_inventory_image_url", dump_only=True)

    def get_product_image_url(self, obj):
        return getattr(obj, "_product_image_url", None)

    def get_inventory_image_url(self, obj):
        return getattr(obj, "_inventory_image_url", None)


class ProductLiteSchema(Schema):
    id = fields.Int()
    product_number = fields.Str()
    completion_group = fields.Str()
    product_type = fields.Nested(TypeSchema)
    translations = fields.Nested("ProductTranslationLiteSchema", many=True)


class ProductTranslationLiteSchema(Schema):
    language_id = fields.Int()
    name = fields.Str()
    name_alter = fields.Str(dump_only=True, allow_none=True)


class CollectionLiteSchema(Schema):
    code = fields.Str()
    name = fields.Str()


class LanguageLiteSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    abbreviation = fields.Str()


class ConditionLiteSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    abbreviation = fields.Str()


class InventoryListSchema(Schema):
    id = fields.Int(dump_only=True)
    quantity = fields.Int()
    is_sealed = BitBool()
    posted_instagram = BitBool()
    user_id = fields.Int(dump_only=True)
    notes = fields.Str(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    product = fields.Nested(ProductLiteSchema, dump_only=True)
    collection = fields.Nested(CollectionLiteSchema, dump_only=True)
    extra_type = fields.Nested(TypeSchema, dump_only=True)
    language = fields.Nested(LanguageLiteSchema, dump_only=True)
    condition = fields.Nested(ConditionLiteSchema, dump_only=True)
    tags = fields.Nested(TagSchema, dump_only=True, many=True)
    acquisition_price = fields.Method("get_acquisition_price", dump_only=True)
    current_price = fields.Method("get_current_price", dump_only=True, allow_none=True)
    min_price = fields.Method("get_min_price", dump_only=True, allow_none=True)
    max_price = fields.Method("get_max_price", dump_only=True, allow_none=True)
    product_image_url = fields.Method("get_product_image_url", dump_only=True)
    inventory_image_url = fields.Method("get_inventory_image_url", dump_only=True)
    tracker_url = fields.Method("get_tracker_url", dump_only=True)

    def get_product_image_url(self, obj):
        return getattr(obj, "_product_image_url", None)

    def get_inventory_image_url(self, obj):
        return getattr(obj, "_inventory_image_url", None)

    def get_acquisition_price(self, obj):
        if obj.purchase_item and obj.purchase_item.unit_price is not None:
            split = obj.purchase_item.split_quantity or 1
            return float(obj.purchase_item.unit_price) / split
        if obj.purchase and obj.purchase.total_amount is not None:
            return float(obj.purchase.total_amount)
        return None

    def get_current_price(self, obj):
        return getattr(obj, "_current_price", None)

    def get_min_price(self, obj):
        return getattr(obj, "_min_price", None)

    def get_max_price(self, obj):
        return getattr(obj, "_max_price", None)

    def get_tracker_url(self, obj):
        product = obj.product
        if not product:
            return None
        trackings = getattr(product, "price_tracking", None)
        if not trackings:
            return None
        t = trackings[0]
        url = t.url
        if not url:
            return None
        ps = t.price_source
        lang = obj.language
        cond = obj.condition
        sep = '&' if '?' in url else '?'
        if ps and ps.language_param and lang and lang.cardmarket_code:
            url += sep + ps.language_param + '=' + str(lang.cardmarket_code)
            sep = '&'
        if ps and ps.condition_param and cond and cond.cardmarket_code:
            url += sep + ps.condition_param + '=' + str(cond.cardmarket_code)
        return url
