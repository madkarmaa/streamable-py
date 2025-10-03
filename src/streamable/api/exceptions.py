"""Custom exceptions for the Streamable.com API client.

This module defines all custom exception classes used throughout the library
to handle various error conditions when interacting with the Streamable.com API.
"""

from pathlib import Path


class StreamableError(Exception):
    """Base exception class for all Streamable.com API related errors.

    Args:
        message: Error message describing the issue
    """

    def __init__(self, message: str) -> None:
        """Initialize the exception with a message.

        Args:
            message: Error message describing the issue
        """
        super().__init__(message)


class EmailAlreadyInUseError(StreamableError):
    """Raised when attempting to create an account with an email that's already registered."""

    pass


class InvalidCredentialsError(StreamableError):
    """Raised when login credentials are invalid.

    This exception is raised when attempting to authenticate with incorrect
    email/password combination or when the current password is wrong during
    password change operations.
    """

    pass


class InvalidSessionError(StreamableError):
    """Raised when attempting to perform operations without proper authentication.

    This exception is raised when:
    - The client is not authenticated
    - The session has expired
    - No session cookie is found
    """

    pass


class PasswordValidationError(StreamableError):
    """Raised when password validation fails.

    This exception is raised when a password doesn't meet the requirements
    set by Streamable.com (e.g., minimum length, character requirements).
    """

    pass


class InvalidPlayerColorError(StreamableError):
    """Raised when an invalid color format is provided for the video player.

    The color must be a valid hexadecimal color code in the format `#RRGGBB`.

    Args:
        color: The invalid color string that was provided
    """

    def __init__(self, color: str) -> None:
        """Initialize with the invalid color that was provided.

        Args:
            color: The invalid color string that was provided
        """
        super().__init__(
            f"Invalid color syntax: expected hex color code, got '{color}'"
        )


class InvalidPrivacySettingsError(StreamableError):
    """Raised when invalid or no privacy settings are provided."""

    pass


class LabelAlreadyExistsError(StreamableError):
    """Raised when attempting to create a label that already exists.

    Args:
        label_name: The name of the label that already exists
    """

    def __init__(self, label_name: str) -> None:
        """Initialize with the name of the label that already exists.

        Args:
            label_name: The name of the label that already exists
        """
        super().__init__(f"Label '{label_name}' already exists.")


class VideoTooLargeError(StreamableError):
    """Raised when a video file exceeds the maximum allowed file size.

    For free Streamable.com accounts, the maximum file size is 250MB.

    Args:
        video_file: Path to the video file that is too large
        size: Actual size of the file in bytes
        max_size: Maximum allowed size in bytes
    """

    def __init__(self, video_file: Path, size: int, max_size: int) -> None:
        """Initialize with file size information.

        Args:
            video_file: Path to the video file that is too large
            size: Actual size of the file in bytes
            max_size: Maximum allowed size in bytes
        """
        super().__init__(
            f"{video_file} size of {size} bytes exceeds maximum allowed size of {max_size} bytes."
        )


class VideoTooLongError(StreamableError):
    """Raised when a video file exceeds the maximum allowed duration.

    For free Streamable.com accounts, the maximum video duration is 10 minutes.

    Args:
        video_file: Path to the video file that is too long
        length: Actual duration of the video in milliseconds
        max_length: Maximum allowed duration in milliseconds
    """

    def __init__(self, video_file: Path, *, length: int, max_length: int) -> None:
        """Initialize with video duration information.

        Args:
            video_file: Path to the video file that is too long
            length: Actual duration of the video in milliseconds
            max_length: Maximum allowed duration in milliseconds
        """
        super().__init__(
            f"{video_file} length {length}ms exceeds maximum allowed length of {max_length}ms."
        )
