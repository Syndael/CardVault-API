from flask import g
from werkzeug.exceptions import BadRequest

import app.auth as auth
from app.models.user_model import UserModel
from app.repositories.purchase_repository import PurchaseRepository
from app.services.crud_service import CrudService


def _can_access(entity):
    if not entity:
        return False
    if auth.has_any_role("admin"):
        return True
    user = getattr(g, "current_user", None)
    if not user:
        return False
    return entity.user_id == user.id


class PurchaseService(CrudService):
    repository = PurchaseRepository

    @classmethod
    def create(cls, data):
        telegram_id = data.pop("telegram_id", None)
        if telegram_id:
            user = UserModel.query.filter(UserModel.telegram_id == str(telegram_id)).first()
            if not user:
                raise BadRequest(f"No hay un usuario web vinculado al ID de Telegram {telegram_id}")
            data["user_id"] = user.id
        else:
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
