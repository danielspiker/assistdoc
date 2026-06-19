"""Hash de senha (bcrypt) e validacao de senha forte.

Usa bcrypt diretamente (evita o conflito passlib 1.7 + bcrypt 5.x).
"""
import bcrypt

BCRYPT_ROUNDS = 12          # custo minimo exigido pelo enunciado
MIN_LEN = 12
_BCRYPT_MAX_BYTES = 72      # limite do algoritmo bcrypt


def hash_password(plain: str) -> str:
    """Gera o hash bcrypt (custo 12) de uma senha."""
    pw = plain.encode("utf-8")[:_BCRYPT_MAX_BYTES]
    return bcrypt.hashpw(pw, bcrypt.gensalt(rounds=BCRYPT_ROUNDS)).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Confere a senha contra o hash."""
    pw = plain.encode("utf-8")[:_BCRYPT_MAX_BYTES]
    try:
        return bcrypt.checkpw(pw, hashed.encode("utf-8"))
    except ValueError:
        return False


# Hash fixo usado para gastar o mesmo tempo de bcrypt quando o usuario NAO existe,
# evitando enumeracao de contas por diferenca de tempo de resposta (timing attack).
DUMMY_HASH = hash_password("timing-uniforme-placeholder")


def validate_strength(plain: str) -> list[str]:
    """Devolve lista de problemas da senha. Vazia = senha forte.

    Regras (enunciado): >= 12 chars, letra maiuscula, numero e simbolo.
    """
    problemas = []
    if len(plain) < MIN_LEN:
        problemas.append(f"deve ter ao menos {MIN_LEN} caracteres")
    if not any(c.isupper() for c in plain):
        problemas.append("deve conter ao menos uma letra maiuscula")
    if not any(c.isdigit() for c in plain):
        problemas.append("deve conter ao menos um numero")
    if not any(not c.isalnum() for c in plain):
        problemas.append("deve conter ao menos um simbolo")
    return problemas
