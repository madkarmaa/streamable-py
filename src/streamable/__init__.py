"""Unofficial Python wrapper for the undocumented API of <a href="https://streamable.com">streamable.com</a>.

This package provides a comprehensive Python interface for interacting with
the undocumented Streamable.com API, enabling video uploads, account management,
and various other operations.

Authentication:
    This library supports email + password authentication only.
    Google and Facebook login methods are not supported.

Limitations:
    - Free account limits: 250MB file size, 10 minute duration per video
"""

from .api.client import StreamableClient
from .api.models import AccountInfo
from .api.exceptions import (
    StreamableError,
    InvalidCredentialsError,
    EmailAlreadyInUseError,
    InvalidSessionError,
    PasswordValidationError,
    InvalidPlayerColorError,
    InvalidPrivacySettingsError,
    LabelAlreadyExistsError,
    VideoTooLargeError,
    VideoTooLongError,
)

__all__ = [
    # Main client
    "StreamableClient",
    # Data models
    "AccountInfo",
    # Exceptions
    "StreamableError",
    "InvalidCredentialsError",
    "EmailAlreadyInUseError",
    "InvalidSessionError",
    "PasswordValidationError",
    "InvalidPlayerColorError",
    "InvalidPrivacySettingsError",
    "LabelAlreadyExistsError",
    "VideoTooLargeError",
    "VideoTooLongError",
]
