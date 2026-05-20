from app.repositories.product_repository import ProductRepository
from app.services.crud_service import CrudService


class ProductService(CrudService):
    repository = ProductRepository
