"""Fabrica de embeddings e do vector store Chroma — reutilizada por ingest e retrieve."""
import os

# Desliga telemetria do Chroma (evita ruido "capture() takes 1 positional...")
os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")

from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

from backend import config

COLLECTION_NAME = "assistdoc"


class NomicEmbeddings(OllamaEmbeddings):
    """OllamaEmbeddings com os prefixos de tarefa que o nomic-embed-text exige.

    O modelo nomic foi treinado com instrucoes: documentos sao embedados com
    'search_document:' e consultas com 'search_query:'. Sem isso o ranking de
    similaridade fica ruim. Os prefixos so entram no calculo do vetor — o texto
    original (page_content) e armazenado limpo pelo Chroma.
    """

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return super().embed_documents([f"search_document: {t}" for t in texts])

    def embed_query(self, text: str) -> list[float]:
        return super().embed_query(f"search_query: {text}")


def get_embeddings() -> OllamaEmbeddings:
    """Modelo de embedding local via Ollama.

    Usa os prefixos de tarefa apenas para modelos da familia nomic; outros
    (ex.: bge-m3) nao usam prefixo.
    """
    model = config.OLLAMA_EMBED_MODEL
    cls = NomicEmbeddings if "nomic" in model.lower() else OllamaEmbeddings
    return cls(model=model, base_url=config.OLLAMA_BASE_URL)


def get_vectorstore() -> Chroma:
    """Vector store Chroma persistido em disco (config.CHROMA_DIR)."""
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=get_embeddings(),
        persist_directory=config.CHROMA_DIR,
    )
