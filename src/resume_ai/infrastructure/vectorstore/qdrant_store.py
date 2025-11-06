"""Qdrant vector store adapter."""

from __future__ import annotations

from typing import Iterable, List

from qdrant_client import QdrantClient
from qdrant_client.http import models as rest

from resume_ai.application.interfaces.embedding_service import EmbeddingService
from resume_ai.application.interfaces.vector_store import VectorStore
from resume_ai.domain.models.resume import ResumeChunk
from resume_ai.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class QdrantVectorStore(VectorStore):
    """Persists resume chunks in Qdrant for semantic search."""

    def __init__(
        self,
        url: str,
        collection_name: str,
        vector_size: int,
        similarity: str,
        embedding_service: EmbeddingService,
    ) -> None:
        self._client = QdrantClient(url=url)
        self._collection = collection_name
        self._embedding_service = embedding_service
        self._vector_size = vector_size
        self._distance = rest.Distance.COSINE if similarity == "cosine" else rest.Distance.DOT
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        collections = self._client.get_collections()
        if any(collection.name == self._collection for collection in collections.collections):
            return
        logger.info("creating_qdrant_collection", collection=self._collection)
        self._client.create_collection(
            collection_name=self._collection,
            vectors_config=rest.VectorParams(size=self._vector_size, distance=self._distance),
        )

    async def upsert_chunks(self, chunks: Iterable[ResumeChunk]) -> None:
        chunk_list = list(chunks)
        if not chunk_list:
            return
        texts = [chunk.text for chunk in chunk_list]
        embeddings = await self._embedding_service.embed_documents(texts)
        points = [
            rest.PointStruct(
                id=chunk.chunk_id,
                vector=embedding,
                payload={
                    "resume_id": chunk.metadata.get("resume_id"),
                    "position": chunk.metadata.get("position"),
                    "text": chunk.text,
                },
            )
            for chunk, embedding in zip(chunk_list, embeddings, strict=False)
        ]
        self._client.upsert(collection_name=self._collection, points=points)

    async def query(self, text: str, limit: int = 5) -> list[ResumeChunk]:
        vector = await self._embedding_service.embed_query(text)
        search_result = self._client.search(
            collection_name=self._collection,
            query_vector=vector,
            limit=limit,
        )
        chunks: list[ResumeChunk] = []
        for index, point in enumerate(search_result):
            payload = point.payload or {}
            resume_id = str(payload.get("resume_id", ""))
            chunk = ResumeChunk(
                chunk_id=str(point.id),
                text=str(payload.get("text", "")),
                metadata={"resume_id": resume_id, "rank": str(index)},
            )
            chunks.append(chunk)
        return chunks
