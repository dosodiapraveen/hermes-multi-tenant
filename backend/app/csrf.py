"""
CSRF (Cross-Site Request Forgery) protection using stateless tokens.

Implements HMAC-signed tokens with user_id and timestamp to prevent
CSRF attacks on state-changing operations.
"""

import hmac
import hashlib
import time
import secrets
from typing import Optional, Tuple
from fastapi import HTTPException, Request, Cookie, Header
from app.config import settings
from app.logging_config import get_logger

logger = get_logger(__name__)

# Token validity period (24 hours)
CSRF_TOKEN_EXPIRY = 86400  # seconds


def generate_csrf_token(user_id: str) -> str:
    """
    Generate a stateless CSRF token for a user.

    Token format: {timestamp}.{user_id}.{hmac_signature}

    Args:
        user_id: User identifier (profile_id or 'admin')

    Returns:
        CSRF token string
    """
    timestamp = str(int(time.time()))

    # Create message to sign: timestamp.user_id
    message = f"{timestamp}.{user_id}"

    # Generate HMAC signature
    signature = hmac.new(
        settings.supabase_jwt_secret.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()

    # Combine into final token
    token = f"{timestamp}.{user_id}.{signature}"

    logger.debug("csrf_token_generated", user_id=user_id)
    return token


def validate_csrf_token(token: str, expected_user_id: str) -> bool:
    """
    Validate a CSRF token.

    Checks:
    1. Token format is correct
    2. Signature is valid
    3. Token hasn't expired
    4. User ID matches expected value

    Args:
        token: CSRF token to validate
        expected_user_id: Expected user ID from session

    Returns:
        True if valid, False otherwise
    """
    if not token:
        logger.warning("csrf_validation_failed", reason="missing_token")
        return False

    try:
        # Parse token components
        parts = token.split('.')
        if len(parts) != 3:
            logger.warning("csrf_validation_failed", reason="invalid_format")
            return False

        timestamp_str, user_id, provided_signature = parts

        # Check user ID matches
        if user_id != expected_user_id:
            logger.warning("csrf_validation_failed",
                          reason="user_id_mismatch",
                          expected=expected_user_id,
                          provided=user_id)
            return False

        # Check token hasn't expired
        timestamp = int(timestamp_str)
        current_time = int(time.time())
        age = current_time - timestamp

        if age > CSRF_TOKEN_EXPIRY:
            logger.warning("csrf_validation_failed",
                          reason="token_expired",
                          age_seconds=age)
            return False

        if age < -60:  # Token from future (clock skew tolerance: 1 minute)
            logger.warning("csrf_validation_failed",
                          reason="token_from_future",
                          age_seconds=age)
            return False

        # Verify signature using constant-time comparison
        message = f"{timestamp_str}.{user_id}"
        expected_signature = hmac.new(
            settings.supabase_jwt_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(provided_signature, expected_signature):
            logger.warning("csrf_validation_failed", reason="invalid_signature")
            return False

        logger.debug("csrf_token_validated", user_id=user_id)
        return True

    except (ValueError, IndexError) as e:
        logger.warning("csrf_validation_failed",
                      reason="parse_error",
                      error=str(e))
        return False


async def verify_csrf_token(
    request: Request,
    csrf_token_header: Optional[str] = Header(None, alias="X-CSRF-Token"),
    csrf_token_cookie: Optional[str] = Cookie(None, alias="csrf_token")
) -> None:
    """
    FastAPI dependency to verify CSRF token on protected endpoints.

    Validates that:
    1. CSRF token is present in both header and cookie
    2. Header and cookie values match (double-submit cookie pattern)
    3. Token is valid (signature, expiry, user ID)

    Args:
        request: FastAPI request object
        csrf_token_header: CSRF token from X-CSRF-Token header
        csrf_token_cookie: CSRF token from cookie

    Raises:
        HTTPException: 403 if CSRF validation fails
    """
    # Skip CSRF check for GET, HEAD, OPTIONS (safe methods)
    if request.method in ["GET", "HEAD", "OPTIONS"]:
        return

    # Get user ID from request state (set by auth middleware)
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        # If no user in session, CSRF not applicable
        return

    # Check both tokens are present
    if not csrf_token_header:
        logger.warning("csrf_check_failed",
                      reason="missing_header",
                      user_id=user_id,
                      method=request.method,
                      path=request.url.path)
        raise HTTPException(403, "CSRF token required in X-CSRF-Token header")

    if not csrf_token_cookie:
        logger.warning("csrf_check_failed",
                      reason="missing_cookie",
                      user_id=user_id,
                      method=request.method,
                      path=request.url.path)
        raise HTTPException(403, "CSRF token cookie required")

    # Double-submit cookie pattern: header and cookie must match
    if not hmac.compare_digest(csrf_token_header, csrf_token_cookie):
        logger.warning("csrf_check_failed",
                      reason="token_mismatch",
                      user_id=user_id,
                      method=request.method,
                      path=request.url.path)
        raise HTTPException(403, "CSRF token mismatch")

    # Validate token signature and expiry
    if not validate_csrf_token(csrf_token_header, user_id):
        logger.warning("csrf_check_failed",
                      reason="invalid_token",
                      user_id=user_id,
                      method=request.method,
                      path=request.url.path)
        raise HTTPException(403, "Invalid or expired CSRF token")

    logger.debug("csrf_check_passed", user_id=user_id, method=request.method)


def create_csrf_dependency(required: bool = True):
    """
    Create a CSRF verification dependency with configurable requirement.

    Args:
        required: If False, logs warning but doesn't block request

    Returns:
        FastAPI dependency function
    """
    async def csrf_dependency(
        request: Request,
        csrf_token_header: Optional[str] = Header(None, alias="X-CSRF-Token"),
        csrf_token_cookie: Optional[str] = Cookie(None, alias="csrf_token")
    ):
        if required:
            await verify_csrf_token(request, csrf_token_header, csrf_token_cookie)
        else:
            # Soft enforcement mode: log but don't block
            try:
                await verify_csrf_token(request, csrf_token_header, csrf_token_cookie)
            except HTTPException as e:
                logger.warning("csrf_soft_check_failed",
                              error=str(e.detail),
                              path=request.url.path)

    return csrf_dependency


# Default CSRF dependency (enforced)
require_csrf = verify_csrf_token

# Soft CSRF dependency (logs only, for gradual rollout)
log_csrf = create_csrf_dependency(required=False)
