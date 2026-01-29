"""
Secure error handling for Mkaguzi
"""
import frappe
import traceback
from typing import Dict, Any, Optional
import logging

# Configure secure logger
logger = logging.getLogger(__name__)

class SecuritySensitiveError(Exception):
    """Base class for errors that may contain sensitive information"""
    pass

class SecureErrorHandler:
    """Handles errors securely without exposing sensitive data"""

    # Fields that should never appear in error messages
    SENSITIVE_PATTERNS = [
        'password', 'token', 'secret', 'key', 'credential',
        'ssn', 'credit_card', 'bank_account', 'pin'
    ]

    @classmethod
    def sanitize_error_message(cls, error_message: str) -> str:
        """
        Sanitize error message to remove sensitive information

        Args:
            error_message: Raw error message

        Returns:
            Sanitized error message safe for logging/display
        """
        if not error_message:
            return "An error occurred"

        sanitized = str(error_message)

        # Remove sensitive patterns
        for pattern in cls.SENSITIVE_PATTERNS:
            if pattern.lower() in sanitized.lower():
                sanitized = "Error: Sensitive information redacted"

        # Limit length
        if len(sanitized) > 200:
            sanitized = sanitized[:200] + "..."

        return sanitized

    @classmethod
    def log_error_securely(cls, error: Exception, context: Optional[Dict] = None) -> str:
        """
        Log error securely

        Args:
            error: The exception that occurred
            context: Optional context dictionary

        Returns:
            Sanitized error message for user display
        """
        # Log full details to secure log file (not accessible to users)
        secure_log_msg = f"Error: {type(error).__name__}"
        if context:
            secure_log_msg += f" | Context: {context}"

        logger.error(secure_log_msg, exc_info=True)

        # Log to Frappe error log (sanitized)
        sanitized_msg = cls.sanitize_error_message(str(error))
        frappe.log_error(
            f"{sanitized_msg} | See secure logs for details",
            title="Mkaguzi Error"
        )

        # Return user-safe message
        return "An error occurred. Please contact support if the problem persists."

    @classmethod
    def handle_api_error(cls, error: Exception, operation: str) -> Dict[str, Any]:
        """
        Handle API errors with secure response

        Args:
            error: The exception that occurred
            operation: Description of the operation being performed

        Returns:
            Secure error response dictionary
        """
        user_message = cls.log_error_securely(error, {'operation': operation})

        return {
            'success': False,
            'error': user_message,
            'error_code': type(error).__name__,
            'operation': operation
        }

    @classmethod
    def raise_user_error(cls, message: str, title: str = "Error"):
        """
        Raise a user-facing error with proper logging

        Args:
            message: Error message to display to user
            title: Error title
        """
        sanitized = cls.sanitize_error_message(message)
        frappe.throw(sanitized, title=title)