"""Conexao SQLite via SQLAlchemy 2.0."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from backend import config

engine = create_engine(
    f"sqlite:///{config.SQLITE_PATH}",
    connect_args={"check_same_thread": False},  # necessario com FastAPI/threadpool
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    """Dependencia FastAPI: cede uma sessao e fecha ao fim da request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Cria as tabelas (idempotente)."""
    from backend.db import models  # noqa: F401  garante registro dos modelos
    Base.metadata.create_all(engine)
