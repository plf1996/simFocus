"""
Custom exceptions for the application

Provides specific exception classes for different error scenarios.
Used for consistent error handling and HTTP responses.
"""
from typing import Any, Optional


class BaseAppException(Exception):
    """
    Base exception class for all application exceptions.

    Attributes:
        message: Human-readable error message
        code: Error code for programmatic handling
        status_code: HTTP status code (if applicable)
        details: Additional error details
    """

    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        status_code: Optional[int] = None,
        details: Optional[dict[str, Any]] = None,
    ):
        self.message = message
        self.code = code or self.__class__.__name__
        self.status_code = status_code or 500
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary for API responses."""
        result = {
            "error": self.code,
            "message": self.message,
        }
        if self.details:
            result["details"] = self.details
        return result

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message={self.message}, code={self.code})"


# HTTP 4xx Client Errors


class BadRequestException(BaseAppException):
    """400 Bad Request - Invalid request parameters."""

    def __init__(
        self,
        message: str = "Bad request",
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            code="BAD_REQUEST",
            status_code=400,
            details=details,
        )


class UnauthorizedException(BaseAppException):
    """401 Unauthorized - Authentication required or failed."""

    def __init__(
        self,
        message: str = "Unauthorized",
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            code="UNAUTHORIZED",
            status_code=401,
            details=details,
        )


class ForbiddenException(BaseAppException):
    """403 Forbidden - User lacks permission for this action."""

    def __init__(
        self,
        message: str = "Forbidden",
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            code="FORBIDDEN",
            status_code=403,
            details=details,
        )


class NotFoundException(BaseAppException):
    """404 Not Found - Resource not found."""

    def __init__(
        self,
        message: str = "Resource not found",
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            code="NOT_FOUND",
            status_code=404,
            details=details,
        )


class ConflictException(BaseAppException):
    """409 Conflict - Resource already exists or conflicts with state."""

    def __init__(
        self,
        message: str = "Resource conflict",
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            code="CONFLICT",
            status_code=409,
            details=details,
        )


class ValidationException(BaseAppException):
    """422 Unprocessable Entity - Validation error."""

    def __init__(
        self,
        message: str = "Validation error",
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=422,
            details=details,
        )


class RateLimitException(BaseAppException):
    """429 Too Many Requests - Rate limit exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            code="RATE_LIMIT_EXCEEDED",
            status_code=429,
            details=details,
        )


# HTTP 5xx Server Errors


class InternalServerException(BaseAppException):
    """500 Internal Server Error - Unexpected server error."""

    def __init__(
        self,
        message: str = "Internal server error",
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            code="INTERNAL_SERVER_ERROR",
            status_code=500,
            details=details,
        )


class BadGatewayException(BaseAppException):
    """502 Bad Gateway - External service error."""

    def __init__(
        self,
        message: str = "Bad gateway",
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            code="BAD_GATEWAY",
            status_code=502,
            details=details,
        )


class ServiceUnavailableException(BaseAppException):
    """503 Service Unavailable - Service temporarily unavailable."""

    def __init__(
        self,
        message: str = "Service unavailable",
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            code="SERVICE_UNAVAILABLE",
            status_code=503,
            details=details,
        )


# Domain-Specific Exceptions


class UserNotFoundException(NotFoundException):
    """User not found."""

    def __init__(self, user_id: Optional[str] = None):
        message = "User not found"
        details = {"user_id": str(user_id)} if user_id else None
        super().__init__(message=message, details=details)


class DuplicateUserException(ConflictException):
    """User already exists."""

    def __init__(self, email: Optional[str] = None):
        message = "User already exists"
        details = {"email": email} if email else None
        super().__init__(message=message, details=details)


class InvalidCredentialsException(UnauthorizedException):
    """Invalid authentication credentials."""

    def __init__(self):
        super().__init__(message="Invalid email or password")


class InvalidTokenException(UnauthorizedException):
    """Invalid or expired token."""

    def __init__(self, message: str = "Invalid or expired token"):
        super().__init__(message=message)


class TopicNotFoundException(NotFoundException):
    """Topic not found."""

    def __init__(self, topic_id: Optional[str] = None):
        message = "Topic not found"
        details = {"topic_id": str(topic_id)} if topic_id else None
        super().__init__(message=message, details=details)


class CharacterNotFoundException(NotFoundException):
    """Character not found."""

    def __init__(self, character_id: Optional[str] = None):
        message = "Character not found"
        details = {"character_id": str(character_id)} if character_id else None
        super().__init__(message=message, details=details)


class DiscussionNotFoundException(NotFoundException):
    """Discussion not found."""

    def __init__(self, discussion_id: Optional[str] = None):
        message = "Discussion not found"
        details = {"discussion_id": str(discussion_id)} if discussion_id else None
        super().__init__(message=message, details=details)


class DiscussionNotActiveException(BadRequestException):
    """Discussion is not in active state."""

    def __init__(self, discussion_id: str, current_state: str):
        message = "Discussion is not in active state"
        details = {
            "discussion_id": str(discussion_id),
            "current_state": current_state,
        }
        super().__init__(message=message, details=details)


class APIKeyNotFoundException(NotFoundException):
    """API key not found for user."""

    def __init__(self, provider: str, user_id: Optional[str] = None):
        message = f"API key not found for provider: {provider}"
        details = {"provider": provider, "user_id": str(user_id)} if user_id else {"provider": provider}
        super().__init__(message=message, details=details)


class ExternalAPIException(BadGatewayException):
    """External API call failed."""

    def __init__(
        self,
        provider: str,
        message: Optional[str] = None,
        status_code: Optional[int] = None,
    ):
        message = message or f"External API call failed: {provider}"
        details = {"provider": provider}
        if status_code:
            details["status_code"] = status_code
        super().__init__(message=message, details=details)


class EncryptionException(InternalServerException):
    """Encryption/decryption error."""

    def __init__(self, message: str = "Encryption operation failed"):
        super().__init__(message=message, code="ENCRYPTION_ERROR")
