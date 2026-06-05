"""Cria (ou promove) um usuario admin.

Uso:
    python -m backend.create_admin admin@ith.edu.br "SenhaForte@123"
"""
import sys

from backend.db.database import SessionLocal, init_db
from backend.db.models import User
from backend.auth import passwords


def main():
    if len(sys.argv) < 3:
        sys.exit('Uso: python -m backend.create_admin <email> "<senha>"')
    email = sys.argv[1].strip().lower()
    senha = sys.argv[2]

    problemas = passwords.validate_strength(senha)
    if problemas:
        sys.exit("Senha fraca: " + "; ".join(problemas))

    init_db()
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user:
            user.role = "admin"
            user.hashed_password = passwords.hash_password(senha)
            user.is_active = True
            user.failed_attempts = 0
            user.locked_until = None
            acao = "atualizado/promovido"
        else:
            user = User(email=email,
                        hashed_password=passwords.hash_password(senha),
                        role="admin")
            db.add(user)
            acao = "criado"
        db.commit()
        print(f"Admin {acao}: {email}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
