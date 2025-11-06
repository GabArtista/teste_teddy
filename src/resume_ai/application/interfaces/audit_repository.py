"""Audit repository interface."""

from typing import Protocol, Sequence

from resume_ai.domain.models.audit import AuditLog


class AuditRepository(Protocol):
    """Contract for persisting audit logs."""

    async def save(self, log: AuditLog) -> None:
        """Persist an audit log."""

    async def list_logs(self, limit: int = 50) -> Sequence[AuditLog]:
        """Return the latest audit logs."""

