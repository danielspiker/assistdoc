"""Criacao e validacao de tokens JWT (python-jose)."""
import datetime
import uuid

from jose import jwt, JWTError

from backend import config

ALGORITHM = "HS256"


def create_access_token(email: str, role: str) -> str:
    """Gera JWT com expiracao curta (config.JWT_EXPIRE_MINUTES) e jti unico."""
    now = datetime.datetime.now(datetime.timezone.utc)
    payload = {
        "sub": email,
        "role": role,
        "jti": str(uuid.uuid4()),
        "iat": now,
        "exp": now + datetime.timedelta(minutes=config.JWT_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, config.JWT_SECRET, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    """Decodifica e valida o token. Lança JWTError se invalido/expirado."""
    return jwt.decode(token, config.JWT_SECRET, algorithms=[ALGORITHM])


__all__ = ["create_access_token", "decode_token", "JWTError"]
