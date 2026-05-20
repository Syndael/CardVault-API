from app.repositories.user_repository import UserRepository
from app.services.crud_service import CrudService


class UserService(CrudService):
    repository = UserRepository
