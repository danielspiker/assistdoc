"""Roteamento automatico RAG vs Long Context (RF07 — bonus).

Regras (do enunciado):
  - documento especifico selecionado  -> Long Context
  - base pequena (< LIMIAR docs)       -> Long Context
  - base grande                        -> RAG
  - (heuristica extra) base pequena mas documento gigante -> RAG, para nao
    estourar a janela de contexto.
"""
from backend.rag.loaders import list_documents, resolve_path, full_text
from backend.rag import retrieve, long_context

# Abaixo deste numero de documentos, Long Context cobre a base inteira.
LIMIAR_BASE_PEQUENA = 5
# Acima deste tamanho (caracteres) caimos em RAG para nao estourar a janela.
LIMIAR_TAMANHO_CHARS = 24000  # ~6k tokens, folga sob num_ctx=8192


def decide(question: str, document: str | None = None) -> str:
    """Decide 'long_context' ou 'rag' para a pergunta."""
    if document:
        # documento unico: Long Context, salvo se for grande demais
        try:
            if len(full_text(resolve_path(document))) > LIMIAR_TAMANHO_CHARS:
                return "rag"
        except FileNotFoundError:
            return "rag"
        return "long_context"

    nomes = list_documents()
    if len(nomes) < LIMIAR_BASE_PEQUENA:
        # base pequena: cabe inteira? senao, RAG
        total = sum(len(full_text(resolve_path(n))) for n in nomes)
        return "long_context" if total <= LIMIAR_TAMANHO_CHARS else "rag"
    return "rag"


def answer(question: str, document: str | None = None) -> dict:
    """Roteia e responde. Devolve dict com a chave 'mode' indicando o caminho usado."""
    modo = decide(question, document)
    if modo == "long_context":
        return long_context.answer(question, document)
    out = retrieve.answer(question)
    out["mode"] = "rag"
    return out
