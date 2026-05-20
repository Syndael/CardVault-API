from app.repositories.user_session_repository import UserSessionRepository
from app.services.crud_service import CrudService


class UserSessionService(CrudService):
    repository = UserSessionRepository
