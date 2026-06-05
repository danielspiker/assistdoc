"""Comparacao RAG vs Long Context (etapa S6 — analise obrigatoria do enunciado).

Para cada pergunta do dataset, roda nos dois modos e mede:
  - latencia (time.time())
  - tokens gastos (usage_metadata do Ollama)
  - resposta gerada (qualidade avaliada depois com RAGAS / manualmente)

Uso (com Ollama no ar; NAO precisa do servidor FastAPI):
    python -m eval.compare
    python -m eval.compare 5      # so as 5 primeiras (teste rapido)

Saidas em eval/:
  - resultado_comparacao.json   (dados crus)
  - resultado_comparacao.md     (tabela para o relatorio)
"""
import json
import os
import sys
import time

from backend.rag import retrieve, long_context

ROOT = os.path.dirname(__file__)
DATASET = os.path.join(ROOT, "dataset.json")
OUT_JSON = os.path.join(ROOT, "resultado_comparacao.json")
OUT_MD = os.path.join(ROOT, "resultado_comparacao.md")


def _total_tokens(tokens: dict) -> int:
    return int(tokens.get("total_tokens") or 0)


def _run_one(item: dict) -> dict:
    q = item["question"]

    t0 = time.time()
    rag = retrieve.answer(q)
    rag_lat = time.time() - t0

    t0 = time.time()
    lc = long_context.answer(q, item["source"])
    lc_lat = time.time() - t0

    return {
        "id": item["id"],
        "question": q,
        "expected": item["expected"],
        "source": item["source"],
        "rag_answer": rag["answer"],
        "rag_latency_s": round(rag_lat, 2),
        "rag_tokens": _total_tokens(rag.get("tokens", {})),
        "lc_answer": lc["answer"],
        "lc_latency_s": round(lc_lat, 2),
        "lc_tokens": _total_tokens(lc.get("tokens", {})),
    }


def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None
    with open(DATASET, encoding="utf-8") as f:
        dataset = json.load(f)
    if limit:
        dataset = dataset[:limit]

    # Warm-up: carrega o modelo na RAM antes de medir (evita cold-start na 1a).
    print("Aquecendo o modelo (warm-up)...")
    retrieve.answer("teste")
    long_context.answer("teste", dataset[0]["source"])

    results = []
    for item in dataset:
        print(f"[{item['id']}/{len(dataset)}] {item['question']}")
        r = _run_one(item)
        results.append(r)
        print(f"    RAG {r['rag_latency_s']}s / {r['rag_tokens']}tok | "
              f"LC {r['lc_latency_s']}s / {r['lc_tokens']}tok")

    # --- agregados ---
    n = len(results)
    avg = lambda key: round(sum(r[key] for r in results) / n, 2) if n else 0
    resumo = {
        "n_perguntas": n,
        "rag_latencia_media_s": avg("rag_latency_s"),
        "lc_latencia_media_s": avg("lc_latency_s"),
        "rag_tokens_medio": avg("rag_tokens"),
        "lc_tokens_medio": avg("lc_tokens"),
    }

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump({"resumo": resumo, "resultados": results}, f,
                  ensure_ascii=False, indent=2)

    _write_md(results, resumo)

    print("\n=== RESUMO ===")
    for k, v in resumo.items():
        print(f"  {k}: {v}")
    print(f"\nSalvo: {OUT_JSON}\n       {OUT_MD}")


def _write_md(results: list[dict], resumo: dict) -> None:
    linhas = [
        "# Comparacao RAG vs Long Context",
        "",
        f"- Perguntas avaliadas: **{resumo['n_perguntas']}**",
        f"- Latencia media — RAG: **{resumo['rag_latencia_media_s']}s** | "
        f"Long Context: **{resumo['lc_latencia_media_s']}s**",
        f"- Tokens medios — RAG: **{resumo['rag_tokens_medio']}** | "
        f"Long Context: **{resumo['lc_tokens_medio']}**",
        "",
        "| # | Pergunta | Esperado | Latencia RAG | Latencia LC | Tokens RAG | Tokens LC |",
        "|---|----------|----------|-------------|------------|-----------|----------|",
    ]
    for r in results:
        linhas.append(
            f"| {r['id']} | {r['question']} | {r['expected']} | "
            f"{r['rag_latency_s']}s | {r['lc_latency_s']}s | "
            f"{r['rag_tokens']} | {r['lc_tokens']} |"
        )
    linhas += [
        "",
        "## Respostas (para inspecao manual de qualidade)",
        "",
    ]
    for r in results:
        linhas += [
            f"### {r['id']}. {r['question']}",
            f"**Esperado:** {r['expected']}  ",
            f"**RAG:** {r['rag_answer']}  ",
            f"**Long Context:** {r['lc_answer']}",
            "",
        ]
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas))


if __name__ == "__main__":
    main()
