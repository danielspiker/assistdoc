"""Dependencias de autenticacao/autorizacao para o FastAPI."""
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from backend.auth.jwt_handler import decode_token, JWTError
from backend.db.database import get_db
from backend.db.models import User

bearer = HTTPBearer(auto_error=True)

# Blocklist de jti revogados (logout). Em memoria: simples e suficiente para
# tokens de 15min; zera ao reiniciar o servidor.
_revoked_jti: set[str] = set()


def revoke(jti: str) -> None:
    _revoked_jti.add(jti)


def get_current_user(
    cred: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    """Valida o JWT e devolve o usuario logado. 401 se invalido/expirado/revogado."""
    creds_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalido ou expirado.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(cred.credentials)
    except JWTError:
        raise creds_exc

    if payload.get("jti") in _revoked_jti:
        raise creds_exc

    email = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()
    if not user or not user.is_active:
        raise creds_exc
    return user


def require_role(*roles: str):
    """Factory de dependencia: exige que o usuario tenha um dos papeis dados."""
    def checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado: permissao insuficiente.",
            )
        return user
    return checker


def client_ip(request: Request) -> str | None:
    """IP do cliente (considera proxy via X-Forwarded-For)."""
    fwd = request.headers.get("x-forwarded-for")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.client.host if request.client else None
