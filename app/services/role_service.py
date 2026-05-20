from app.repositories.role_repository import RoleRepository
from app.services.crud_service import CrudService


class RoleService(CrudService):
    repository = RoleRepository
