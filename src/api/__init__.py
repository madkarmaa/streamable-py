from httpx import (
    Client,
    Response,
    get as httpx_get,
    post as httpx_post,
)
from urllib.parse import urljoin, urlencode
from pydantic import ValidationError
from typing import Optional
from pathlib import Path
from .models import *
from .exceptions import *
from ..utils.s3 import build_s3_upload_headers


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

    if response.status_code == 400 and "Email already in use" in response.text:
        raise EmailAlreadyInUseError(response.text)

    return response


def login(session: Client, account_info: AccountInfo) -> Response:
    url: str = AUTH_BASE_URL.path("check").build()
    body: LoginRequest = LoginRequest.from_account_info(account_info)

    response: Response = session.post(url, json=body.model_dump())

    try:
        # API returns 200 OK even for invalid credentials
        # so we need to check the response body for error messages
        response_data: ErrorResponse = ErrorResponse.model_validate(response.json())
        if (
            response_data.error == "AuthError"
            and "Invalid username or password" in response_data.message
        ):
            raise InvalidCredentialsError(response_data.message)
    except ValidationError:
        pass

    return response


def change_password(
    session: Client, *, current_password: str, new_password: str
) -> Response:
    url: str = AUTH_BASE_URL.path("me", "change_password").build()
    session_id: str = str(session.cookies.get("session", ""))

    if not session_id:
        raise InvalidSessionError("No session cookie found. Are you logged in?")

    # there is no API-level check for new and current password equality
    body: ChangePasswordRequest = ChangePasswordRequest(
        current_password=current_password,
        new_password=new_password,
        session=session_id,
    )

    response: Response = session.post(url, json=body.model_dump())

    if response.status_code == 400:
        response_data: ErrorResponse = ErrorResponse.model_validate(response.json())
        if response_data.error == "ValidationError":
            raise PasswordValidationError(response_data.message)

    try:
        # API returns 200 OK even for invalid current password
        # so we need to check the response body for error messages
        response_data = ErrorResponse.model_validate(response.json())
        if response_data.error == "AuthError":
            raise InvalidCredentialsError("Current password is incorrect.")
    except ValidationError:
        pass

    return response


def user_info(session: Optional[Client] = None) -> Response:
    url: str = API_BASE_URL.path("me").build()
    return session.get(url) if session is not None else httpx_get(url)


def change_player_color(session: Client, *, color: str) -> Response:
    url: str = AUTH_BASE_URL.path("me").build()

    try:
        body: ChangePlayerColorRequest = ChangePlayerColorRequest(color=color)
    except ValidationError as e:
        raise InvalidPlayerColorError(color) from e

    return session.put(url, json=body.model_dump())


def change_privacy_settings(
    session: Client,
    *,
    allow_download: Optional[bool] = None,
    allow_sharing: Optional[bool] = None,
    hide_view_count: Optional[bool] = None,
    visibility: Optional[Literal["public", "private"]] = None,
) -> Response:
    if (
        allow_download is None
        and allow_sharing is None
        and hide_view_count is None
        and visibility is None
    ):
        raise InvalidPrivacySettingsError("At least one setting must be provided.")

    url: str = API_BASE_URL.path("me", "settings").build()

    body: ChangePrivacySettingsRequest = ChangePrivacySettingsRequest(
        allow_download=allow_download,
        allow_sharing=allow_sharing,
        hide_view_count=hide_view_count,
        visibility=visibility,
    )

    return session.patch(
        url, json=body.model_dump(exclude_none=True, exclude_unset=True)
    )


def create_label(session: Client, *, name: str) -> Response:
    url: str = API_BASE_URL.path("labels").build()
    body: CreateLabelRequest = CreateLabelRequest(name=name)

    response: Response = session.post(url, json=body.model_dump())

    if response.status_code == 409:
        raise LabelAlreadyExistsError(name)

    return response


def rename_label(session: Client, *, label_id: int, new_name: str) -> Response:
    url: str = API_BASE_URL.path("labels", str(label_id)).build()
    body: RenameLabelRequest = RenameLabelRequest(name=new_name)
    return session.patch(url, json=body.model_dump())


def delete_label(session: Client, *, label_id: int) -> Response:
    url: str = API_BASE_URL.path("labels", str(label_id)).build()
    return session.delete(url)  # there is no API-level check for the label existence


def labels(session: Client) -> Response:
    url: str = API_BASE_URL.path("labels").build()
    return session.get(url)


def shortcode(*, session: Optional[Client] = None, video_file: Path) -> Response:
    url: str = (
        API_BASE_URL.path("uploads", "shortcode")
        .query(size=str(video_file.stat().st_size), version="unknown")
        .build()
    )
    return session.get(url) if session is not None else httpx_get(url)


def initialize_video_upload(
    *,
    session: Optional[Client] = None,
    upload_info: UploadInfo,
    video_file: Path,
    title: Optional[str] = None,
) -> Response:
    url: str = API_BASE_URL.path("videos", upload_info.shortcode, "initialize").build()
    body: InitializeVideoUploadRequest = InitializeVideoUploadRequest(
        original_name=video_file.name,
        original_size=video_file.stat().st_size,
        title=title if title else video_file.stem,
    )
    return (
        session.post(url, json=body.model_dump())
        if session is not None
        else httpx_post(url, json=body.model_dump())
    )


def cancel_video_upload(
    *, session: Optional[Client] = None, shortcode: str
) -> Response:
    url: str = API_BASE_URL.path("videos", shortcode, "cancel").build()
    return session.post(url) if session is not None else httpx_post(url)


def upload_video_file_to_s3(
    *, session: Optional[Client] = None, upload_info: UploadInfo, video_file: Path
) -> Response:
    url: str = f"https://{upload_info.bucket}.s3.amazonaws.com/{upload_info.fields.key}"

    headers: dict[str, str] = build_s3_upload_headers(
        upload_info,
        content_length=video_file.stat().st_size,
        use_current_timestamp=True,
    )

    with video_file.open("rb") as f:
        return (
            session.put(url, content=f, headers=headers)
            if session is not None
            else httpx_post(url, content=f, headers=headers)
        )


def transcode_video_after_upload(
    *,
    session: Optional[Client] = None,
    upload_info: UploadInfo,
) -> Response:
    url: str = API_BASE_URL.path("transcode", upload_info.shortcode).build()
    return (
        session.post(url, json=upload_info.transcoder_options.model_dump())
        if session is not None
        else httpx_post(url, json=upload_info.transcoder_options.model_dump())
    )
