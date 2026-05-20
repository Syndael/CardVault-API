from marshmallow import Schema, fields

from app.schemas.role_schema import RoleSchema
from app.schemas.user_schema import UserSchema


class UserRoleSchema(Schema):
    user_id = fields.Int(load_only=True, required=True)
    role_id = fields.Int(load_only=True, required=True)
    created_at = fields.DateTime(dump_only=True)
    user = fields.Nested(UserSchema, dump_only=True)
    role = fields.Nested(RoleSchema, dump_only=True)
