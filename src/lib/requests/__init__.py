from httpx import Client, Response
from urllib.parse import urljoin, urlencode
from .models import *


class URLBuilder:
    def __init__(
        self,
        base_url: str,
        path_parts: list[str] | None = None,
        query_params: dict[str, str] | None = None,
    ):
        self.base_url: str = base_url.rstrip("/")
        self.path_parts: list[str] = path_parts.copy() if path_parts else []
        self.query_params: dict[str, str] = query_params.copy() if query_params else {}

    def path(self, *parts: str) -> "URLBuilder":
        new_instance: URLBuilder = URLBuilder(
            self.base_url, self.path_parts, self.query_params
        )
        new_instance.path_parts.extend(parts)
        return new_instance

    def query(self, **params: str) -> "URLBuilder":
        new_instance: URLBuilder = URLBuilder(
            self.base_url, self.path_parts, self.query_params
        )
        new_instance.query_params.update(params)
        return new_instance

    def build(self) -> str:
        full_path: str = "/".join(part.strip("/") for part in self.path_parts)
        url: str = urljoin(f"{self.base_url}/", full_path)
        if self.query_params:
            url += "?" + urlencode(self.query_params)
        return url

    def __str__(self) -> str:
        return self.build()


AUTH_BASE_URL: URLBuilder = URLBuilder("https://ajax.streamable.com")
API_BASE_URL: URLBuilder = URLBuilder("https://api-f.streamable.com/api/v1")


def signup(session: Client, account_info: AccountInfo) -> Response:
    url: str = AUTH_BASE_URL.path("users").build()
    body: CreateAccountRequest = CreateAccountRequest.from_account_info(account_info)

    response: Response = session.post(url, json=body.model_dump())
    return response


def login(session: Client, account_info: AccountInfo) -> Response:
    url: str = AUTH_BASE_URL.path("check").build()
    body: LoginRequest = LoginRequest.from_account_info(account_info)

    response: Response = session.post(url, json=body.model_dump())
    return response
