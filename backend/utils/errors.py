"""Custom exceptions used across the backend services and modules."""

class APIServiceError(Exception):
    """Raised when an external API call fails or returns invalid data."""


class InvalidInputError(Exception):
    """Raised when provided input is invalid or insufficient."""


# Audio / ASR specific errors (used by modules/asr.py)
class AudioProcessingError(Exception):
    """Raised when audio processing fails."""


class TranscriptionError(Exception):
    """Raised when speech-to-text transcription fails."""


class ConfigurationError(Exception):
    """Raised when required configuration is missing or invalid."""

"""
Custom exceptions for the application.
"""

class AppError(Exception):
    """Base exception for all application errors."""
    def __init__(self, message: str, code: str = None, status_code: int = 500, **kwargs):
        self.message = message
        self.code = code or "app_error"
        self.status_code = status_code
        self.details = kwargs
        super().__init__(self.message)

class ValidationError(AppError):
    """Raised when input validation fails."""
    def __init__(self, message: str = "Invalid input", **kwargs):
        super().__init__(
            message=message,
            code="validation_error",
            status_code=400,
            **kwargs
        )

class AuthenticationError(AppError):
    """Raised when authentication fails."""
    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(
            message=message,
            code="authentication_error",
            status_code=401,
            **kwargs
        )

class AuthorizationError(AppError):
    """Raised when a user is not authorized to perform an action."""
    def __init__(self, message: str = "Not authorized", **kwargs):
        super().__init__(
            message=message,
            code="authorization_error",
            status_code=403,
            **kwargs
        )

class NotFoundError(AppError):
    """Raised when a requested resource is not found."""
    def __init__(self, resource: str = "Resource", **kwargs):
        super().__init__(
            message=f"{resource} not found",
            code="not_found",
            status_code=404,
            **kwargs
        )

class ConflictError(AppError):
    """Raised when a resource conflict occurs."""
    def __init__(self, message: str = "Resource conflict", **kwargs):
        super().__init__(
            message=message,
            code="conflict",
            status_code=409,
            **kwargs
        )

class RateLimitError(AppError):
    """Raised when rate limits are exceeded."""
    def __init__(self, message: str = "Rate limit exceeded", **kwargs):
        super().__init__(
            message=message,
            code="rate_limit_exceeded",
            status_code=429,
            **kwargs
        )

class ServiceError(AppError):
    """Raised when an external service fails."""
    def __init__(self, service: str, message: str = "Service error", **kwargs):
        super().__init__(
            message=f"{service} error: {message}",
            code=f"{service.lower()}_error",
            status_code=502,
            **kwargs
        )

class ASRServiceError(ServiceError):
    """Raised when there's an error with the ASR service."""
    def __init__(self, message: str = "Speech recognition error", **kwargs):
        super().__init__(
            service="ASR",
            message=message,
            **kwargs
        )

class AudioProcessingError(ASRServiceError):
    """Raised when there's an error processing audio data."""
    def __init__(self, message: str = "Audio processing error", **kwargs):
        super().__init__(message=message, **kwargs)
        self.code = "audio_processing_error"

class TranscriptionError(ASRServiceError):
    """Raised when there's an error during speech-to-text conversion."""
    def __init__(self, message: str = "Transcription failed", **kwargs):
        super().__init__(message=message, **kwargs)
        self.code = "transcription_error"

class ConfigurationError(AppError):
    """Raised when there's a configuration error."""
    def __init__(self, message: str = "Configuration error", **kwargs):
        super().__init__(
            message=message,
            code="configuration_error",
            status_code=500,
            **kwargs
        )

class TextToSpeechError(ServiceError):
    """Raised when there's an error with the Text-to-Speech service."""
    def __init__(self, message: str = "Text-to-speech error", **kwargs):
        super().__init__(
            service="TTS",
            message=message,
            **kwargs
        )

def error_response(error: Exception) -> dict:
    """Convert an exception to a standardized error response."""
    if isinstance(error, AppError):
        return {
            "error": {
                "code": error.code,
                "message": str(error.message),
                "details": getattr(error, "details", {})
            }
        }, error.status_code
    
    # Handle unexpected errors
    return {
        "error": {
            "code": "internal_server_error",
            "message": "An unexpected error occurred",
            "details": {"error": str(error)}
        }
    }, 500