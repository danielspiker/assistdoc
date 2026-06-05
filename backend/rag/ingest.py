"""Pipeline de ingestao (RAG — etapa S2).

Carrega documentos (.txt/.pdf/.docx), fatia em chunks com metadados,
gera embeddings e persiste no Chroma.

Uso como script (indexa tudo de docs_base/):
    python -m backend.rag.ingest

Uso como funcao (indexar 1 arquivo enviado por upload):
    from backend.rag.ingest import ingest_file
    n = ingest_file("storage/contrato.pdf")
"""
import os
import sys

from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend import config
from backend.rag.loaders import load_file_documents
from backend.rag.vectorstore import get_vectorstore


def _make_splitter() -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )


# --- API publica ------------------------------------------------------------

def ingest_file(path: str) -> int:
    """Indexa um unico arquivo no Chroma. Devolve quantos chunks foram criados."""
    docs = load_file_documents(path)
    splitter = _make_splitter()
    chunks = splitter.split_documents(docs)

    source = os.path.basename(path)
    for i, ch in enumerate(chunks):
        ch.metadata["source"] = source
        ch.metadata["chunk"] = i
        # PyPDFLoader ja inclui "page" (int); txt/docx nao tem pagina.
        # Chroma rejeita metadados None -> remove quaisquer chaves nulas.
        ch.metadata = {k: v for k, v in ch.metadata.items() if v is not None}

    if not chunks:
        return 0

    store = get_vectorstore()
    store.add_documents(chunks)
    return len(chunks)


def ingest_dir(directory: str) -> dict:
    """Indexa todos os .txt/.pdf/.docx de uma pasta. Devolve {arquivo: n_chunks}."""
    result = {}
    for name in sorted(os.listdir(directory)):
        if name.lower().endswith((".txt", ".pdf", ".docx")):
            path = os.path.join(directory, name)
            try:
                result[name] = ingest_file(path)
            except Exception as e:  # noqa: BLE001
                result[name] = f"ERRO: {e}"
    return result


# --- CLI --------------------------------------------------------------------

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else config.DOCS_BASE_DIR
    print(f"Indexando: {target}")
    summary = ingest_dir(target)
    total = sum(v for v in summary.values() if isinstance(v, int))
    for name, n in summary.items():
        print(f"  {name}: {n} chunks")
    print(f"Total: {total} chunks no Chroma ({config.CHROMA_DIR})")
