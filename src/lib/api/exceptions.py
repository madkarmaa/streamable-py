class StreamableError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class EmailAlreadyInUseError(StreamableError):
    pass


class InvalidCredentialsError(StreamableError):
    pass


class InvalidSessionError(StreamableError):
    pass


class PasswordValidationError(StreamableError):
    pass
