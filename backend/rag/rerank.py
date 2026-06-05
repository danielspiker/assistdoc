"""Re-ranking dos chunks recuperados (RF08, bonus) — via LLM (qwen2.5).

Estrategia "retrieve-then-rerank": o vector store traz muitos candidatos
(rapido, mas grosseiro) e o proprio LLM re-ordena por relevancia real entre a
pergunta e cada trecho, ficando so com os melhores.

Usa o LLM local (qwen2.5) — forte em pt-BR. Custo: 1 chamada extra por pergunta.
Tem fallback seguro: se o parse falhar, mantem a ordem do vector store.
"""
import json
import re

from backend.llm.client import get_llm

RERANK_RANK_KEY = "rerank_pos"

_SYSTEM = ("Voce ordena trechos de documentos por relevancia a uma pergunta. "
           "Responda SOMENTE com uma lista JSON de inteiros, nada mais.")

_CHUNK_PREVIEW = 400  # caracteres por trecho enviados ao reranker


def _parse_ids(text: str, n: int) -> list[int]:
    """Extrai os indices da resposta do LLM (lista JSON ou numeros soltos)."""
    ids: list[int] = []
    m = re.search(r"\[[\d,\s]*\]", text)
    if m:
        try:
            ids = [int(x) for x in json.loads(m.group())]
        except Exception:
            ids = [int(x) for x in re.findall(r"\d+", m.group())]
    else:
        ids = [int(x) for x in re.findall(r"\d+", text)]
    # remove invalidos e duplicados, preservando ordem
    visto, limpos = set(), []
    for i in ids:
        if 0 <= i < n and i not in visto:
            visto.add(i)
            limpos.append(i)
    return limpos


def rerank_docs(query: str, docs: list, top_k: int) -> list:
    """Re-ordena `docs` (Document) por relevancia a `query` e devolve os top_k."""
    if not docs or len(docs) <= top_k:
        return docs[:top_k]
    try:
        listing = "\n".join(
            f"[{i}] {d.page_content[:_CHUNK_PREVIEW].strip()}"
            for i, d in enumerate(docs)
        )
        human = (
            f"Pergunta: {query}\n\n"
            f"Trechos candidatos:\n{listing}\n\n"
            f"Liste os {top_k} numeros dos trechos MAIS relevantes para responder "
            f"a pergunta, em ordem decrescente de relevancia, como lista JSON de "
            f"inteiros. Exemplo: [3, 0, 7]. Responda APENAS o JSON."
        )
        resp = get_llm().invoke([("system", _SYSTEM), ("human", human)])
        ids = _parse_ids(resp.content, len(docs))
        if not ids:
            return docs[:top_k]

        ordenados = [docs[i] for i in ids[:top_k]]
        # completa se o LLM devolveu menos que top_k
        if len(ordenados) < top_k:
            faltando = [d for j, d in enumerate(docs) if j not in set(ids)]
            ordenados += faltando[: top_k - len(ordenados)]

        for pos, d in enumerate(ordenados):
            d.metadata[RERANK_RANK_KEY] = pos
        return ordenados[:top_k]
    except Exception:
        return docs[:top_k]
