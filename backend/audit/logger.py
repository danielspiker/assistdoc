"""Auditoria: registra acoes sensiveis no banco (user, acao, detalhe, IP, timestamp)."""
from sqlalchemy.orm import Session

from backend.db.models import AuditLog


def log_action(db: Session, action: str, user_email: str | None = None,
               detail: str | None = None, ip: str | None = None) -> None:
    """Grava um evento de auditoria. Nao quebra o fluxo se falhar."""
    try:
        db.add(AuditLog(action=action, user_email=user_email, detail=detail, ip=ip))
        db.commit()
    except Exception:
        db.rollback()
