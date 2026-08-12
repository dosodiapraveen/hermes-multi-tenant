"""
Logging middleware for request correlation and context tracking.

Adds unique request IDs to all requests and binds contextual information
like IP address, user agent, and user ID for comprehensive audit trails.
"""

import time
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.logging_config import get_logger, bind_context, clear_context

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that adds request correlation IDs and logs all HTTP requests.

    For each request:
    - Generates unique request_id
    - Binds request context (IP, user agent, method, path)
    - Logs request start and completion with duration
    - Clears context after request completes
    """

    async def dispatch(self, request: Request, call_next):
        # Generate unique request ID
        request_id = str(uuid.uuid4())

        # Extract client information
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "unknown")

        # Bind context for all logs in this request
        bind_context(
            request_id=request_id,
            ip_address=client_ip,
            user_agent=user_agent,
            method=request.method,
            path=request.url.path,
        )

        # Add request_id to request state for access in handlers
        request.state.request_id = request_id

        # Log request start
        logger.info(
            "request_started",
            method=request.method,
            path=request.url.path,
            query_params=str(request.query_params),
        )

        # Process request and measure duration
        start_time = time.time()
        try:
            response = await call_next(request)
            duration_ms = (time.time() - start_time) * 1000

            # Add request_id to response headers for client tracking
            response.headers["X-Request-ID"] = request_id

            # Log request completion
            logger.info(
                "request_completed",
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2),
            )

            # Detect slow requests (>1 second)
            if duration_ms > 1000:
                logger.warning(
                    "slow_request_detected",
                    duration_ms=round(duration_ms, 2),
                    threshold_ms=1000,
                )

            return response

        except Exception as exc:
            duration_ms = (time.time() - start_time) * 1000

            # Log request failure
            logger.error(
                "request_failed",
                error=str(exc),
                error_type=type(exc).__name__,
                duration_ms=round(duration_ms, 2),
                exc_info=True,
            )
            raise

        finally:
            # Clear context to prevent leakage between requests
            clear_context()

    @staticmethod
    def _get_client_ip(request: Request) -> str:
        """
        Extract client IP address, accounting for proxies.

        Checks X-Forwarded-For header first (for reverse proxy setups),
        then falls back to direct client address.
        """
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # X-Forwarded-For can contain multiple IPs, take the first
            return forwarded_for.split(",")[0].strip()

        if request.client:
            return request.client.host

        return "unknown"
