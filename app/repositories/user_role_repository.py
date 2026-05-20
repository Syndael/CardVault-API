from app.models.user_role_model import UserRoleModel
from app.repositories.crud_repository import CrudRepository


class UserRoleRepository(CrudRepository):
    model = UserRoleModel
    order_by = (UserRoleModel.user_id, UserRoleModel.role_id)
    create_fields = (
        "user_id",
        "role_id"
    )
    update_fields = ()

    @classmethod
    def get_by_id(cls, entity_id):
        user_id, role_id = entity_id
        return cls.model.query.get((user_id, role_id))
