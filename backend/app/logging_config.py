"""
Structured logging configuration using structlog.

Provides JSON-formatted logs with request correlation IDs, user context,
and timestamp information for production observability.
"""

import logging
import structlog
from typing import Any
import sys


def setup_logging(
    log_level: str = "INFO",
    json_logs: bool = True,
    service_name: str = "hermes-api"
) -> None:
    """
    Configure structured logging for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_logs: Whether to output logs in JSON format
        service_name: Name of the service for log identification
    """

    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )

    # Shared processors for all logs
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    if json_logs:
        # Production: JSON formatting
        structlog.configure(
            processors=shared_processors + [
                structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
            ],
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

        formatter = structlog.stdlib.ProcessorFormatter(
            processor=structlog.processors.JSONRenderer(),
            foreign_pre_chain=shared_processors,
        )
    else:
        # Development: Console formatting
        structlog.configure(
            processors=shared_processors + [
                structlog.dev.ConsoleRenderer(),
            ],
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

        formatter = structlog.stdlib.ProcessorFormatter(
            processor=structlog.dev.ConsoleRenderer(),
            foreign_pre_chain=shared_processors,
        )

    # Apply formatter to root handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(getattr(logging, log_level.upper()))


def get_logger(name: str = None) -> Any:
    """
    Get a configured structlog logger.

    Args:
        name: Logger name (typically __name__ of the module)

    Returns:
        Configured structlog logger instance
    """
    return structlog.get_logger(name)


# Context management utilities
def bind_context(**kwargs) -> None:
    """
    Bind context variables that will be included in all subsequent logs.

    Example:
        bind_context(request_id="abc123", user_id="user-456")
    """
    structlog.contextvars.bind_contextvars(**kwargs)


def clear_context() -> None:
    """Clear all bound context variables."""
    structlog.contextvars.clear_contextvars()


def unbind_context(*keys) -> None:
    """
    Remove specific context variables.

    Args:
        *keys: Variable names to remove
    """
    structlog.contextvars.unbind_contextvars(*keys)
