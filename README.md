# AssistDoc

Assistente inteligente de documentos academicos. Responde perguntas em linguagem
natural sobre regimento, manual do aluno e politicas da instituicao, citando a
fonte (documento + pagina). Usa **RAG** + **Long Context**.

Projeto integrador — cobre duas disciplinas:
- **Desenvolver Sistemas Inteligentes (IA):** pipeline RAG + Long Context.
- **Desenvolver Sistemas Seguros (SEC):** auth JWT, RBAC, auditoria, OWASP.

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
# editar .env

# 4. Ollama (LLM local) — https://ollama.com
ollama pull llama3.2
ollama pull nomic-embed-text

# 5. Rodar API
uvicorn backend.main:app --reload
# Swagger: http://localhost:8000/docs

# 6. Rodar frontend (outro terminal)
streamlit run frontend/app.py
```

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
