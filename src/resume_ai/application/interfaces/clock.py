"""Clock interface used for deterministic testing."""

from datetime import datetime, timezone
from typing import Protocol


class Clock(Protocol):
    """Provides current UTC timestamp."""

    def now(self) -> datetime:
        """Return current UTC datetime."""


class SystemClock:
    """Production clock implementation."""

    def now(self) -> datetime:
        """Return real current UTC time."""

        return datetime.now(tz=timezone.utc)

