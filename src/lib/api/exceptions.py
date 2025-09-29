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
