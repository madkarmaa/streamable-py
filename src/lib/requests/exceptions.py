from httpx import Response


class StreamableError(Exception):
    def __init__(self, message: str, response: Response):
        self.message: str = message
        self.response: Response = response
        super().__init__(message)


class EmailAlreadyInUseError(StreamableError):
    pass


class InvalidCredentialsError(StreamableError):
    pass
