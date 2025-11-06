"""Structured logging configuration."""

import logging
from typing import Any

import structlog


def configure_logging(level: str = "INFO") -> None:
    """Configure structlog for the application."""

    min_level = getattr(logging, level.upper(), logging.INFO)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(min_level),
        context_class=dict,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> Any:
    """Return a configured structlog logger."""

    return structlog.get_logger(name)
