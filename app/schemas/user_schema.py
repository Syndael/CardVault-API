from marshmallow import Schema, fields


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    email = fields.Email(required=True)
    password_hash = fields.Str(load_only=True, required=True)
    display_name = fields.Str(allow_none=True)
    is_active = fields.Bool(load_default=True)
    is_email_verified = fields.Bool(load_default=False)
    last_login_at = fields.DateTime(allow_none=True)
    password_changed_at = fields.DateTime(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
