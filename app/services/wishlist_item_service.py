from datetime import datetime, timedelta

from flask import request

from app.database.session import db
from app.models.wishlist_item_model import WishlistItemModel
from app.models.wishlist_notification_model import WishlistNotificationModel
from app.models.wishlist_price_model import WishlistPriceModel
from app.models.product_model import ProductModel
from app.models.collection_model import CollectionModel
from app.models.product_translation_model import ProductTranslationModel
from app.repositories.wishlist_item_repository import WishlistItemRepository
from app.services.crud_service import CrudService
from app.utils.pagination import paginate_query


class WishlistItemService(CrudService):
    repository = WishlistItemRepository

    @classmethod
    def get_by_user(cls, user_id):
        return cls.repository.model.query.filter_by(user_id=user_id).order_by(cls.repository.model.created_at.desc()).all()

    @classmethod
    def get_paginated_by_user(cls, user_id, page, per_page):
        query = cls.repository.model.query.filter_by(user_id=user_id).order_by(cls.repository.model.created_at.desc())

        try:
            language_id = request.args.get("language_id")
        except RuntimeError:
            language_id = None
        if language_id:
            try:
                query = query.filter(cls.repository.model.language_id == int(language_id))
            except ValueError:
                pass

        try:
            condition_id = request.args.get("condition_id")
        except RuntimeError:
            condition_id = None
        if condition_id:
            try:
                query = query.filter(cls.repository.model.condition_id == int(condition_id))
            except ValueError:
                pass

        try:
            card_type_id = request.args.get("card_type_id")
        except RuntimeError:
            card_type_id = None

        try:
            collection_code = request.args.get("collection_code")
        except RuntimeError:
            collection_code = None

        try:
            product_number = request.args.get("product_number")
        except RuntimeError:
            product_number = None

        try:
            product_name = request.args.get("product_name")
        except RuntimeError:
            product_name = None

        needs_product = bool(card_type_id or collection_code or product_number or product_name)
        if needs_product:
            query = query.join(ProductModel)

            if card_type_id:
                try:
                    query = query.filter(ProductModel.product_type_id == int(card_type_id))
                except ValueError:
                    pass

            if collection_code:
                query = query.join(ProductModel.collection).filter(
                    CollectionModel.code.ilike(f"%{collection_code}%")
                )

            if product_number:
                query = query.filter(ProductModel.product_number.ilike(f"%{product_number}%"))

            if product_name:
                query = query.join(ProductModel.translations).filter(
                    ProductTranslationModel.name.ilike(f"%{product_name}%")
                )

        try:
            w_state = request.args.get("w_state")
        except RuntimeError:
            w_state = None
        if w_state:
            query = query.filter(cls.repository.model.w_state == w_state)

        return paginate_query(query, page, per_page)

    @classmethod
    def get_all(cls):
        return cls.repository.model.query.order_by(cls.repository.model.created_at.desc()).all()

    @classmethod
    def get_by_product(cls, product_id):
        return cls.repository.model.query.filter_by(product_id=product_id).all()

    @classmethod
    def get_all_active(cls):
        return cls.repository.model.query.filter(
            WishlistItemModel.target_price.isnot(None),
            WishlistItemModel.w_state == "buscando",
        ).all()

    @classmethod
    def record_price(cls, item_id, price, source=None):
        price_val = float(price) if not isinstance(price, (int, float)) else float(price)
        now = datetime.now()

        record = WishlistPriceModel.query.filter_by(wishlist_item_id=item_id).first()

        if record:
            if record.min_price is not None:
                new_min = min(price_val, float(record.min_price))
                new_max = max(price_val, float(record.max_price))
                min_ts = record.min_price_recorded_at if float(record.min_price) < price_val else now
                max_ts = record.max_price_recorded_at if float(record.max_price) > price_val else now
            else:
                new_min = price_val
                new_max = price_val
                min_ts = now
                max_ts = now

            record.price = price_val
            record.min_price = new_min
            record.max_price = new_max
            record.min_price_recorded_at = min_ts
            record.max_price_recorded_at = max_ts
            record.source = source
            record.recorded_at = now
        else:
            record = WishlistPriceModel(
                wishlist_item_id=item_id,
                price=price_val,
                min_price=price_val,
                max_price=price_val,
                min_price_recorded_at=now,
                max_price_recorded_at=now,
                source=source,
            )
            db.session.add(record)

        db.session.commit()
        return record

    @classmethod
    def get_prices(cls, item_id, limit=20):
        return WishlistPriceModel.query.filter_by(wishlist_item_id=item_id).order_by(WishlistPriceModel.recorded_at.desc()).limit(limit).all()

    @classmethod
    def has_recent_notification(cls, item_id, hours=24):
        since = datetime.now() - timedelta(hours=hours)
        return WishlistNotificationModel.query.filter(
            WishlistNotificationModel.wishlist_item_id == item_id,
            WishlistNotificationModel.notified_at >= since,
        ).first() is not None

    @classmethod
    def create_notification(cls, item_id, notif_type, price):
        notif = WishlistNotificationModel(
            wishlist_item_id=item_id,
            type=notif_type,
            price=price,
        )
        db.session.add(notif)
        db.session.commit()
        return notif
