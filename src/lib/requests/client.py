from contextlib import contextmanager
from typing import Any, Generator
from httpx import Client
from . import login, signup
from .models import AccountInfo


def create_authenticated_client(
    account_info: AccountInfo,
    *,
    create_account: bool = False,
    **client_kwargs: Any,
) -> Client:
    client: Client = Client(**client_kwargs)

    try:
        if create_account:
            signup(client, account_info).raise_for_status()
        else:
            login(client, account_info).raise_for_status()
    except Exception:
        client.close()
        raise

    return client


@contextmanager
def authenticated_client(
    account_info: AccountInfo,
    *,
    create_account: bool = False,
    **client_kwargs: Any,
) -> Generator[Client, None, None]:
    client: Client = create_authenticated_client(
        account_info,
        create_account=create_account,
        **client_kwargs,
    )
    try:
        yield client
    finally:
        client.close()
