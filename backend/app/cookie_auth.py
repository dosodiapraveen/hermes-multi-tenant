"""
Cookie-based authentication helpers.

Provides utilities for setting, clearing, and extracting authentication
tokens from httpOnly cookies instead of localStorage.
"""

from typing import Optional
from fastapi import Response, Request, Cookie
from datetime import datetime, timedelta
from app.config import settings
from app.logging_config import get_logger
from app.csrf import generate_csrf_token

logger = get_logger(__name__)


class CookieConfig:
    """Cookie configuration for different token types."""

    # Admin token configuration
    ADMIN_TOKEN_NAME = "admin_token"
    ADMIN_TOKEN_MAX_AGE = 28800  # 8 hours in seconds
    ADMIN_TOKEN_PATH = "/api/admin"

    # Portal (user) token configuration
    PORTAL_TOKEN_NAME = "portal_token"
    PORTAL_TOKEN_MAX_AGE = 2592000  # 30 days in seconds
    PORTAL_TOKEN_PATH = "/api"

    # CSRF token configuration
    CSRF_TOKEN_NAME = "csrf_token"
    CSRF_TOKEN_MAX_AGE = 2592000  # 30 days in seconds
    CSRF_TOKEN_PATH = "/"

    # Security flags
    SECURE = True  # HTTPS only (set to False for local development)
    HTTPONLY_AUTH = True  # Prevent JavaScript access to auth tokens
    HTTPONLY_CSRF = False  # CSRF token needs to be readable by JS
    SAMESITE_ADMIN = "lax"  # Allow cross-site for admin SSO
    SAMESITE_PORTAL = "strict"  # Strict for user portal
    SAMESITE_CSRF = "strict"  # Strict for CSRF tokens


def set_admin_auth_cookies(
    response: Response,
    token: str,
    admin_email: str
) -> None:
    """
    Set admin authentication cookies.

    Sets:
    - admin_token: httpOnly, Secure, 8-hour expiry
    - csrf_token: readable by JS, Secure, 8-hour expiry

    Args:
        response: FastAPI response object
        token: JWT token
        admin_email: Admin email for CSRF token generation
    """
    # Determine if we're in development mode
    secure = CookieConfig.SECURE and not settings.public_url.startswith("http://localhost")

    # Set authentication token (httpOnly)
    response.set_cookie(
        key=CookieConfig.ADMIN_TOKEN_NAME,
        value=token,
        max_age=CookieConfig.ADMIN_TOKEN_MAX_AGE,
        path=CookieConfig.ADMIN_TOKEN_PATH,
        secure=secure,
        httponly=CookieConfig.HTTPONLY_AUTH,
        samesite=CookieConfig.SAMESITE_ADMIN
    )

    # Generate and set CSRF token (readable by JS)
    csrf_token = generate_csrf_token("admin")
    response.set_cookie(
        key=CookieConfig.CSRF_TOKEN_NAME,
        value=csrf_token,
        max_age=CookieConfig.ADMIN_TOKEN_MAX_AGE,
        path="/",
        secure=secure,
        httponly=CookieConfig.HTTPONLY_CSRF,
        samesite=CookieConfig.SAMESITE_CSRF
    )

    logger.info("admin_cookies_set",
                admin_email=admin_email,
                secure=secure,
                token_expiry_hours=CookieConfig.ADMIN_TOKEN_MAX_AGE / 3600)


def set_portal_auth_cookies(
    response: Response,
    token: str,
    user_id: str
) -> None:
    """
    Set portal (user) authentication cookies.

    Sets:
    - portal_token: httpOnly, Secure, 30-day expiry
    - csrf_token: readable by JS, Secure, 30-day expiry

    Args:
        response: FastAPI response object
        token: Session token
        user_id: User profile ID for CSRF token generation
    """
    # Determine if we're in development mode
    secure = CookieConfig.SECURE and not settings.public_url.startswith("http://localhost")

    # Set authentication token (httpOnly)
    response.set_cookie(
        key=CookieConfig.PORTAL_TOKEN_NAME,
        value=token,
        max_age=CookieConfig.PORTAL_TOKEN_MAX_AGE,
        path=CookieConfig.PORTAL_TOKEN_PATH,
        secure=secure,
        httponly=CookieConfig.HTTPONLY_AUTH,
        samesite=CookieConfig.SAMESITE_PORTAL
    )

    # Generate and set CSRF token (readable by JS)
    csrf_token = generate_csrf_token(user_id)
    response.set_cookie(
        key=CookieConfig.CSRF_TOKEN_NAME,
        value=csrf_token,
        max_age=CookieConfig.PORTAL_TOKEN_MAX_AGE,
        path="/",
        secure=secure,
        httponly=CookieConfig.HTTPONLY_CSRF,
        samesite=CookieConfig.SAMESITE_CSRF
    )

    logger.info("portal_cookies_set",
                user_id=user_id,
                secure=secure,
                token_expiry_days=CookieConfig.PORTAL_TOKEN_MAX_AGE / 86400)


def clear_admin_cookies(response: Response) -> None:
    """
    Clear admin authentication cookies.

    Sets max_age=0 to immediately expire cookies.

    Args:
        response: FastAPI response object
    """
    response.set_cookie(
        key=CookieConfig.ADMIN_TOKEN_NAME,
        value="",
        max_age=0,
        path=CookieConfig.ADMIN_TOKEN_PATH,
        secure=True,
        httponly=True,
        samesite=CookieConfig.SAMESITE_ADMIN
    )

    response.set_cookie(
        key=CookieConfig.CSRF_TOKEN_NAME,
        value="",
        max_age=0,
        path="/",
        secure=True,
        httponly=False,
        samesite=CookieConfig.SAMESITE_CSRF
    )

    logger.info("admin_cookies_cleared")


def clear_portal_cookies(response: Response) -> None:
    """
    Clear portal (user) authentication cookies.

    Args:
        response: FastAPI response object
    """
    response.set_cookie(
        key=CookieConfig.PORTAL_TOKEN_NAME,
        value="",
        max_age=0,
        path=CookieConfig.PORTAL_TOKEN_PATH,
        secure=True,
        httponly=True,
        samesite=CookieConfig.SAMESITE_PORTAL
    )

    response.set_cookie(
        key=CookieConfig.CSRF_TOKEN_NAME,
        value="",
        max_age=0,
        path="/",
        secure=True,
        httponly=False,
        samesite=CookieConfig.SAMESITE_CSRF
    )

    logger.info("portal_cookies_cleared")


def get_token_from_cookie_or_header(
    request: Request,
    cookie_name: str,
    header_name: str = "Authorization"
) -> Optional[str]:
    """
    Extract authentication token from cookie or Authorization header.

    Supports dual-mode authentication during migration:
    1. Check cookie first (new method)
    2. Fall back to Authorization header (legacy method)

    Args:
        request: FastAPI request object
        cookie_name: Name of the cookie containing the token
        header_name: Name of the header (default: Authorization)

    Returns:
        Token string if found, None otherwise
    """
    # Try cookie first (new method)
    token = request.cookies.get(cookie_name)
    if token:
        logger.debug("token_from_cookie", cookie_name=cookie_name)
        return token

    # Fall back to Authorization header (legacy method)
    auth_header = request.headers.get(header_name)
    if auth_header:
        # Handle "Bearer <token>" format
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            logger.debug("token_from_header", header_name=header_name)
            return token
        # Handle raw token
        logger.debug("token_from_header_raw", header_name=header_name)
        return auth_header

    logger.debug("token_not_found", cookie_name=cookie_name, header_name=header_name)
    return None


def get_admin_token(request: Request) -> Optional[str]:
    """
    Get admin token from cookie or Authorization header.

    Args:
        request: FastAPI request object

    Returns:
        Admin token if found
    """
    return get_token_from_cookie_or_header(
        request,
        CookieConfig.ADMIN_TOKEN_NAME,
        "Authorization"
    )


def get_portal_token(request: Request) -> Optional[str]:
    """
    Get portal token from cookie or Authorization header.

    Args:
        request: FastAPI request object

    Returns:
        Portal token if found
    """
    return get_token_from_cookie_or_header(
        request,
        CookieConfig.PORTAL_TOKEN_NAME,
        "Authorization"
    )
