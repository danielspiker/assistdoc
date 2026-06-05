"""Avaliacao RAGAS do pipeline RAG (etapa S6 — RF / secao 7.4 do enunciado).

Juiz: Google Gemini (free tier). Metricas:
  - Faithfulness     : a resposta e fiel ao contexto recuperado? (anti-alucinacao)
  - AnswerRelevancy  : a resposta e relevante para a pergunta?
  - ContextRecall    : os chunks recuperados cobrem a resposta esperada?
  - ContextPrecision : os chunks recuperados sao precisos (pouco ruido)?

Pre-requisitos:
  - pip install -r requirements.txt   (traz ragas + langchain-google-genai)
  - GEMINI_API_KEY no .env (https://ai.google.dev)
  - Ollama no ar (gera as respostas RAG que serao avaliadas)

Uso:
    python -m eval.run_ragas
    python -m eval.run_ragas 10      # avalia so as 10 primeiras (mais rapido / menos cota)
"""
import json
import os
import sys

from backend import config
from backend.rag import retrieve

ROOT = os.path.dirname(__file__)
DATASET = os.path.join(ROOT, "dataset.json")
OUT_JSON = os.path.join(ROOT, "resultado_ragas.json")

# langchain-google-genai le a chave de GOOGLE_API_KEY
os.environ.setdefault("GOOGLE_API_KEY", config.GEMINI_API_KEY)

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_EMBED_MODEL = os.getenv("GEMINI_EMBED_MODEL", "models/text-embedding-004")


def _build_samples(dataset: list[dict]) -> list[dict]:
    """Roda o RAG em cada pergunta e monta as amostras no formato do RAGAS."""
    samples = []
    for item in dataset:
        print(f"  [{item['id']}] RAG: {item['question']}")
        out = retrieve.answer(item["question"])
        samples.append({
            "user_input": item["question"],
            "response": out["answer"],
            "retrieved_contexts": out.get("contexts", []),
            "reference": item["expected"],
        })
    return samples


# Juiz: "gemini" (nuvem, free tier 2.5) ou "ollama" (local, sem cota mas pior em JSON)
JUDGE = os.getenv("RAGAS_JUDGE", "gemini")


def _make_judge():
    """Devolve (llm, embeddings) ja embrulhados para o RAGAS, conforme RAGAS_JUDGE."""
    from ragas.llms import LangchainLLMWrapper
    from ragas.embeddings import LangchainEmbeddingsWrapper

    if JUDGE == "gemini":
        if not config.GEMINI_API_KEY:
            sys.exit("ERRO: defina GEMINI_API_KEY no .env (https://ai.google.dev).")
        from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
        llm = ChatGoogleGenerativeAI(model=GEMINI_MODEL, temperature=0)
        emb = GoogleGenerativeAIEmbeddings(model=GEMINI_EMBED_MODEL)
        nome = GEMINI_MODEL
    else:  # ollama local
        from langchain_ollama import ChatOllama
        from backend.rag.vectorstore import get_embeddings
        # Juiz pode ser um modelo maior que o do app (segue JSON melhor).
        judge_model = os.getenv("RAGAS_OLLAMA_MODEL", config.OLLAMA_LLM_MODEL)
        llm = ChatOllama(
            model=judge_model,
            base_url=config.OLLAMA_BASE_URL,
            temperature=0,
            num_ctx=config.OLLAMA_NUM_CTX,
        )
        emb = get_embeddings()
        nome = f"ollama:{judge_model}"

    return LangchainLLMWrapper(llm), LangchainEmbeddingsWrapper(emb), nome


def main():
    # imports pesados so aqui
    from ragas import EvaluationDataset, evaluate
    from ragas.metrics import (
        Faithfulness, AnswerRelevancy, ContextRecall, ContextPrecision,
    )
    from ragas.run_config import RunConfig

    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None
    with open(DATASET, encoding="utf-8") as f:
        dataset = json.load(f)
    if limit:
        dataset = dataset[:limit]

    print(f"Gerando respostas RAG para {len(dataset)} perguntas...")
    samples = _build_samples(dataset)
    eval_dataset = EvaluationDataset.from_list(samples)

    judge, judge_emb, judge_nome = _make_judge()
    metrics = [Faithfulness(), AnswerRelevancy(), ContextRecall(), ContextPrecision()]

    # Juiz local e mais lento: menos workers e timeout maior.
    workers = 4 if JUDGE == "gemini" else 1
    print(f"\nAvaliando com RAGAS (juiz: {judge_nome})...")
    result = evaluate(
        dataset=eval_dataset,
        metrics=metrics,
        llm=judge,
        embeddings=judge_emb,
        run_config=RunConfig(max_workers=workers, timeout=300),
    )

    print("\n=== SCORES RAGAS ===")
    print(result)

    # Salva scores agregados + por amostra
    df = result.to_pandas()
    df.to_json(OUT_JSON, orient="records", force_ascii=False, indent=2)
    print(f"\nDetalhe por pergunta salvo em: {OUT_JSON}")


if __name__ == "__main__":
    main()
