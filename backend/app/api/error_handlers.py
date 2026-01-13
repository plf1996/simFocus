"""
Global exception handlers for the API

Provides comprehensive error handling for all API endpoints including:
- ValidationError (Pydantic validation errors)
- HTTPException (FastAPI HTTP exceptions)
- Generic exceptions (unexpected errors)
- Custom application exceptions
"""
import logging
from typing import Any, Union

from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.core.exceptions import BaseAppException

# Configure logger
logger = logging.getLogger(__name__)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handle FastAPI HTTPException.

    Args:
        request: The incoming request
        exc: The HTTPException raised

    Returns:
        JSONResponse with error details
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": _get_error_code_from_status(exc.status_code),
            "message": exc.detail,
        },
    )


async def validation_exception_handler(
    request: Request,
    exc: Union[RequestValidationError, ValidationError]
) -> JSONResponse:
    """
    Handle Pydantic validation errors from request body/query/path parameters.

    Args:
        request: The incoming request
        exc: The validation error raised

    Returns:
        JSONResponse with detailed validation error information
    """
    # Format validation errors for better readability
    formatted_errors = []
    errors = exc.errors() if isinstance(exc, RequestValidationError) else exc.errors()

    for error in errors:
        location = " -> ".join(str(loc) for loc in error["loc"])
        formatted_errors.append({
            "location": location,
            "message": error["msg"],
            "type": error["type"],
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "VALIDATION_ERROR",
            "message": "Request validation failed",
            "details": {
                "errors": formatted_errors,
                "error_count": len(formatted_errors),
            },
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle all unhandled exceptions.

    Logs the error and returns a generic error response to the client.
    Detailed stack traces are logged but not exposed to clients for security.

    Args:
        request: The incoming request
        exc: The unhandled exception

    Returns:
        JSONResponse with generic error message
    """
    # Log the full error with stack trace
    logger.error(
        f"Unhandled exception on {request.method} {request.url.path}: {str(exc)}",
        exc_info=True,
        extra={
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "client": request.client.host if request.client else None,
        },
    )

    # Return generic error message (don't expose internal details)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred. Please try again later.",
        },
    )


async def base_app_exception_handler(request: Request, exc: BaseAppException) -> JSONResponse:
    """
    Handle custom application exceptions.

    All custom exceptions inherit from BaseAppException and include
    error codes, messages, and optional details.

    Args:
        request: The incoming request
        exc: The BaseAppException raised

    Returns:
        JSONResponse formatted from exception's to_dict() method
    """
    # Log application exceptions (excluding 404s to reduce noise)
    if exc.status_code != 404:
        logger.warning(
            f"Application exception on {request.method} {request.url.path}: {exc.code} - {exc.message}",
            extra={
                "method": request.method,
                "url": str(request.url),
                "path": request.url.path,
                "error_code": exc.code,
                "details": exc.details,
            },
        )

    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict(),
    )


def _get_error_code_from_status(status_code: int) -> str:
    """
    Convert HTTP status code to error code string.

    Args:
        status_code: HTTP status code

    Returns:
        Error code string (e.g., 404 -> "NOT_FOUND")
    """
    status_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        409: "CONFLICT",
        422: "VALIDATION_ERROR",
        429: "RATE_LIMIT_EXCEEDED",
        500: "INTERNAL_SERVER_ERROR",
        502: "BAD_GATEWAY",
        503: "SERVICE_UNAVAILABLE",
    }
    return status_map.get(status_code, "HTTP_ERROR")


def register_exception_handlers(app) -> None:
    """
    Register all exception handlers with the FastAPI application.

    Args:
        app: FastAPI application instance

    Example:
        >>> from app.main import app
        >>> from app.api.error_handlers import register_exception_handlers
        >>> register_exception_handlers(app)
    """
    # Custom application exceptions
    app.add_exception_handler(BaseAppException, base_app_exception_handler)

    # FastAPI HTTPException
    app.add_exception_handler(HTTPException, http_exception_handler)

    # Pydantic validation errors
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(ValidationError, validation_exception_handler)

    # Catch-all for any other exceptions
    app.add_exception_handler(Exception, generic_exception_handler)
