"""Unofficial Python wrapper for the undocumented API of <a href="https://streamable.com">streamable.com</a>

This package provides a comprehensive Python interface for interacting with
the undocumented Streamable.com API, enabling video uploads, account management,
and various other operations.

Authentication:
    This library supports email + password authentication only.
    Google and Facebook login methods are not supported.
"""

from .api.client import StreamableClient
from .api.models import (
    AccountInfo,
    StreamableUser,
    StreamableUnauthenticatedUser,
    Label,
    UserLabel,
    Video,
    UploadInfo,
    PrivacySettings,
    Plan,
    Feature,
    PlanPricing,
    Limits,
    StorageLimits,
)
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

__version__ = "0.1.0"
__author__ = "madkarmaa"
__email__ = "your-email@example.com"
__license__ = "MIT"

__all__ = [
    # Main client
    "StreamableClient",
    # Data models
    "AccountInfo",
    "StreamableUser",
    "StreamableUnauthenticatedUser",
    "Label",
    "UserLabel",
    "Video",
    "UploadInfo",
    "PrivacySettings",
    "Plan",
    "Feature",
    "PlanPricing",
    "Limits",
    "StorageLimits",
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
