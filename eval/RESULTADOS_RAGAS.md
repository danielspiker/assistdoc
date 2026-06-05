# Resultados RAGAS — AssistDoc

Avaliação do pipeline RAG com o framework RAGAS.

- **Dataset:** 25 perguntas com gabarito (`dataset.json`), 5 documentos da base.
- **Modelo do app (gera respostas):** Ollama `llama3.2` + embeddings `bge-m3`.
- **Juiz (avalia):** Ollama `qwen2.5` (local). *Gemini free tier foi testado mas a
  chave disponível tinha cota muito baixa — 20 req/dia no 2.5-flash; o juiz local
  contornou sem custo. O llama3.2 (3B) como juiz falhava no parse do faithfulness
  (NaN); o qwen2.5 (7B) segue o JSON estruturado corretamente.*

## Scores agregados (25 perguntas)

| Métrica | Score | O que mede |
|---------|-------|------------|
| Faithfulness | **0.74** | Resposta é fiel ao contexto recuperado (anti-alucinação) |
| Answer Relevancy | **0.73** | Resposta é relevante para a pergunta feita |
| Context Recall | **1.00** | Os chunks recuperados cobrem a resposta esperada |
| Context Precision | **0.98** | Os chunks recuperados são precisos (pouco ruído) |

> *Nota de variância:* o juiz local (qwen2.5) não é 100% determinístico. Em duas
> execuções, faithfulness oscilou entre 0.74 e 0.79 e relevancy entre 0.73 e 0.76;
> recall manteve 1.00 e precision ~0.96–0.98. As conclusões não mudam.

## Leitura

- **Context Recall 1.00 + Precision 0.96:** o retrieve (bge-m3, top-5) está
  excelente — traz o conteúdo certo com pouquíssimo ruído. Validou a troca do
  `nomic-embed-text` pelo `bge-m3`.
- **Faithfulness 0.79:** maioria das respostas fundamentada no contexto; quedas
  vêm de o llama3.2 às vezes acrescentar frases não presentes nos trechos.
- **Answer Relevancy 0.76:** respostas relevantes, mas por vezes verbosas/ com
  informação extra, o que reduz a métrica.

## RF08 — Re-ranking (bônus): avaliado e descartado

Implementamos re-ranking "retrieve-then-rerank" (busca 15 candidatos, re-ordena
para top-5) em duas variantes: cross-encoder leve (FlashRank `ms-marco-MultiBERT`)
e LLM-as-reranker (qwen2.5). Avaliamos com RAGAS sobre as mesmas 25 perguntas:

| Métrica | Sem rerank (baseline) | Com rerank (LLM) | Efeito |
|---------|----------------------|------------------|--------|
| Faithfulness | 0.74 | 0.62 | piora |
| Answer Relevancy | 0.73 | 0.72 | ~igual |
| Context Recall | **1.00** | 0.92 | piora |
| Context Precision | **0.98** | 0.51 | piora muito |

**Conclusão:** o re-ranking **piorou** todas as métricas. Causa: o retrieval com
`bge-m3` já está saturado (recall 1.0, precision 0.96) — não há ganho possível em
recall e o rerank apenas reordena, podendo cortar chunks relevantes (recall caiu
para 0.92) e introduzir ruído (precision despencou para 0.51). Decisão de
engenharia fundamentada em dado: **re-ranking mantido desligado** (`RERANK=false`).
O código está pronto (`backend/rag/rerank.py`), permitindo reativar caso a base
cresça muito (cenário onde o retrieve grosseiro erraria mais e o rerank ajudaria).

## Reprodução

```
python -m eval.run_ragas          # 25 perguntas (definitivo)
python -m eval.run_ragas 5        # amostra rápida
```
Detalhe por pergunta em `resultado_ragas.json`.
Comparação RAG vs Long Context (latência/tokens) em `resultado_comparacao.md`.
