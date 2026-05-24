from marshmallow import Schema, fields

from app.schemas.fields import BitBool
from app.schemas.type_schema import TypeSchema


class CollectionSchema(Schema):
    id = fields.Int(dump_only=True)
    card_type_id = fields.Int(load_only=True)
    code = fields.Str(required=True)
    is_manual = BitBool()
    release_date = fields.Date(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    card_type = fields.Nested(
        TypeSchema,
        dump_only=True
    )
    name = fields.Method("get_name", dump_only=True)
    name_alter = fields.Method("get_name_alter", dump_only=True)

    def _best_translation(self, obj):
        if not obj.translations:
            return None
        return sorted(
            obj.translations,
            key=lambda t: t.language.priority_order if t.language else 999
        )[0]

    def get_name(self, obj):
        best = self._best_translation(obj)
        return best.name if best else None

    def get_name_alter(self, obj):
        best = self._best_translation(obj)
        return best.name_alter if best and best.name_alter else None
