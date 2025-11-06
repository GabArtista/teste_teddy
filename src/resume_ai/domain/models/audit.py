"""Audit log domain model."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class AuditLog:
    """Represents an execution trace of the resume intelligence workflow."""

    request_id: str
    user_id: str
    timestamp: datetime
    query: str | None
    result: dict

