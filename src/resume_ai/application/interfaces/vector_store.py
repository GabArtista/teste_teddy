"""Vector store interface."""

from typing import Iterable, Protocol

from resume_ai.domain.models.resume import ResumeChunk


class VectorStore(Protocol):
    """Contract for vector storage adapters."""

    async def upsert_chunks(self, chunks: Iterable[ResumeChunk]) -> None:
        """Persist resume chunks for retrieval."""

    async def query(self, text: str, limit: int = 5) -> list[ResumeChunk]:
        """Return the most relevant chunks for the supplied query."""

