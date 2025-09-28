from types import TracebackType
from typing import Optional, Type
from httpx import Client, Response
from . import login, signup
from .models import AccountInfo


class StreamableClient:
    _client: Optional[Client] = None
    _authenticated: bool = False

    @property
    def is_authenticated(self) -> bool:
        return self._authenticated

    def _reset_state(self) -> None:
        self._client = None
        self._authenticated = False

    def _get_or_create_client(self) -> Client:
        if self._client is None or self._client.is_closed:
            self._client = Client()
        return self._client

    def _ensure_authenticated(self) -> None:
        if not self._authenticated or self._client is None or self._client.is_closed:
            raise RuntimeError(
                "Client is not authenticated. Call login() or signup() successfully first."
            )

    def close(self) -> None:
        if self._client is not None and not self._client.is_closed:
            self._client.close()
        self._reset_state()

    def login(self, account_info: AccountInfo) -> Response:
        self._reset_state()
        client: Client = self._get_or_create_client()

        try:
            response: Response = login(client, account_info)
            self._authenticated = True
            return response
        except:
            self.close()
            raise

    def signup(self, account_info: AccountInfo) -> Response:
        self._reset_state()
        client: Client = self._get_or_create_client()

        try:
            response: Response = signup(client, account_info)
            self._authenticated = True
            return response
        except:
            self.close()
            raise

    def __enter__(self) -> "StreamableClient":
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        self.close()
