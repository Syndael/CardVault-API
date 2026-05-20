from app.models.user_session_model import UserSessionModel
from app.repositories.crud_repository import CrudRepository


class UserSessionRepository(CrudRepository):
    model = UserSessionModel
    order_by = (UserSessionModel.created_at.desc(),)
    create_fields = (
        "user_id",
        "token_hash",
        "user_agent",
        "ip_address",
        "expires_at",
        "revoked_at"
    )
    update_fields = (
        "expires_at",
        "revoked_at"
    )
