from app.models.user_model import UserModel
from app.repositories.crud_repository import CrudRepository


class UserRepository(CrudRepository):
    model = UserModel
    order_by = (UserModel.username,)
    create_fields = (
        "username",
        "email",
        "password_hash",
        "display_name",
        "is_active",
        "is_email_verified",
        "telegram_id",
        "last_login_at",
        "password_changed_at"
    )
    update_fields = create_fields
