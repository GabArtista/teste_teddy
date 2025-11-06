"""MongoDB audit repository using Motor."""

from __future__ import annotations

from typing import Any, Sequence

try:
    from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
except ImportError:  # pragma: no cover - fallback for test environments
    AsyncIOMotorClient = None  # type: ignore
    AsyncIOMotorCollection = Any  # type: ignore

from resume_ai.application.interfaces.audit_repository import AuditRepository
from resume_ai.domain.models.audit import AuditLog


class MongoAuditRepository(AuditRepository):
    """Persists audit logs in MongoDB."""

    def __init__(self, mongo_uri: str, collection_name: str = "audit_logs") -> None:
        if AsyncIOMotorClient is None:
            raise RuntimeError(
                "motor is not installed or incompatible. Install motor to use MongoAuditRepository."
            )
        self._client = AsyncIOMotorClient(mongo_uri)
        self._collection: AsyncIOMotorCollection = self._client.get_default_database()[
            collection_name
        ]

    async def save(self, log: AuditLog) -> None:
        document = {
            "request_id": log.request_id,
            "user_id": log.user_id,
            "timestamp": log.timestamp,
            "query": log.query,
            "result": log.result,
        }
        await self._collection.insert_one(document)

    async def list_logs(self, limit: int = 50) -> Sequence[AuditLog]:
        cursor = self._collection.find().sort("timestamp", -1).limit(limit)
        items: list[AuditLog] = []
        async for doc in cursor:
            items.append(
                AuditLog(
                    request_id=str(doc["request_id"]),
                    user_id=str(doc["user_id"]),
                    timestamp=doc["timestamp"],
                    query=doc.get("query"),
                    result=doc.get("result", {}),
                )
            )
        return items
