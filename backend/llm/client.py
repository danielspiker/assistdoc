"""Cliente LLM — abstrai o provedor (Ollama local por padrao)."""
from langchain_ollama import ChatOllama

from backend import config


def get_llm(num_ctx: int | None = None):
    """Devolve um chat model. Hoje: Ollama. Gemini fica para depois (RF nuvem).

    num_ctx: tamanho da janela de contexto. RAG usa o padrao (poucos chunks);
    Long Context passa um valor maior para caber o documento inteiro.
    """
    if config.LLM_PROVIDER == "ollama":
        return ChatOllama(
            model=config.OLLAMA_LLM_MODEL,
            base_url=config.OLLAMA_BASE_URL,
            temperature=0,  # respostas factuais, menos alucinacao
            num_ctx=num_ctx or config.OLLAMA_NUM_CTX,
        )
    raise ValueError(
        f"LLM_PROVIDER '{config.LLM_PROVIDER}' nao suportado ainda. Use 'ollama'."
    )
