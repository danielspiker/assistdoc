"""Carregamento de documentos — compartilhado por ingest (RAG) e long_context."""
import os

from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    Docx2txtLoader,
)

from backend import config

SUPPORTED_EXTS = (".txt", ".pdf", ".docx")


def load_file_documents(path: str):
    """Le um arquivo e devolve lista de Documents (1 por pagina no PDF)."""
    ext = os.path.splitext(path)[1].lower()
    if ext == ".txt":
        loader = TextLoader(path, encoding="utf-8")
    elif ext == ".pdf":
        loader = PyPDFLoader(path)
    elif ext == ".docx":
        loader = Docx2txtLoader(path)
    else:
        raise ValueError(f"Formato nao suportado: {ext} (use .txt, .pdf ou .docx)")
    return loader.load()


def full_text(path: str) -> str:
    """Texto completo de um arquivo (todas as paginas concatenadas)."""
    docs = load_file_documents(path)
    return "\n\n".join(d.page_content for d in docs)


def list_documents(*dirs: str) -> list[str]:
    """Nomes dos documentos suportados nas pastas dadas (sem repetir)."""
    if not dirs:
        dirs = (config.DOCS_BASE_DIR, config.STORAGE_DIR)
    nomes = []
    for d in dirs:
        if not os.path.isdir(d):
            continue
        for name in sorted(os.listdir(d)):
            if name.lower().endswith(SUPPORTED_EXTS) and name not in nomes:
                nomes.append(name)
    return nomes


def resolve_path(doc_name: str) -> str:
    """Acha o caminho de um documento pelo nome, procurando em docs_base e storage."""
    for d in (config.DOCS_BASE_DIR, config.STORAGE_DIR):
        candidate = os.path.join(d, doc_name)
        if os.path.isfile(candidate):
            return candidate
    raise FileNotFoundError(f"Documento nao encontrado: {doc_name}")
