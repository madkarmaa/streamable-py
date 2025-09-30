from pathlib import Path


class StreamableError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class EmailAlreadyInUseError(StreamableError):
    pass


class InvalidCredentialsError(StreamableError):
    pass


class InvalidSessionError(StreamableError):
    pass


class PasswordValidationError(StreamableError):
    pass


class InvalidPlayerColorError(StreamableError):
    def __init__(self, color: str) -> None:
        super().__init__(
            f"Invalid color syntax: expected hex color code, got '{color}'"
        )


class InvalidPrivacySettingsError(StreamableError):
    pass


class LabelAlreadyExistsError(StreamableError):
    def __init__(self, label_name: str) -> None:
        super().__init__(f"Label '{label_name}' already exists.")


class VideoTooLargeError(StreamableError):
    def __init__(self, video_file: Path, size: int, max_size: int) -> None:
        super().__init__(
            f"{video_file} size {size} exceeds maximum allowed size of {max_size}."
        )


class VideoTooLongError(StreamableError):
    def __init__(self, video_file: Path, *, length: int, max_length: int) -> None:
        super().__init__(
            f"{video_file} length {length}ms exceeds maximum allowed length of {max_length}ms."
        )
