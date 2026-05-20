import hashlib
import os
import secrets
from datetime import datetime, timedelta
from functools import wraps

from flask import request, g, jsonify
from sqlalchemy import or_

from app.database.session import db
from app.models.user_model import UserModel
from app.models.user_session_model import UserSessionModel

try:
    # werkzeug is available in Flask environments
    from werkzeug.security import check_password_hash
except Exception:  # pragma: no cover - fallback
    def check_password_hash(stored, plain):
        # naive fallback: compare directly (not secure). This is only
        # a fallback to avoid hard failure if werkzeug isn't present.
        return stored == plain

SESSION_EXPIRES_DAYS = int(os.getenv("SESSION_EXPIRES_DAYS", "7"))


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _generate_token() -> str:
    # 32 bytes -> 64 hex chars
    return secrets.token_hex(32)


def login_user(identifier: str, password: str, user_agent: str = None, ip_address: str = None):
    """Authenticate a user and create a session.

    Returns (token, session_model, user) on success or (None, None, None) on failure.
    """
    user = (
        UserModel.query
        .filter(or_(UserModel.username == identifier, UserModel.email == identifier))
        .filter_by(is_active=True)
        .first()
    )

    if not user:
        return None, None, None

    if not check_password_hash(user.password_hash, password):
        return None, None, None

    token = _generate_token()
    token_hash = _hash_token(token)
    expires_at = datetime.utcnow() + timedelta(days=SESSION_EXPIRES_DAYS)

    session = UserSessionModel(
        user_id=user.id,
        token_hash=token_hash,
        user_agent=(user_agent or "")[:255],
        ip_address=(ip_address or "")[:45],
        expires_at=expires_at,
    )

    db.session.add(session)
    db.session.commit()

    return token, session, user


def _get_token_from_header():
    auth = request.headers.get("Authorization") or ""
    if not auth:
        return None
    parts = auth.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    return None


def get_user_from_token(token: str):
    if not token:
        return None
    token_hash = _hash_token(token)
    now = datetime.utcnow()
    session = (
        UserSessionModel.query
        .filter_by(token_hash=token_hash)
        .filter(UserSessionModel.revoked_at.is_(None))
        .filter(UserSessionModel.expires_at > now)
        .first()
    )

    if not session:
        return None

    return session.user


def revoke_token(token: str) -> bool:
    if not token:
        return False
    token_hash = _hash_token(token)
    session = UserSessionModel.query.filter_by(token_hash=token_hash).first()
    if not session:
        return False
    session.revoked_at = datetime.utcnow()
    db.session.commit()
    return True


def require_auth(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = _get_token_from_header()
        if not token:
            return jsonify({"message": "Unauthorized"}), 401
        user = get_user_from_token(token)
        if not user:
            return jsonify({"message": "Unauthorized"}), 401
        g.current_user = user
        g.current_token = token
        return func(*args, **kwargs)

    return wrapper


def require_role(*role_names):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            token = _get_token_from_header()
            if not token:
                return jsonify({"message": "Unauthorized"}), 401
            user = get_user_from_token(token)
            if not user:
                return jsonify({"message": "Unauthorized"}), 401
            user_roles = [ur.role.name for ur in getattr(user, "user_roles", [])]
            if not any(r in user_roles for r in role_names):
                return jsonify({"message": "Forbidden"}), 403
            g.current_user = user
            return func(*args, **kwargs)

        return wrapper

    return decorator


def has_any_role(*role_names):
    user = getattr(g, "current_user", None)
    if not user:
        return False
    user_roles = [ur.role.name for ur in getattr(user, "user_roles", [])]
    return any(r in user_roles for r in role_names)


def get_token_from_header():
    """Public wrapper used by other modules to inspect the header."""
    return _get_token_from_header()


def get_user_from_request():
    token = _get_token_from_header()
    return get_user_from_token(token) if token else None
