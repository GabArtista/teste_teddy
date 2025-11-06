"""Embedding service interface."""

from typing import Iterable, Protocol, Sequence


class EmbeddingService(Protocol):
    """Contract for embedding providers."""

    async def embed_documents(self, texts: Iterable[str]) -> Sequence[list[float]]:
        """Return embeddings for each text."""

    async def embed_query(self, text: str) -> list[float]:
        """Return embedding for a query string."""

