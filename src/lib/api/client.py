from types import TracebackType
from typing import Optional, Type
from httpx import Client, Response
from .exceptions import InvalidSessionError
from . import *
from .models import *


class StreamableClient:
    def __init__(self) -> None:
        self._client: Client = Client()
        self._authenticated: bool = False
        self._account_info: Optional[AccountInfo] = None

    @property
    def is_authenticated(self) -> bool:
        return self._authenticated

    @property
    def unsafe_client(self) -> Client:
        return self._client

    def _ensure_authenticated(self) -> None:
        if (
            not self._authenticated
            or self._account_info is None
            or self._client.is_closed
        ):
            raise InvalidSessionError(
                "Client is not authenticated. Call login() or signup() successfully first."
            )

    def login(self, account_info: AccountInfo) -> StreamableUser:
        self._authenticated = False
        try:
            response: Response = login(self._client, account_info)
            self._authenticated = True
            self._account_info = account_info
            return StreamableUser.model_validate(response.json())
        except:
            self.logout()
            raise

    def signup(self, account_info: AccountInfo) -> StreamableUser:
        self._authenticated = False
        try:
            response: Response = signup(self._client, account_info)
            self._authenticated = True
            self._account_info = account_info
            return StreamableUser.model_validate(response.json())
        except:
            self.logout()
            raise

    def logout(self) -> None:
        self._ensure_authenticated()

        # maybe call an API endpoint to invalidate the session on server side in the future
        # but it's not necessary since login() and signup() will create a new session anyway

        if not self._client.is_closed:
            self._client.close()

        self._authenticated = False
        self._account_info = None

    def get_user_info(self) -> StreamableUser:
        self._ensure_authenticated()
        response: Response = user_info(self._client)
        return StreamableUser.model_validate(response.json())

    @staticmethod
    def get_subscription_plans() -> list[Plan]:
        response: Response = subscription_info()
        return SubscriptionInfo.model_validate(response.json()).availablePlans

    def change_password(self, new_password: str) -> None:
        self._ensure_authenticated()
        assert self._account_info is not None

        change_password(
            self._client,
            current_password=self._account_info.password,
            new_password=new_password,
        )

        self._account_info.password = new_password

    def __enter__(self) -> "StreamableClient":
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        self.logout()
