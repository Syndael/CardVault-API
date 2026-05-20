from flask import g

from app.repositories.purchase_repository import PurchaseRepository
from app.services.crud_service import CrudService


def _is_admin():
    user = getattr(g, "current_user", None)
    if not user:
        return False
    return any(ur.role.name == "admin" for ur in getattr(user, "user_roles", []))


def _can_access(entity):
    if not entity:
        return False
    if _is_admin():
        return True
    user = getattr(g, "current_user", None)
    if not user:
        return False
    return entity.user_id == user.id


class PurchaseService(CrudService):
    repository = PurchaseRepository

    @classmethod
    def create(cls, data):
        user = getattr(g, "current_user", None)
        if user:
            data["user_id"] = user.id
        return cls.repository.create(data)

    @classmethod
    def update(cls, entity_id, data):
        entity = cls.repository.get_by_id(entity_id)
        if not entity:
            return None
        if not _can_access(entity):
            return None
        return cls.repository.update(entity, data)

    @classmethod
    def delete(cls, entity_id):
        entity = cls.repository.get_by_id(entity_id)
        if not entity:
            return None
        if not _can_access(entity):
            return None
        cls.repository.delete(entity)
        return True
