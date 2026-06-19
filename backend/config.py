"""Configuracao central — le variaveis de ambiente do .env."""
import os
from dotenv import load_dotenv

load_dotenv()

# LLM
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_LLM_MODEL = os.getenv("OLLAMA_LLM_MODEL", "llama3.2")
# Janela de contexto do Ollama. Padrao do Ollama e 2048 (trunca!). Subimos para
# caber documentos inteiros no modo Long Context.
OLLAMA_NUM_CTX = int(os.getenv("OLLAMA_NUM_CTX", "8192"))
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "bge-m3")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# RAG
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "80"))
TOP_K = int(os.getenv("TOP_K", "5"))

# Re-ranking (RF08, bonus): busca RERANK_CANDIDATES e o LLM re-ranqueia para TOP_K.
# Default OFF: avaliacao mostrou que piora (baseline bge-m3 ja saturado, recall 1.0).
RERANK = os.getenv("RERANK", "false").lower() == "true"
RERANK_CANDIDATES = int(os.getenv("RERANK_CANDIDATES", "15"))

# Auth
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-trocar")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "15"))
MAX_LOGIN_ATTEMPTS = int(os.getenv("MAX_LOGIN_ATTEMPTS", "5"))

# Upload
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "10"))

# Caminhos
CHROMA_DIR = os.getenv("CHROMA_DIR", "./chroma_db")
STORAGE_DIR = os.getenv("STORAGE_DIR", "./storage")
DOCS_BASE_DIR = os.getenv("DOCS_BASE_DIR", "./docs_base")
SQLITE_PATH = os.getenv("SQLITE_PATH", "./assistdoc.db")
