"""Custom exceptions for aemon library."""


class AemonError(Exception):
    """Base exception for aemon library."""
    pass


class FastAPIAppNotFoundError(AemonError):
    """Raised when FastAPI app cannot be found in the specified module."""
    pass


class InvalidModulePathError(AemonError):
    """Raised when module path is invalid or cannot be imported."""
    pass


class ConfigurationError(AemonError):
    """Raised when configuration is invalid."""
    pass


class GenerationError(AemonError):
    """Raised when OpenAPI generation fails."""
    pass