"""OpenAI embedding service."""

from typing import Iterable, Sequence

from langchain_openai import OpenAIEmbeddings

from resume_ai.application.interfaces.embedding_service import EmbeddingService


class OpenAIEmbeddingService(EmbeddingService):
    """Uses OpenAI embedding models through LangChain."""

    def __init__(self, api_key: str, model: str) -> None:
        self._client = OpenAIEmbeddings(api_key=api_key, model=model)

    async def embed_documents(self, texts: Iterable[str]) -> Sequence[list[float]]:
        return await self._client.aembed_documents(list(texts))

    async def embed_query(self, text: str) -> list[float]:
        return await self._client.aembed_query(text)

