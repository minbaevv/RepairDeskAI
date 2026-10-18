from langchain_ollama import ChatOllama

from mysite.config import settings


def get_model() -> ChatOllama:
    return ChatOllama(
        model=settings.ollama_model,
        base_url=settings.ollama_base_url,
        temperature=settings.temperature,
        num_predict=settings.num_predict,
    )