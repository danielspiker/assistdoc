"""AssistDoc — API FastAPI.

Rodar: uvicorn backend.main:app --port 8001
Docs (Swagger): http://localhost:8001/docs
"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, Request, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from backend import config
from backend.rag import retrieve, long_context, router
from backend.rag.loaders import list_documents, SUPPORTED_EXTS
from backend.rag.ingest import ingest_file
from backend.db.database import get_db, init_db
from backend.db.models import User, AuditLog
from backend.auth import service, jwt_handler
from backend.auth.deps import get_current_user, require_role, revoke, client_ip
from backend.audit.logger import log_action


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()  # cria tabelas se nao existirem
    yield


app = FastAPI(
    title="AssistDoc",
    description="Assistente inteligente de documentos academicos (RAG + Long Context)",
    version="0.3.0",
    lifespan=lifespan,
)
bearer = HTTPBearer(auto_error=True)


# --- Schemas ----------------------------------------------------------------

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=12)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str


class AskRequest(BaseModel):
    question: str = Field(..., min_length=3, examples=["Quantas faltas posso ter?"])
    k: int | None = Field(None, ge=1, le=20)


class AskDocRequest(BaseModel):
    question: str = Field(..., min_length=3)
    document: str | None = None


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=3)
    document: str | None = None


class Source(BaseModel):
    source: str | None = None
    chunk: int | None = None
    page: int | None = None
    snippet: str | None = None


class Answer(BaseModel):
    answer: str
    mode: str | None = None
    sources: list[Source] = []
    documents: list[str] = []
    tokens: dict | None = None


# --- Saude / publico --------------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok", "service": "assistdoc"}


# --- Autenticacao -----------------------------------------------------------

@app.post("/auth/register", response_model=TokenResponse)
def register(req: RegisterRequest, request: Request, db: Session = Depends(get_db)):
    """Cadastro publico (cria sempre perfil 'aluno')."""
    try:
        user = service.register(db, req.email, req.password, role="aluno",
                                ip=client_ip(request))
    except service.AuthError as e:
        raise HTTPException(status_code=400, detail=str(e))
    token = jwt_handler.create_access_token(user.email, user.role)
    return TokenResponse(access_token=token, role=user.role)


@app.post("/auth/login", response_model=TokenResponse)
def login(req: LoginRequest, request: Request, db: Session = Depends(get_db)):
    """Login: devolve JWT (exp 15min). Bloqueia apos N tentativas erradas."""
    try:
        user = service.authenticate(db, req.email, req.password, ip=client_ip(request))
    except service.AuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    token = jwt_handler.create_access_token(user.email, user.role)
    return TokenResponse(access_token=token, role=user.role)


@app.post("/auth/logout")
def logout(cred: HTTPAuthorizationCredentials = Depends(bearer),
           user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Invalida o token atual no servidor (blocklist do jti)."""
    try:
        payload = jwt_handler.decode_token(cred.credentials)
        if payload.get("jti"):
            revoke(payload["jti"])
    except jwt_handler.JWTError:
        pass
    log_action(db, "logout", user.email)
    return {"detail": "Logout efetuado."}


@app.get("/auth/me")
def me(user: User = Depends(get_current_user)):
    return {"email": user.email, "role": user.role}


# --- Documentos / RAG (exige login) -----------------------------------------

@app.get("/documents")
def documents(user: User = Depends(get_current_user)):
    return {"documents": list_documents()}


@app.post("/ask", response_model=Answer)
def ask(req: AskRequest, user: User = Depends(get_current_user)):
    """RAG: busca semantica nos chunks e responde citando a fonte."""
    out = retrieve.answer(req.question, k=req.k)
    out["mode"] = "rag"
    return out


@app.post("/ask-doc", response_model=Answer)
def ask_doc(req: AskDocRequest, user: User = Depends(get_current_user)):
    """Long Context: injeta o documento inteiro (ou a base) no prompt."""
    return long_context.answer(req.question, req.document)


@app.post("/chat", response_model=Answer)
def chat(req: ChatRequest, user: User = Depends(get_current_user)):
    """Roteamento automatico RAG vs Long Context (RF07)."""
    return router.answer(req.question, req.document)


# --- Painel administrativo (somente admin) ----------------------------------

@app.post("/admin/ingest")
def admin_ingest(file: UploadFile = File(...), request: Request = None,
                 admin: User = Depends(require_role("admin")),
                 db: Session = Depends(get_db)):
    """Upload + indexação de um documento (PDF/DOCX/TXT). Só admin."""
    nome = os.path.basename(file.filename or "")
    ext = os.path.splitext(nome)[1].lower()
    if ext not in SUPPORTED_EXTS:
        raise HTTPException(400, f"Formato nao suportado: {ext}. Use {SUPPORTED_EXTS}.")

    os.makedirs(config.STORAGE_DIR, exist_ok=True)
    destino = os.path.join(config.STORAGE_DIR, nome)
    with open(destino, "wb") as f:
        f.write(file.file.read())

    try:
        n_chunks = ingest_file(destino)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(500, f"Falha ao indexar: {e}")

    log_action(db, "upload_doc", admin.email, f"{nome} ({n_chunks} chunks)",
               client_ip(request))
    return {"document": nome, "chunks": n_chunks}


@app.get("/admin/audit")
def admin_audit(limit: int = 50, admin: User = Depends(require_role("admin")),
                db: Session = Depends(get_db)):
    """Últimos eventos de auditoria. Só admin."""
    rows = (db.query(AuditLog).order_by(AuditLog.timestamp.desc())
            .limit(min(limit, 500)).all())
    return {"logs": [
        {"timestamp": r.timestamp.isoformat(), "user": r.user_email,
         "action": r.action, "detail": r.detail, "ip": r.ip}
        for r in rows
    ]}


@app.get("/admin/users")
def admin_users(admin: User = Depends(require_role("admin")),
                db: Session = Depends(get_db)):
    """Lista usuários. Só admin."""
    rows = db.query(User).order_by(User.created_at.desc()).all()
    return {"users": [
        {"email": u.email, "role": u.role, "is_active": u.is_active,
         "failed_attempts": u.failed_attempts,
         "locked": bool(u.locked_until)}
        for u in rows
    ]}


@app.post("/admin/users/{email}/active")
def admin_set_active(email: str, active: bool,
                     admin: User = Depends(require_role("admin")),
                     request: Request = None, db: Session = Depends(get_db)):
    """Ativa/desativa um usuário e destrava bloqueio. Só admin."""
    user = db.query(User).filter(User.email == email.strip().lower()).first()
    if not user:
        raise HTTPException(404, "Usuario nao encontrado.")
    user.is_active = active
    if active:  # reativar tambem destrava
        user.failed_attempts = 0
        user.locked_until = None
    db.commit()
    log_action(db, "user_set_active", admin.email,
               f"{email} -> active={active}", client_ip(request))
    return {"email": user.email, "is_active": user.is_active}
