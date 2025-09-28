from types import TracebackType
from typing import Optional, Type, overload, Literal
from httpx import Client, Response
from . import *
from .models import *


class StreamableClient:
    def __init__(self) -> None:
        self._client: Client = Client()
        self._authenticated: bool = False

    @property
    def is_authenticated(self) -> bool:
        return self._authenticated

    @property
    def unsafe_client(self) -> Client:
        return self._client

    def _ensure_authenticated(self) -> None:
        if not self._authenticated or self._client.is_closed:
            raise RuntimeError(
                "Client is not authenticated. Call login() or signup() successfully first."
            )

    def close(self) -> None:
        if not self._client.is_closed:
            self._client.close()
        self._authenticated = False

    def login(self, account_info: AccountInfo) -> Response:
        self._authenticated = False
        try:
            response: Response = login(self._client, account_info)
            self._authenticated = True
            return response
        except:
            self.close()
            raise

    def signup(self, account_info: AccountInfo) -> Response:
        self._authenticated = False
        try:
            response: Response = signup(self._client, account_info)
            self._authenticated = True
            return response
        except:
            self.close()
            raise

    @overload
    def get_user_info(self, *, authenticated: Literal[True]) -> StreamableUser: ...

    @overload
    def get_user_info(
        self, *, authenticated: Literal[False]
    ) -> StreamableUnauthenticatedUser: ...

    def get_user_info(
        self, *, authenticated: bool
    ) -> StreamableUser | StreamableUnauthenticatedUser:
        if authenticated:
            self._ensure_authenticated()

        response: Response = user_info(self._client, authenticated=authenticated)

        if authenticated:
            return StreamableUser.model_validate(response.json())

        return StreamableUnauthenticatedUser.model_validate(response.json())

    def get_subscription_plans(self, *, authenticated: bool = False) -> list[Plan]:
        if authenticated:
            self._ensure_authenticated()

        response: Response = subscription_info(
            self._client, authenticated=authenticated
        )
        return SubscriptionInfo.model_validate(response.json()).availablePlans

    def __enter__(self) -> "StreamableClient":
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        self.close()
