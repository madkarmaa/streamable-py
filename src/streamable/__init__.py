"""Streamable.py - Unofficial Python wrapper for the Streamable.com API.

This package provides a comprehensive Python interface for interacting with
the undocumented Streamable.com API, enabling video uploads, account management,
and various other operations.

Example:
    Basic usage with the StreamableClient:

    ```python
    from streamable_py import StreamableClient, AccountInfo
    from pathlib import Path

    # Create account info
    account = AccountInfo(email="your@email.com", password="your_password")

    # Use the client
    with StreamableClient() as client:
        client.login(account)
        video = client.upload_video(Path("video.mp4"))
        print(f"Uploaded video: {video.url}")
    ```

Modules:
    api: Core API client and models for Streamable.com interaction
    utils: Utility functions for video processing and AWS S3 operations
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
