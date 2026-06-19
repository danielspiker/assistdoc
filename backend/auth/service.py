"""Regras de negocio de autenticacao: registro, login, bloqueio anti-brute-force."""
import datetime

from sqlalchemy.orm import Session

from backend import config
from backend.auth import passwords
from backend.audit.logger import log_action
from backend.db.models import User

LOCK_MINUTES = 15


def _now() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


class AuthError(Exception):
    """Erro de autenticacao com mensagem segura para o cliente."""


def register(db: Session, email: str, password: str, role: str = "aluno",
             ip: str | None = None) -> User:
    """Cadastra usuario com senha forte. Lança AuthError em caso de problema."""
    email = email.strip().lower()
    if role not in ("aluno", "admin"):
        raise AuthError("Papel invalido.")
    if db.query(User).filter(User.email == email).first():
        raise AuthError("E-mail ja cadastrado.")
    problemas = passwords.validate_strength(password)
    if problemas:
        raise AuthError("Senha fraca: " + "; ".join(problemas))

    user = User(email=email, hashed_password=passwords.hash_password(password), role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    log_action(db, "register", email, f"role={role}", ip)
    return user


def authenticate(db: Session, email: str, password: str, ip: str | None = None) -> User:
    """Valida credenciais. Aplica bloqueio apos N falhas. Lança AuthError se falhar."""
    email = email.strip().lower()
    user = db.query(User).filter(User.email == email).first()

    # Mensagem SEMPRE generica para nao revelar se o e-mail existe nem seu estado
    # (anti-enumeracao). O motivo real fica so no log de auditoria.
    INVALID = "Credenciais invalidas."

    if not user:
        # Gasta o mesmo tempo de bcrypt de um usuario real (anti-timing attack).
        passwords.verify_password(password, passwords.DUMMY_HASH)
        log_action(db, "login_fail", email, "usuario inexistente", ip)
        raise AuthError(INVALID)

    if not user.is_active:
        log_action(db, "login_blocked", email, "conta inativa", ip)
        raise AuthError(INVALID)

    if user.locked_until and user.locked_until > _now().replace(tzinfo=None):
        log_action(db, "login_blocked", email, "conta bloqueada", ip)
        raise AuthError(INVALID)

    if not passwords.verify_password(password, user.hashed_password):
        user.failed_attempts += 1
        if user.failed_attempts >= config.MAX_LOGIN_ATTEMPTS:
            user.locked_until = _now().replace(tzinfo=None) + datetime.timedelta(minutes=LOCK_MINUTES)
            log_action(db, "login_lockout", email,
                       f"{user.failed_attempts} tentativas", ip)
        else:
            log_action(db, "login_fail", email,
                       f"tentativa {user.failed_attempts}", ip)
        db.commit()
        raise AuthError("Credenciais invalidas.")

    # sucesso: zera contadores
    user.failed_attempts = 0
    user.locked_until = None
    db.commit()
    log_action(db, "login_ok", email, None, ip)
    return user
