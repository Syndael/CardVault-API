from app.repositories.price_source_repository import PriceSourceRepository
from app.services.crud_service import CrudService


class PriceSourceService(CrudService):
    repository = PriceSourceRepository
