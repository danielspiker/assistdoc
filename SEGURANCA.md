# Segurança do AssistDoc

Documento de segurança do projeto. Cobre **OWASP Top 10 (2021)** e a modelagem
de ameaças **STRIDE** sobre a arquitetura. Cada item aponta o código real onde
a mitigação está implementada.

---

## 1. Arquitetura e superfície de ataque

```
[Cliente Streamlit] --HTTPS/JWT--> [FastAPI] --SQL--> [SQLite]
                                       |
                                       +--> [Chroma]   (vetores)
                                       +--> [Ollama]   (LLM local, 127.0.0.1)
                                       +--> [Storage]  (uploads PDF/DOCX/TXT)
```

Componentes que processam input externo:
- **API** (rotas em `backend/main.py`): porta de entrada de tudo.
- **Auth** (`backend/auth/`): credenciais, tokens, RBAC.
- **Upload de documentos** (`/admin/ingest`): arquivo binário do usuário.
- **LLM** (Ollama): recebe perguntas do usuário + trechos de documentos.
- **Banco** (SQLite via SQLAlchemy ORM): persistência.

---

## 2. Princípios aplicados

- **Defesa em profundidade:** validação no frontend (mascara senha, tipos),
  validação no Pydantic (schema), regra de negócio no `service.py`, RBAC no
  `deps.py`, ORM previne SQLi e log de auditoria por trás.
- **Menor privilégio:** registro público só cria `aluno`. Admin só por seed
  (`create_admin.py`).
- **Tríade CIA:**
  - *Confidencialidade:* senha em bcrypt; JWT assinado; chave em `.env` fora do
    Git; chat exige login.
  - *Integridade:* tokens assinados (HS256); SQLAlchemy parametriza queries; ORM
    valida tipos.
  - *Disponibilidade:* bloqueio anti-brute-force; token curto (15min);
    `try/except` no upload e auditoria pra não derrubar o servidor.

---

## 3. OWASP Top 10 (2021) — mitigações

### A01:2021 — Broken Access Control
**Risco:** usuário comum acessar rota de admin; manipular `id`/`email` para
afetar outros usuários.
**Mitigações:**
- RBAC em camada de dependência (`backend/auth/deps.py::require_role`). Todas
  as rotas `/admin/*` exigem `require_role("admin")`. Aluno autenticado recebe
  **HTTP 403** (testado em /admin/audit).
- Frontend esconde a aba "Admin" para alunos (`_is_admin()` em `frontend/app.py`).
- Token traz `role` mas o servidor **revalida** consultando o usuário no banco a
  cada request (`get_current_user`), evitando privilégio congelado em token.

### A02:2021 — Cryptographic Failures
**Risco:** senha em texto puro; segredo do JWT exposto; HTTPS ausente.
**Mitigações:**
- Senha guardada como **bcrypt custo 12** (`backend/auth/passwords.py`), nunca em
  texto puro. Hash incluso ao salvar (`service.register`).
- JWT assinado com HS256 e segredo em `.env` (fora do Git: `.gitignore` exclui
  `.env`). Em produção, segredo deve vir de gestor de segredos.
- Em dev usamos HTTP localhost; em produção: TLS obrigatório (uvicorn atrás de
  Nginx/Caddy com cert).

### A03:2021 — Injection
**Risco:** SQL injection; injeção de prompt no LLM; path traversal no upload.
**Mitigações:**
- **SQL:** SQLAlchemy ORM com binds parametrizados. Nenhuma query construída
  por concatenação.
- **Path traversal:** `os.path.basename(file.filename)` em `/admin/ingest`
  remove qualquer `..\` ou caminho absoluto antes de salvar.
- **Tipo:** `SUPPORTED_EXTS` whitelist (.txt/.pdf/.docx).
- **Prompt injection:** prompt de sistema instrui o LLM a responder *somente*
  com base nos trechos fornecidos (`retrieve.py::SYSTEM_PROMPT`,
  `long_context.py::SYSTEM_PROMPT`). Trechos recuperados são tratados como
  dados, não como instruções; LLM roda local (sem chamadas externas).

### A04:2021 — Insecure Design
**Risco:** falhas de modelagem — ex.: ausência de rate limit, falta de log.
**Mitigações:**
- Bloqueio anti-brute-force por design (`config.MAX_LOGIN_ATTEMPTS=5`,
  `LOCK_MINUTES=15` em `service.py`).
- Auditoria desde o desenho (`audit/logger.py`) chamada em pontos sensíveis:
  register, login_ok/login_fail/login_lockout, logout, upload_doc,
  user_set_active.
- Tokens curtos (15min) reduzem janela de comprometimento.

### A05:2021 — Security Misconfiguration
**Risco:** segredo padrão em produção, debug ligado, CORS aberto.
**Mitigações:**
- `.env.example` traz segredo placeholder `troque-isto-por-uma-chave-longa-aleatoria`
  — o real só no `.env` local.
- `uvicorn` sem `--reload` em produção; FastAPI não vaza stack trace ao cliente
  (Starlette responde 500 genérico — o detalhe vai só pro log).
- CORS não habilitado por enquanto (front e API mesma origem). Quando for
  separar, configurar `CORSMiddleware` com origem específica.

### A06:2021 — Vulnerable and Outdated Components
**Risco:** dependências com CVE.
**Mitigações:**
- Versões pinadas em `requirements.txt` (faixas controladas: `fastapi==0.115.*`).
- Plano: rodar `pip-audit` periodicamente.
- Nota dependência: `passlib 1.7.4` quebra com `bcrypt >= 4.1` (CVE não, mas
  bug). Optamos por usar `bcrypt` diretamente, sem passlib.

### A07:2021 — Identification and Authentication Failures
**Risco:** senha fraca; credenciais previsíveis; sessão eterna.
**Mitigações:**
- Política de senha forte em `passwords.validate_strength`: ≥12 caracteres,
  letra maiúscula, número e símbolo.
- bcrypt custo 12 (≥12 conforme enunciado).
- JWT com `exp=15min` e `jti` único; logout invalida o `jti` na blocklist
  (`auth/deps.py::revoke`).
- Bloqueio temporário após 5 tentativas (`service.authenticate`).
- Mensagem de erro genérica ("Credenciais invalidas.") para não revelar se o
  e-mail existe (mitiga user enumeration).

### A08:2021 — Software and Data Integrity Failures
**Risco:** token forjado; dependências baixadas sem verificação.
**Mitigações:**
- JWT assinado (HS256). Servidor valida a assinatura no `decode_token`.
- pip usa HTTPS + checksums do PyPI por padrão. Documentamos no PLANO o uso
  de `--trusted-host` apenas em ambiente local com proxy SSL interceptando.

### A09:2021 — Security Logging and Monitoring Failures
**Risco:** ataque passa despercebido; ausência de trilha de auditoria.
**Mitigações:**
- Tabela `audit_logs` (`backend/db/models.py`) com timestamp UTC, e-mail, ação,
  detalhe, IP (`X-Forwarded-For` priorizado em `client_ip`).
- Eventos cobertos: `register`, `login_ok`, `login_fail`, `login_blocked`,
  `login_lockout`, `logout`, `upload_doc`, `user_set_active`.
- Painel admin (`/admin/audit`) consulta os últimos eventos para revisão.

### A10:2021 — Server-Side Request Forgery (SSRF)
**Risco:** servidor convidado a buscar URL controlada pelo atacante.
**Mitigações:**
- Nenhuma rota da aplicação aceita URL como input. Upload é arquivo direto
  (multipart). Ollama é fixo em `127.0.0.1:11434` (config).
- Se evoluir para crawler/fetch externo, aplicar allowlist de host.

---

## 4. Modelagem de ameaças — STRIDE

Para cada componente da arquitetura, ameaças mapeadas pela técnica STRIDE
(Spoofing, Tampering, Repudiation, Information disclosure, Denial of service,
Elevation of privilege).

### 4.1 API FastAPI (rotas)

| Cat. | Ameaça | Mitigação |
|------|--------|-----------|
| **S**poofing | Usuário se passar por outro com token roubado | JWT 15min + jti + blocklist no logout |
| **T**ampering | Cliente altera `role` no token | HS256 assinado; servidor revalida no banco a cada request |
| **R**epudiation | Usuário nega ter feito uma ação | Auditoria com timestamp, user, IP em cada ação sensível |
| **I**nfo. disclosure | Stack trace expõe estrutura interna | Starlette retorna 500 genérico ao cliente; detalhe só no log |
| **D**enial of service | Flood de logins/perguntas | Bloqueio anti-brute-force; token curto; LLM local com fila do Ollama |
| **E**oP | Aluno acessa rota admin | `require_role("admin")` em todas as rotas `/admin/*` |

### 4.2 Banco (SQLite)

| Cat. | Ameaça | Mitigação |
|------|--------|-----------|
| **S** | App fingir ser outro app no DB | Banco local, acesso só pelo processo do FastAPI |
| **T** | SQL injection corrompendo registros | ORM SQLAlchemy parametriza tudo; nenhuma query string concatenada |
| **R** | Apagar trilha de auditoria | Apenas admin (e por enquanto não há rota de delete em `audit_logs`) |
| **I** | Vazamento do `.db` | `.gitignore` exclui `*.db`; em produção, criptografia em repouso |
| **D** | Disco cheio por flood de logs | Logs por evento curto; revisão periódica |
| **E** | Escalar de leitor para escritor no DB | Não aplicável (única sessão, mesma conexão) |

### 4.3 LLM (Ollama)

| Cat. | Ameaça | Mitigação |
|------|--------|-----------|
| **S** | LLM de terceiro injetar conteúdo malicioso | Modelo local Ollama em `127.0.0.1`; sem chamada externa |
| **T** | Prompt injection alterar instruções do sistema | System prompt restritivo ("apenas com base nos trechos"); contexto = dado, não instrução; resposta segue "não encontrei" se fora |
| **R** | LLM gerar conteúdo que o user nega ter solicitado | Pergunta original fica no log via `/ask` (poderia ser estendida ao audit) |
| **I** | Resposta vazar dados sensíveis de outros docs | RAG restringe ao retrieve (top-k); admin controla quais docs entram |
| **D** | Prompt muito longo trava o Ollama | `num_ctx=8192` cap; LC limita doc grande via roteador (`router.py`) |
| **E** | LLM convencer o app a executar algo | App só recebe texto; nenhuma ação executiva derivada do output |

### 4.4 Upload de documentos

| Cat. | Ameaça | Mitigação |
|------|--------|-----------|
| **S** | Aluno fazer upload se passando por admin | RBAC: `/admin/ingest` exige role admin |
| **T** | Upload de arquivo malicioso (PDF com payload) | Whitelist de extensão; processamento por pypdf/docx2txt (parsers maduros); arquivo isolado em `./storage/` |
| **R** | Admin nega ter subido conteúdo indevido | `audit_logs` registra `upload_doc` com user, IP, nome do arquivo, nº chunks |
| **I** | Conteúdo do upload exposto a alunos sem direito | Cada chunk é metadado em Chroma; futura granularidade por papel é possível |
| **D** | Upload gigante esgota disco/RAM | Tamanho razoável (não há limite explícito hoje — *melhoria sugerida:* `Content-Length` limit) |
| **E** | Path traversal escreve fora de `./storage/` | `os.path.basename` no nome antes de salvar |

### 4.5 Frontend Streamlit

| Cat. | Ameaça | Mitigação |
|------|--------|-----------|
| **S** | Token roubado via XSS | Streamlit renderiza markdown sem executar JS injetado; token em `st.session_state` (memória do processo, não localStorage) |
| **T** | User edita HTML para liberar aba admin | UI esconde aba admin, mas backend é a fonte de verdade (403) |
| **R** | Mensagem nega ter sido enviada | Cada `/ask` chega no servidor com user identificado pelo JWT |
| **I** | Histórico de chat persistido sem querer | `session_state` é em memória; "Limpar conversa" limpa |
| **D** | Loops de chat travam UI | Timeout 180s; spinner com feedback |
| **E** | Aluno ativa "Admin" no UI | Mesmo se conseguir, todas as rotas backend dão 403 |

---

## 5. Pendências e melhorias futuras

- **HTTPS/TLS** obrigatório em produção (reverse proxy).
- **Rate limit por IP** nas rotas públicas (`/auth/login`, `/auth/register`),
  além do bloqueio por conta.
- **Limite de tamanho** no upload (`Content-Length`).
- **SAST** com `bandit` integrado ao CI.
- **DAST** com `OWASP ZAP` em ambiente de homologação.
- **Refresh tokens** se a UX exigir sessão longa (hoje login a cada 15min).
- **Rotação do segredo JWT** periódica.
- **Segredos via cofre** (não `.env`) em produção.

---

## 6. Mapa código ↔ controle

| Controle | Arquivo |
|----------|---------|
| Hash bcrypt + senha forte | `backend/auth/passwords.py` |
| JWT emissão/validação | `backend/auth/jwt_handler.py` |
| Login + bloqueio | `backend/auth/service.py` |
| Dependências auth (RBAC, blocklist, IP) | `backend/auth/deps.py` |
| Auditoria | `backend/audit/logger.py`, `backend/db/models.py::AuditLog` |
| Rotas auth e admin (RBAC ativo) | `backend/main.py` |
| Bootstrap de admin | `backend/create_admin.py` |
| `.gitignore` (segredo + db fora) | `.gitignore` |
