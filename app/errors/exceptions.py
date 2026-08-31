from typing import Any, Dict, Optional


class AppException(Exception):
    """Base class for all domain-specific application exceptions."""

    status_code: int = 500
    error_code: str = "INTERNAL_SERVER_ERROR"
    message: str = "An unexpected internal server error occurred."

    def __init__(self, message: Optional[str] = None, details: Optional[Dict[str, Any]] = None, status_code: Optional[int] = None):
        super().__init__(message or self.message)
        if message:
            self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "success": False,
            "error": {
                "code": self.error_code,
                "message": self.message,
            },
        }
        if self.details:
            result["error"]["details"] = self.details
        return result


class ValidationError(AppException):
    """Raised when incoming user request payload or parameters fail schema validation."""
    status_code = 400
    error_code = "VALIDATION_ERROR"
    message = "Request validation failed."


class AuthenticationError(AppException):
    """Raised when user credentials are invalid or missing."""
    status_code = 401
    error_code = "AUTHENTICATION_FAILED"
    message = "Authentication required or credentials invalid."


class AuthorizationError(AppException):
    """Raised when authenticated user lacks permissions to access a resource."""
    status_code = 403
    error_code = "FORBIDDEN"
    message = "You do not have permission to perform this action."


class NotFoundError(AppException):
    """Raised when requested resource does not exist in database or filesystem."""
    status_code = 404
    error_code = "RESOURCE_NOT_FOUND"
    message = "The requested resource was not found."


class ConflictError(AppException):
    """Raised when creating a resource conflicts with an existing unique identifier."""
    status_code = 409
    error_code = "CONFLICT"
    message = "A conflict occurred with an existing resource."


class ArchiveExtractionError(AppException):
    """Raised when project archive decompression fails or violates security constraints."""
    status_code = 400
    error_code = "ARCHIVE_EXTRACTION_ERROR"
    message = "Failed to safely extract the uploaded archive file."


class SecurityViolationError(AppException):
    """Raised when malicious path traversal, zip slip, or quota breach is detected."""
    status_code = 400
    error_code = "SECURITY_VIOLATION"
    message = "Security constraint violation detected in uploaded artifact."


class ParserError(AppException):
    """Raised when AST parsing or syntax tree construction encounters an unrecoverable failure."""
    status_code = 422
    error_code = "PARSER_ERROR"
    message = "Source code parsing encountered an error."


class AnalysisTimeoutError(AppException):
    """Raised when an analysis pipeline exceeds allowed execution time limit."""
    status_code = 408
    error_code = "ANALYSIS_TIMEOUT"
    message = "The codebase analysis task timed out."


class RateLimitError(AppException):
    """Raised when client exceeds allowed request frequency."""
    status_code = 429
    error_code = "RATE_LIMIT_EXCEEDED"
    message = "Too many requests. Please slow down."
