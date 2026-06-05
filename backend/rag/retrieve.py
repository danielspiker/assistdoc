"""RAG — recuperacao + grounding + geracao (etapa S3).

Fluxo:
  1. busca top-K chunks mais similares no Chroma
  2. monta prompt com os trechos (contexto) + a pergunta
  3. LLM responde APENAS com base no contexto, citando a fonte
  4. devolve resposta + lista de fontes usadas
"""
from backend import config
from backend.rag.vectorstore import get_vectorstore
from backend.rag.rerank import rerank_docs
from backend.llm.client import get_llm

SYSTEM_PROMPT = (
    "Voce e um assistente especializado em documentos institucionais de uma "
    "faculdade. Responda em portugues, de forma clara e objetiva, APENAS com "
    "base nos trechos fornecidos no contexto. Se a informacao nao estiver nos "
    "trechos, responda exatamente: 'Nao encontrei essa informacao nos "
    "documentos disponiveis.' Ao final da resposta, cite sempre a fonte no "
    "formato (Fonte: <arquivo>, trecho <n>)."
)


def _format_context(docs) -> str:
    """Monta o bloco de contexto numerado a partir dos chunks recuperados."""
    blocos = []
    for d in docs:
        src = d.metadata.get("source", "desconhecido")
        chunk = d.metadata.get("chunk", "?")
        page = d.metadata.get("page")
        ref = f"{src}, trecho {chunk}" + (f", pagina {page}" if page is not None else "")
        blocos.append(f"[{ref}]\n{d.page_content}")
    return "\n\n".join(blocos)


def _sources(docs) -> list[dict]:
    """Lista de fontes para o frontend exibir."""
    out = []
    for d in docs:
        out.append({
            "source": d.metadata.get("source"),
            "chunk": d.metadata.get("chunk"),
            "page": d.metadata.get("page"),
            "snippet": d.page_content[:200],
        })
    return out


def answer(question: str, k: int | None = None) -> dict:
    """Responde uma pergunta via RAG. Devolve {answer, sources}.

    Com config.RERANK ligado: busca RERANK_CANDIDATES candidatos e re-ranqueia
    com cross-encoder, ficando com os top-k mais relevantes (RF08).
    """
    k = k or config.TOP_K
    store = get_vectorstore()

    if config.RERANK:
        candidates = store.similarity_search(question, k=config.RERANK_CANDIDATES)
        docs = rerank_docs(question, candidates, top_k=k)
    else:
        docs = store.similarity_search(question, k=k)

    if not docs:
        return {
            "answer": "Nao encontrei essa informacao nos documentos disponiveis.",
            "sources": [],
        }

    context = _format_context(docs)
    messages = [
        ("system", SYSTEM_PROMPT),
        ("human", f"Contexto:\n{context}\n\nPergunta: {question}\n\nResposta:"),
    ]
    resp = get_llm().invoke(messages)
    tokens = dict(getattr(resp, "usage_metadata", None) or {})
    return {
        "answer": resp.content,
        "sources": _sources(docs),
        "contexts": [d.page_content for d in docs],  # texto integral p/ avaliacao RAGAS
        "tokens": tokens,
    }


# --- teste rapido pela linha de comando -------------------------------------
if __name__ == "__main__":
    import sys
    q = sys.argv[1] if len(sys.argv) > 1 else "Quantas faltas posso ter sem reprovar?"
    print(f"Pergunta: {q}\n")
    r = answer(q)
    print("Resposta:\n", r["answer"])
    print("\nFontes:")
    for s in r["sources"]:
        print(f"  - {s['source']} (trecho {s['chunk']})")
