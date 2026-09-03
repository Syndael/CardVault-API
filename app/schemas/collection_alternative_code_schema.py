from marshmallow import Schema, fields


class CollectionAlternativeCodeSchema(Schema):
    id = fields.Int(dump_only=True)
    collection_id = fields.Int(required=True)
    code = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)
