#!/usr/bin/env python3
"""
Custom exception classes for better error handling
"""


class PublitzError(Exception):
    """Base exception for all Publitz errors"""

    def __init__(self, message: str, user_message: str = None, recoverable: bool = True):
        """
        Initialize exception

        Args:
            message: Technical error message (for logs)
            user_message: User-friendly message (for UI display)
            recoverable: Whether the error is recoverable (retry possible)
        """
        super().__init__(message)
        self.message = message
        self.user_message = user_message or message
        self.recoverable = recoverable


# API-related errors
class APIError(PublitzError):
    """Base class for API errors"""
    pass


class SteamAPIError(APIError):
    """Steam API errors"""

    def __init__(self, message: str, app_id: int = None):
        user_msg = f"Unable to fetch game data from Steam. The game may be private or unavailable."
        super().__init__(message, user_msg, recoverable=True)
        self.app_id = app_id


class SteamSpyAPIError(APIError):
    """SteamSpy API errors"""

    def __init__(self, message: str, app_id: int = None):
        user_msg = "Unable to fetch sales data from SteamSpy. This may be temporary."
        super().__init__(message, user_msg, recoverable=True)
        self.app_id = app_id


class RateLimitError(APIError):
    """Rate limit exceeded"""

    def __init__(self, service: str, retry_after: int = None):
        message = f"Rate limit exceeded for {service}"
        user_msg = f"Too many requests to {service}. Please try again in a few moments."
        super().__init__(message, user_msg, recoverable=True)
        self.service = service
        self.retry_after = retry_after


class AIGenerationError(APIError):
    """AI report generation errors"""

    def __init__(self, message: str, provider: str = "Claude"):
        user_msg = f"Failed to generate report using {provider}. Please check your API key and try again."
        super().__init__(message, user_msg, recoverable=True)
        self.provider = provider


class AuthenticationError(PublitzError):
    """Authentication errors"""

    def __init__(self, service: str):
        message = f"Authentication failed for {service}"
        user_msg = f"Invalid API key for {service}. Please check your credentials."
        super().__init__(message, user_msg, recoverable=False)
        self.service = service


# Data validation errors
class ValidationError(PublitzError):
    """Data validation errors"""
    pass


class InvalidSteamURLError(ValidationError):
    """Invalid Steam URL"""

    def __init__(self, url: str):
        message = f"Invalid Steam URL: {url}"
        user_msg = "Invalid Steam URL. Please provide a valid Steam store URL (e.g., https://store.steampowered.com/app/12345/...)"
        super().__init__(message, user_msg, recoverable=False)
        self.url = url


class GameNotFoundError(ValidationError):
    """Game not found"""

    def __init__(self, app_id: int):
        message = f"Game not found: {app_id}"
        user_msg = f"Game with App ID {app_id} not found on Steam. The game may be delisted or private."
        super().__init__(message, user_msg, recoverable=False)
        self.app_id = app_id


class NoCompetitorsFoundError(ValidationError):
    """No competitors found"""

    def __init__(self, game_name: str):
        message = f"No competitors found for {game_name}"
        user_msg = "Unable to find competitor games for analysis. This may be a very unique game."
        super().__init__(message, user_msg, recoverable=True)
        self.game_name = game_name


# System errors
class TimeoutError(PublitzError):
    """Timeout errors"""

    def __init__(self, operation: str, timeout: int):
        message = f"Timeout after {timeout}s during {operation}"
        user_msg = f"Operation timed out: {operation}. Please try again."
        super().__init__(message, user_msg, recoverable=True)
        self.operation = operation
        self.timeout = timeout


class DataSourceError(PublitzError):
    """All data sources failed"""

    def __init__(self, sources: list):
        message = f"All data sources failed: {', '.join(sources)}"
        user_msg = "Unable to fetch data from any available sources. This may be a temporary issue."
        super().__init__(message, user_msg, recoverable=True)
        self.sources = sources


class PDFGenerationError(PublitzError):
    """PDF generation errors"""

    def __init__(self, message: str):
        user_msg = "Failed to generate PDF report. You can still download the Markdown version."
        super().__init__(message, user_msg, recoverable=False)
