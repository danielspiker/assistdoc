# AssistDoc

Assistente inteligente de documentos academicos. Responde perguntas em linguagem
natural sobre regimento, manual do aluno e politicas da instituicao, citando a
fonte (documento + pagina). Usa **RAG** + **Long Context**.

Projeto cobre as disciplinas:
- **Desenvolver Sistemas Inteligentes (IA):** pipeline RAG + Long Context.
- **Desenvolver Sistemas Seguros (SEC):** auth JWT, RBAC, auditoria, OWASP.

## Apresentação em vídeo
https://youtu.be/8Jd07g4r7AA

## Grupo
- Daniel Marques do Nascimento — 2415050075
- Gabriel Castro C. J. Mamede — 2415050064
- José Willianson Santos Dantas — 2415050060
- Nicholas Almeida Ramirez Emery — 2415050077
- Yveen Barbosa Nóbrega — 2415050069

## Stack
Python · FastAPI · Ollama (LLM local) · LangChain · Chroma (Vector DB) · Streamlit · SQLite

## Setup

```bash
# 1. Ambiente virtual
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/Mac

# 2. Dependencias
pip install -r requirements.txt

# 3. Config
copy .env.example .env        # Windows  (cp no Linux)
# editar .env — defina um JWT_SECRET forte:
#   python -c "import secrets; print(secrets.token_urlsafe(48))"

# 4. Ollama (modelos locais) — https://ollama.com
ollama pull qwen2.5            # LLM da aplicacao
ollama pull bge-m3            # embeddings

# 5. Indexar a base de documentos
python -m backend.rag.ingest

# 6. Criar o primeiro admin
python -m backend.create_admin admin@ith.edu.br "Admin@Senha123"

# 7. Rodar API (porta 8001) — em producao NAO use --reload
uvicorn backend.main:app --port 8001

# 8. Rodar frontend (outro terminal)
streamlit run frontend/app.py
```

## API / Swagger

Com a API no ar (porta 8001):

- **Swagger UI** (interativo): http://127.0.0.1:8001/docs
- **ReDoc**: http://127.0.0.1:8001/redoc
- **OpenAPI (JSON)**: http://127.0.0.1:8001/openapi.json

Como autenticar no Swagger para testar rotas protegidas:
1. `POST /auth/login` com `{"email": "...", "password": "..."}` → copie o `access_token`.
2. Botão **Authorize** (topo direito) → cole apenas o token → Close.
3. As rotas protegidas (`/ask`, `/admin/*`, ...) passam a responder.

## Estrutura
```
backend/   API FastAPI, RAG, auth, db
frontend/  Streamlit (chat + upload)
eval/      RAGAS + comparacao RAG vs Long Context
docs_base/ documentos (gerados por IA)
```

## Documentação
- `RELATORIO.md` — relatório técnico (arquitetura, decisões, avaliação, dificuldades).
- `SEGURANCA.md` — OWASP Top 10, STRIDE e mitigações.
- `eval/RESULTADOS_RAGAS.md` — métricas de qualidade do RAG.

## Status
Funcional: RAG + Long Context + roteamento automático, avaliação RAGAS, e camada
de segurança (JWT, RBAC, auditoria, painel admin).
