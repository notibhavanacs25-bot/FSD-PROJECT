from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from app.config import settings


# Password hashing
password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Convert a plain password into a secure password hash."""
    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    """Check whether the submitted password matches the stored hash."""
    return password_hash.verify(
        plain_password,
        hashed_password
    )


# JWT creation
def create_access_token(user_id: str) -> str:

    expiry = datetime.now(timezone.utc) + timedelta(
        minutes=settings.jwt_expire_minutes
    )

    payload = {
        "sub": user_id,
        "exp": expiry
    }

    token = jwt.encode(
        payload,
        settings.jwt_secret,
        algorithm="HS256"
    )

    return token


# JWT verification
def decode_access_token(token: str) -> dict:

    payload = jwt.decode(
        token,
        settings.jwt_secret,
        algorithms=["HS256"]
    )

    return payload