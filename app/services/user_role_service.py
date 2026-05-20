from app.repositories.user_role_repository import UserRoleRepository
from app.services.crud_service import CrudService


class UserRoleService(CrudService):
    repository = UserRoleRepository

    @classmethod
    def get_by_id(cls, user_id, role_id):
        return cls.repository.get_by_id((user_id, role_id))

    @classmethod
    def delete(cls, user_id, role_id):
        entity = cls.repository.get_by_id((user_id, role_id))
        if not entity:
            return None
        cls.repository.delete(entity)
        return True
