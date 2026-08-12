"""
Audit logging service for security events.

Provides centralized audit logging for authentication, authorization,
and administrative actions with database persistence.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from app.logging_config import get_logger
from app.database import get_db_pool

logger = get_logger(__name__)


class AuditLogger:
    """
    Service for logging security-critical events to audit_logs table.

    Events are logged both to structured logs (for real-time monitoring)
    and to the database (for compliance and long-term analysis).
    """

    # Event categories
    class EventType:
        # Authentication events
        LOGIN_SUCCESS = "login_success"
        LOGIN_FAILED = "login_failed"
        LOGOUT = "logout"
        PASSWORD_RESET_REQUEST = "password_reset_request"
        PASSWORD_RESET_SUCCESS = "password_reset_success"
        EMAIL_VERIFICATION = "email_verification"
        REGISTRATION = "registration"

        # Authorization events
        UNAUTHORIZED_ACCESS = "unauthorized_access"
        PERMISSION_DENIED = "permission_denied"

        # Admin events
        ADMIN_LOGIN = "admin_login"
        ADMIN_LOGIN_FAILED = "admin_login_failed"
        USER_CREATED = "user_created"
        USER_UPDATED = "user_updated"
        USER_DELETED = "user_deleted"
        API_KEY_CREATED = "api_key_created"
        API_KEY_DELETED = "api_key_deleted"
        MODEL_OVERRIDE = "model_override"
        SKILL_DEPLOYED = "skill_deployed"

        # Webhook events
        WEBHOOK_SIGNATURE_FAILED = "webhook_signature_failed"
        WEBHOOK_MESSAGE_RECEIVED = "webhook_message_received"
        WEBHOOK_DOCUMENT_UPLOAD = "webhook_document_upload"

        # System events
        RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
        SLOW_QUERY = "slow_query"
        AI_MODEL_FAILURE = "ai_model_failure"

    # Severity levels
    class Severity:
        INFO = "info"
        WARNING = "warning"
        ERROR = "error"
        CRITICAL = "critical"

    @staticmethod
    async def log_event(
        event_type: str,
        severity: str = Severity.INFO,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_id: Optional[str] = None,
        admin_email: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log a security event to both structured logs and database.

        Args:
            event_type: Type of event (use EventType constants)
            severity: Event severity (use Severity constants)
            user_id: User profile ID or auth_user_id involved
            ip_address: Client IP address
            user_agent: Client user agent
            request_id: Request correlation ID
            admin_email: Email of admin performing action (for admin events)
            details: Additional event-specific data as JSON
        """
        # Log to structured logs for real-time monitoring
        log_data = {
            "event": event_type,
            "severity": severity,
        }

        if user_id:
            log_data["user_id"] = user_id
        if ip_address:
            log_data["ip_address"] = ip_address
        if request_id:
            log_data["request_id"] = request_id
        if admin_email:
            log_data["admin_email"] = admin_email
        if details:
            log_data["details"] = details

        # Use appropriate log level based on severity
        if severity == AuditLogger.Severity.CRITICAL:
            logger.critical("audit_event", **log_data)
        elif severity == AuditLogger.Severity.ERROR:
            logger.error("audit_event", **log_data)
        elif severity == AuditLogger.Severity.WARNING:
            logger.warning("audit_event", **log_data)
        else:
            logger.info("audit_event", **log_data)

        # Persist to database for long-term audit trail
        try:
            pool = get_db_pool()
            async with pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO audit_logs
                    (event_type, severity, user_id, ip_address, user_agent,
                     request_id, admin_email, details, timestamp)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                    """,
                    event_type,
                    severity,
                    user_id,
                    ip_address,
                    user_agent,
                    request_id,
                    admin_email,
                    details or {},
                    datetime.utcnow(),
                )
        except Exception as e:
            # Never fail the request due to audit logging issues
            logger.error(
                "audit_log_db_error",
                error=str(e),
                event_type=event_type,
                exc_info=True,
            )

    @staticmethod
    async def log_auth_event(
        event_type: str,
        success: bool,
        email: Optional[str] = None,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        request_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Convenience method for logging authentication events.

        Args:
            event_type: Type of auth event
            success: Whether the auth attempt succeeded
            email: Email address used in attempt
            user_id: User ID if auth succeeded
            ip_address: Client IP address
            request_id: Request correlation ID
            details: Additional details
        """
        severity = AuditLogger.Severity.INFO if success else AuditLogger.Severity.WARNING

        event_details = details or {}
        if email:
            event_details["email"] = email

        await AuditLogger.log_event(
            event_type=event_type,
            severity=severity,
            user_id=user_id,
            ip_address=ip_address,
            request_id=request_id,
            details=event_details,
        )

    @staticmethod
    async def log_admin_event(
        event_type: str,
        admin_email: str,
        ip_address: Optional[str] = None,
        request_id: Optional[str] = None,
        target_user_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Convenience method for logging administrative actions.

        Args:
            event_type: Type of admin event
            admin_email: Email of admin performing action
            ip_address: Admin's IP address
            request_id: Request correlation ID
            target_user_id: ID of user being affected
            details: Additional action details
        """
        event_details = details or {}
        if target_user_id:
            event_details["target_user_id"] = target_user_id

        await AuditLogger.log_event(
            event_type=event_type,
            severity=AuditLogger.Severity.INFO,
            ip_address=ip_address,
            request_id=request_id,
            admin_email=admin_email,
            details=event_details,
        )


# Convenience instance for easy imports
audit_logger = AuditLogger()
