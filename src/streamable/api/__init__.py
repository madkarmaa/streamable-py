"""Core API functions for Streamable.com communication.

This module contains all the low-level API functions that directly
interact with the Streamable.com endpoints.
"""

from httpx import Client, Response
from urllib.parse import urljoin, urlencode
from pydantic import ValidationError
from typing import Optional
from pathlib import Path
from .models import *
from .exceptions import *
from ..utils.s3 import build_s3_upload_headers


class URLBuilder:
    """Helper class for building URLs with path and query parameters.

    Args:
        base_url: The base URL to build from
        path_parts: Initial path components (optional)
        query_params: Initial query parameters (optional)
    """

    def __init__(
        self,
        base_url: str,
        path_parts: list[str] | None = None,
        query_params: dict[str, str] | None = None,
    ):
        """Initialize the URLBuilder.

        Args:
            base_url: The base URL to build from
            path_parts: Initial path components (optional)
            query_params: Initial query parameters (optional)
        """
        self.base_url: str = base_url.strip().rstrip("/")
        self.path_parts: list[str] = path_parts.copy() if path_parts else []
        self.query_params: dict[str, str] = query_params.copy() if query_params else {}

    def path(self, *parts: str) -> "URLBuilder":
        """Add path components to the URL.

        Args:
            *parts: Path components to add

        Returns:
            A new URLBuilder instance with the added path components
        """
        new_instance: URLBuilder = URLBuilder(
            self.base_url, self.path_parts, self.query_params
        )
        new_instance.path_parts.extend(parts)
        return new_instance

    def query(self, **params: str) -> "URLBuilder":
        """Add query parameters to the URL.

        Args:
            **params: Query parameters as keyword arguments

        Returns:
            A new URLBuilder instance with the added query parameters
        """
        new_instance: URLBuilder = URLBuilder(
            self.base_url, self.path_parts, self.query_params
        )
        new_instance.query_params.update(params)
        return new_instance

    def build(self) -> str:
        """Build the final URL string.

        Returns:
            The complete URL with base, path, and query parameters
        """
        full_path: str = "/".join(part.strip("/") for part in self.path_parts)
        url: str = urljoin(f"{self.base_url}/", full_path)
        if self.query_params:
            url += "?" + urlencode(self.query_params)
        return url

    def __str__(self) -> str:
        """Return the built URL as a string.

        Returns:
            The complete URL string
        """
        return self.build()


AUTH_BASE_URL: URLBuilder = URLBuilder("https://ajax.streamable.com")
API_BASE_URL: URLBuilder = URLBuilder("https://api-f.streamable.com/api/v1")


def signup(session: Client, *, account_info: AccountInfo) -> Response:
    """Create a new Streamable.com account.

    Args:
        session: HTTP client session
        account_info: Account credentials for the new account

    Returns:
        HTTP response from the signup request

    Raises:
        EmailAlreadyInUseError: If the email is already registered
    """
    url: str = AUTH_BASE_URL.path("users").build()
    body: CreateAccountRequest = CreateAccountRequest.from_account_info(account_info)

    response: Response = session.post(url, json=body.model_dump())

    if response.status_code == 400 and "Email already in use" in response.text:
        raise EmailAlreadyInUseError(response.text)

    return response


def login(session: Client, *, account_info: AccountInfo) -> Response:
    """Authenticate with Streamable.com.

    Args:
        session: HTTP client session
        account_info: Account credentials for authentication

    Returns:
        HTTP response from the login request

    Raises:
        InvalidCredentialsError: If the credentials are invalid
    """
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
    """Change the user's password.

    Args:
        session: HTTP client session (must be authenticated)
        current_password: The user's current password
        new_password: The new password to set

    Returns:
        HTTP response from the password change request

    Raises:
        InvalidSessionError: If no session cookie is found
        PasswordValidationError: If password validation fails
        InvalidCredentialsError: If current password is incorrect
    """
    url: str = AUTH_BASE_URL.path("me", "change_password").build()
    session_id: str = str(session.cookies.get("session", ""))

    if not session_id:
        raise InvalidSessionError("No session cookie found. Are you logged in?")

    # there is no API-level check for new and current password equality
    body: ChangePasswordRequest = ChangePasswordRequest(
        current_password=current_password.strip(),
        new_password=new_password.strip(),
        session=session_id.strip(),
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


def user_info(session: Client) -> Response:
    """Get current user information.

    Args:
        session: HTTP client session (must be authenticated)

    Returns:
        HTTP response containing user information
    """
    url: str = API_BASE_URL.path("me").build()
    return session.get(url)


def change_player_color(session: Client, *, color: str) -> Response:
    """Change the user's video player color.

    Args:
        session: HTTP client session (must be authenticated)
        color: Hex color code (e.g., '#FF0080')

    Returns:
        HTTP response from the color change request

    Raises:
        InvalidPlayerColorError: If the color format is invalid
    """
    color = color.strip()
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
    """Change the user's privacy settings.

    Args:
        session: HTTP client session (must be authenticated)
        allow_download: Whether to allow video downloads (optional)
        allow_sharing: Whether to allow video sharing (optional)
        hide_view_count: Whether to hide view counts (optional)
        visibility: Video visibility setting (optional)

    Returns:
        HTTP response from the privacy settings change request

    Raises:
        InvalidPrivacySettingsError: If no settings are provided
    """
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
    """Create a new label.

    Args:
        session: HTTP client session (must be authenticated)
        name: Name of the label to create

    Returns:
        HTTP response from the label creation request

    Raises:
        LabelAlreadyExistsError: If a label with this name already exists
    """
    name = name.strip()
    url: str = API_BASE_URL.path("labels").build()
    body: CreateLabelRequest = CreateLabelRequest(name=name)

    response: Response = session.post(url, json=body.model_dump())

    if response.status_code == 409:
        raise LabelAlreadyExistsError(name)

    return response


def rename_label(session: Client, *, label_id: int, new_name: str) -> Response:
    """Rename an existing label.

    Args:
        session: HTTP client session (must be authenticated)
        label_id: ID of the label to rename
        new_name: New name for the label

    Returns:
        HTTP response from the label rename request
    """
    url: str = API_BASE_URL.path("labels", str(label_id)).build()
    body: RenameLabelRequest = RenameLabelRequest(name=new_name.strip())

    response: Response = session.patch(url, json=body.model_dump())

    if response.status_code == 404:
        raise LabelNotFoundError(label_id)

    return response


def delete_label(session: Client, *, label_id: int) -> Response:
    """Delete a label.

    Args:
        session: HTTP client session (must be authenticated)
        label_id: ID of the label to delete

    Returns:
        HTTP response from the label deletion request

    Note:
        There is no API-level check for label existence
    """
    url: str = API_BASE_URL.path("labels", str(label_id)).build()
    return session.delete(url)  # there is no API-level check for the label existence


def labels(session: Client) -> Response:
    """Get all user labels.

    Args:
        session: HTTP client session (must be authenticated)

    Returns:
        HTTP response containing the list of user labels
    """
    url: str = API_BASE_URL.path("labels").build()
    return session.get(url)


def shortcode(session: Client, *, video_file: Path) -> Response:
    """Generate a shortcode for video upload.

    This is the first step in the video upload process, which generates
    upload credentials and S3 information.

    Args:
        session: HTTP client session
        video_file: Path to the video file to upload

    Returns:
        HTTP response containing upload information
    """
    url: str = (
        API_BASE_URL.path("uploads", "shortcode")
        .query(size=str(video_file.stat().st_size), version="unknown")
        .build()
    )
    return session.get(url)


def initialize_video_upload(
    session: Client,
    *,
    upload_info: UploadInfo,
    video_file: Path,
    title: Optional[str] = None,
) -> Response:
    """Initialize a video upload with metadata.

    This sets up the video record in Streamable's database before
    the actual file upload to S3.

    Args:
        session: HTTP client session
        upload_info: Upload information from shortcode generation
        video_file: Path to the video file to upload
        title: Optional video title (defaults to filename)

    Returns:
        HTTP response from the initialization request
    """
    url: str = API_BASE_URL.path("videos", upload_info.shortcode, "initialize").build()
    body: InitializeVideoUploadRequest = InitializeVideoUploadRequest(
        original_name=video_file.name,
        original_size=video_file.stat().st_size,
        title=title if title else video_file.stem,
    )
    return session.post(url, json=body.model_dump())


def cancel_video_upload(session: Client, *, shortcode: str) -> Response:
    """Cancel a video upload.

    Args:
        session: HTTP client session
        shortcode: Shortcode of the upload to cancel

    Returns:
        HTTP response from the cancellation request
    """
    url: str = API_BASE_URL.path("videos", shortcode, "cancel").build()
    return session.post(url)


def upload_video_file_to_s3(
    session: Client, *, upload_info: UploadInfo, video_file: Path
) -> Response:
    """Upload the video file to AWS S3.

    This performs the actual file upload using the credentials
    and information provided by the shortcode generation.

    Args:
        session: HTTP client session
        upload_info: Upload information from shortcode generation
        video_file: Path to the video file to upload

    Returns:
        HTTP response from the S3 upload
    """
    url: str = f"https://{upload_info.bucket}.s3.amazonaws.com/{upload_info.fields.key}"

    headers: dict[str, str] = build_s3_upload_headers(
        upload_info,
        content_length=video_file.stat().st_size,
        use_current_timestamp=True,
    )

    with video_file.open("rb") as f:
        return session.put(url, content=f, headers=headers)


def transcode_video_after_upload(
    session: Client, *, upload_info: UploadInfo
) -> Response:
    """Start video transcoding after upload.

    This is the final step in the upload process, which triggers
    the video processing and will make the video available for playback.

    Args:
        session: HTTP client session
        upload_info: Upload information from shortcode generation

    Returns:
        HTTP response containing the processed video information
    """
    url: str = API_BASE_URL.path("transcode", upload_info.shortcode).build()
    return session.post(url, json=upload_info.transcoder_options.model_dump())
