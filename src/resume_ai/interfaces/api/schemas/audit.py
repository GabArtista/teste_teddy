"""Audit log response schema."""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class AuditLogSchema(BaseModel):
    """Representation of an audit log entry."""

    request_id: str = Field(..., example="a85e1f2c-5c74-45f8-ad66-6cedf6762b9e")
    user_id: str = Field(..., example="fabio.talent@techmatch.io")
    timestamp: datetime
    query: Optional[str]
    result: Dict[str, Any]

