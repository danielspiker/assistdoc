"""Diagnostico de retrieval. Mostra contagem, top-k com score e procura um termo.

Uso:
    python -m backend.rag.debug_search "posso solicitar revisao de prova?" revis
"""
import sys

from backend.rag.vectorstore import get_vectorstore


def main():
    query = sys.argv[1] if len(sys.argv) > 1 else "posso solicitar revisao de prova?"
    termo = sys.argv[2] if len(sys.argv) > 2 else "revis"

    store = get_vectorstore()

    # 1. Quantos vetores existem
    count = store._collection.count()
    print(f"Total de chunks no Chroma: {count}\n")

    # 2. Top-10 por similaridade, com score (menor = mais perto na distancia)
    print(f"== Top-10 para: {query!r} ==")
    results = store.similarity_search_with_score(query, k=10)
    for doc, score in results:
        src = doc.metadata.get("source")
        ch = doc.metadata.get("chunk")
        print(f"  score={score:.4f}  {src} (trecho {ch})")
        print(f"     {doc.page_content[:90].strip()!r}")

    # 3. Quais chunks contem o termo (verifica se o conteudo certo foi indexado)
    print(f"\n== Chunks cujo conteudo contem {termo!r} ==")
    data = store.get()  # todos os documentos
    achou = False
    for content, meta in zip(data["documents"], data["metadatas"]):
        if termo.lower() in content.lower():
            achou = True
            print(f"  {meta.get('source')} (trecho {meta.get('chunk')})")
            print(f"     {content[:120].strip()!r}")
    if not achou:
        print("  NENHUM chunk contem o termo. (problema de ingestao/chunking)")


if __name__ == "__main__":
    main()
