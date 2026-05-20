from marshmallow import Schema, fields

from app.schemas.user_schema import UserSchema


class UserSessionSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(load_only=True, required=True)
    token_hash = fields.Str(load_only=True, required=True)
    user_agent = fields.Str(allow_none=True)
    ip_address = fields.Str(allow_none=True)
    expires_at = fields.DateTime(required=True)
    revoked_at = fields.DateTime(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    user = fields.Nested(UserSchema, dump_only=True)
