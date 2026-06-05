"""Long Context (etapa S5).

Em vez de buscar trechos (RAG), injeta o documento INTEIRO no prompt e deixa o
LLM raciocinar sobre tudo. Bom para analise profunda de 1 documento (ou de uma
base pequena), aproveitando a janela de contexto grande do modelo.

Se nenhum documento for indicado, concatena todos os da base (uso valido quando
a base e pequena).
"""
from backend import config
from backend.rag.loaders import full_text, resolve_path, list_documents
from backend.llm.client import get_llm

SYSTEM_PROMPT = (
    "Voce e um assistente que analisa documentos institucionais de uma "
    "faculdade. Responda em portugues, de forma clara, APENAS com base no "
    "documento fornecido. Se a informacao nao estiver no documento, responda "
    "exatamente: 'Nao encontrei essa informacao no documento.' Cite a fonte "
    "ao final no formato (Fonte: <documento>)."
)


def _build_context(doc_name: str | None) -> tuple[str, list[str]]:
    """Monta o texto completo a injetar e a lista de documentos usados."""
    if doc_name:
        path = resolve_path(doc_name)
        return full_text(path), [doc_name]

    # sem documento especifico: usa a base inteira (valido quando e pequena)
    nomes = list_documents()
    partes = []
    for nome in nomes:
        partes.append(f"### DOCUMENTO: {nome}\n{full_text(resolve_path(nome))}")
    return "\n\n".join(partes), nomes


def answer(question: str, doc_name: str | None = None) -> dict:
    """Responde via Long Context. Devolve {answer, mode, documents}."""
    contexto, usados = _build_context(doc_name)

    if not contexto.strip():
        return {
            "answer": "Nao ha documentos disponiveis para analise.",
            "mode": "long_context",
            "documents": [],
        }

    messages = [
        ("system", SYSTEM_PROMPT),
        ("human", f"Documento(s):\n{contexto}\n\nPergunta: {question}\n\nResposta:"),
    ]
    resp = get_llm().invoke(messages)
    tokens = dict(getattr(resp, "usage_metadata", None) or {})
    return {"answer": resp.content, "mode": "long_context", "documents": usados,
            "tokens": tokens}


# --- teste rapido pela linha de comando -------------------------------------
if __name__ == "__main__":
    import sys
    q = sys.argv[1] if len(sys.argv) > 1 else "Resuma as regras de estagio."
    doc = sys.argv[2] if len(sys.argv) > 2 else None
    r = answer(q, doc)
    print(f"Modo: {r['mode']} | Documentos: {r['documents']}\n")
    print(r["answer"])
