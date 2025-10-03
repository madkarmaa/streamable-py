"""High-level client for Streamable.com API operations.

This module provides the main StreamableClient class which offers a
convenient interface for all Streamable.com operations including
authentication, video uploads, and account management.
"""

from types import TracebackType
from typing import Optional, Type, Union, overload, Literal
from httpx import Client, Response
from pathlib import Path
from .exceptions import InvalidSessionError
from . import (
    login,
    signup,
    user_info,
    change_password,
    change_player_color,
    change_privacy_settings,
    create_label,
    rename_label,
    delete_label,
    labels,
    shortcode,
    initialize_video_upload,
    upload_video_file_to_s3,
    transcode_video_after_upload,
)
from .models import (
    AccountInfo,
    StreamableUser,
    Label,
    UserLabel,
    Video,
    UploadInfo,
    PrivacySettings,
    UserLabels,
)
from .exceptions import InvalidSessionError
from ..utils import ensure_is_not_more_than_10_minutes, ensure_is_not_more_than_250mb


class StreamableClient:
    """High-level client for Streamable.com API operations.

    This class provides a convenient interface for interacting with Streamable.com,
    including authentication, video uploads, account management, and label operations.
    It handles session management and provides type-safe methods for all operations.

    The client supports context manager usage.

    Authentication:
        Only email + password authentication is supported by this client.
        Google and Facebook login methods are not available.

    Example:
        ```python
        from streamable import StreamableClient, AccountInfo
        from pathlib import Path

        with StreamableClient() as client:
            account_info = AccountInfo(email="user@example.com", password="password123")
            client.login(account_info)
            video = client.upload_video(Path("video.mp4"))
            print(f"Uploaded: {video.url}")
        ```

    Attributes:
        is_authenticated: Whether the client is currently authenticated
        unsafe_httpx_client: Direct access to the underlying HTTP client (use with caution)
    """

    def __init__(self) -> None:
        """Initialize a new StreamableClient instance."""
        self._client: Client = Client()
        self._authenticated: bool = False
        self._account_info: Optional[AccountInfo] = None

    @property
    def is_authenticated(self) -> bool:
        """Check if the client is currently authenticated.

        Returns:
            True if the client has valid authentication, False otherwise
        """
        return self._authenticated

    @property
    def unsafe_httpx_client(self) -> Client:
        """Get direct access to the underlying HTTP client.

        Warning:
            This provides direct access to the HTTPX client. Use with caution
            as improper use may affect authentication or session state.

        Returns:
            The underlying HTTPX Client instance
        """
        return self._client

    def _ensure_authenticated(self) -> None:
        """Ensure the client is properly authenticated.

        Raises:
            InvalidSessionError: If the client is not authenticated or session is invalid
        """
        if (
            not self._authenticated
            or self._account_info is None
            or self._client.is_closed
        ):
            raise InvalidSessionError(
                "Client is not authenticated. Call login() or signup() successfully first."
            )

    def login(self, account_info: AccountInfo) -> StreamableUser:
        """Authenticate with Streamable.com using email + password credentials.

        Args:
            account_info: Account credentials for authentication (email + password only)

        Returns:
            User information for the authenticated account

        Raises:
            InvalidCredentialsError: If the credentials are invalid

        Note:
            This will close any existing session before creating a new one.
            Only email + password authentication is supported - Google and Facebook
            login methods are not available.
        """
        self._authenticated = False
        try:
            response: Response = login(self._client, account_info=account_info)
            self._authenticated = True
            self._account_info = account_info
            return StreamableUser.model_validate(response.json())
        except:
            self.logout()
            raise

    def signup(self, account_info: AccountInfo) -> StreamableUser:
        """Create a new Streamable.com account and authenticate.

        Args:
            account_info: Account credentials for the new account (email + password only)

        Returns:
            User information for the newly created account

        Raises:
            EmailAlreadyInUseError: If the email is already registered

        Note:
            This will close any existing session before creating a new one.
            Only email + password registration is supported - Google and Facebook
            signup methods are not available.
        """
        self._authenticated = False
        try:
            response: Response = signup(self._client, account_info=account_info)
            self._authenticated = True
            self._account_info = account_info
            return StreamableUser.model_validate(response.json())
        except:
            self.logout()
            raise

    def logout(self) -> None:
        """Log out and close the current session.

        This closes the HTTP client and resets the authentication state.
        After logout, you'll need to call login() or signup() again to
        perform authenticated operations.
        """
        # maybe call an API endpoint to invalidate the session on server side in the future
        # but it's not necessary since login() and signup() will create a new session anyway

        if not self._client.is_closed:
            self._client.close()

        self._authenticated = False
        self._account_info = None
        self._client = Client()

    def get_user_info(self) -> StreamableUser:
        """Get current user information.

        Returns:
            Current user information

        Raises:
            InvalidSessionError: If not authenticated
        """
        self._ensure_authenticated()
        response: Response = user_info(self._client)
        return StreamableUser.model_validate(response.json())

    def change_password(self, new_password: str) -> None:
        """Change the user's password.

        Args:
            new_password: The new password to set

        Raises:
            InvalidSessionError: If not authenticated
            PasswordValidationError: If password validation fails
            InvalidCredentialsError: If current password is incorrect

        Note:
            The client's stored account info is automatically updated with the new password.
        """
        self._ensure_authenticated()
        assert self._account_info is not None

        change_password(
            self._client,
            current_password=self._account_info.password,
            new_password=new_password,
        )

        self._account_info.password = new_password

    def change_player_color(self, color: str) -> None:
        """Change the video player color theme.

        Sets the color theme for the video player interface. The color must be
        a valid hexadecimal color code in #RRGGBB format.

        Args:
            color: Hex color code in #RRGGBB format (e.g., '#FF0080')

        Raises:
            InvalidSessionError: If not authenticated
            InvalidPlayerColorError: If the color format is invalid
        """
        self._ensure_authenticated()
        change_player_color(self._client, color=color)

    def change_privacy_settings(
        self,
        *,
        allow_download: Optional[bool] = None,
        allow_sharing: Optional[bool] = None,
        hide_view_count: Optional[bool] = None,
        visibility: Optional[Literal["public", "private"]] = None,
    ) -> PrivacySettings:
        """Change privacy settings for videos.

        Args:
            allow_download: Whether to allow video downloads (optional)
            allow_sharing: Whether to allow video sharing (optional)
            hide_view_count: Whether to hide view counts (optional)
            visibility: Video visibility setting (optional)

        Returns:
            Updated privacy settings

        Raises:
            InvalidSessionError: If not authenticated
            InvalidPrivacySettingsError: If no settings are provided
        """
        self._ensure_authenticated()

        response: Response = change_privacy_settings(
            self._client,
            allow_download=allow_download,
            allow_sharing=allow_sharing,
            hide_view_count=hide_view_count,
            visibility=visibility,
        )

        return StreamableUser.model_validate(response.json()).privacy_settings

    def create_label(self, name: str) -> Label:
        """Create a new label.

        Args:
            name: Name of the label to create

        Returns:
            The created label

        Raises:
            InvalidSessionError: If not authenticated
            LabelAlreadyExistsError: If a label with this name already exists
        """
        self._ensure_authenticated()
        response: Response = create_label(self._client, name=name)
        return Label.model_validate(response.json())

    @overload
    def rename_label(self, label: int, new_name: str) -> Label: ...
    @overload
    def rename_label(self, label: Label, new_name: str) -> Label: ...
    def rename_label(self, label: Union[int, Label], new_name: str) -> Label:
        """Rename an existing label.

        Args:
            label: Label ID or Label instance to rename
            new_name: New name for the label

        Returns:
            The updated label

        Raises:
            InvalidSessionError: If not authenticated
        """
        self._ensure_authenticated()

        if isinstance(label, Label):
            label_id: int = label.id
        else:
            label_id: int = label

        response: Response = rename_label(
            self._client, label_id=label_id, new_name=new_name
        )
        return Label.model_validate(response.json())

    @overload
    def delete_label(self, label: int) -> None: ...
    @overload
    def delete_label(self, label: Label) -> None: ...
    def delete_label(self, label: Union[int, Label]) -> None:
        """Delete a label.

        Args:
            label: Label ID or Label instance to delete

        Raises:
            InvalidSessionError: If not authenticated

        Note:
            No error is raised if the label doesn't exist.
        """
        self._ensure_authenticated()

        if isinstance(label, Label):
            label_id: int = label.id
        else:
            label_id: int = label

        delete_label(self._client, label_id=label_id)

    def get_user_labels(self) -> list[UserLabel]:
        """Get all user labels.

        Returns:
            List of user labels with usage counts

        Raises:
            InvalidSessionError: If not authenticated
        """
        self._ensure_authenticated()
        response: Response = labels(self._client)
        return UserLabels.model_validate(response.json()).userLabels

    def get_label_by_name(self, name: str) -> Optional[UserLabel]:
        """Find a label by name.

        Args:
            name: Name of the label to find

        Returns:
            The label if found, None otherwise

        Raises:
            InvalidSessionError: If not authenticated
        """
        labels: list[UserLabel] = self.get_user_labels()
        for label in labels:
            if label.name == name:
                return label
        return None

    def upload_video(self, video_file: Path) -> Video:
        """Upload a video file to Streamable.com.

        This method handles the complete upload process:
        1. Validates file size and duration
        2. Generates upload credentials
        3. Initializes the video record
        4. Uploads the file to S3
        5. Triggers transcoding

        Args:
            video_file: Path to the video file to upload

        Returns:
            Information about the uploaded video

        Raises:
            InvalidSessionError: If not authenticated
            VideoTooLargeError: If file exceeds 250MB limit
            VideoTooLongError: If video exceeds 10 minute limit
            ValueError: If the file doesn't exist or is not a valid video

        Note:
            Free account limits: Maximum 250MB file size and 10 minute duration.
            The method automatically validates these constraints before upload.
        """
        video_file = video_file.resolve()

        ensure_is_not_more_than_250mb(video_file)
        ensure_is_not_more_than_10_minutes(video_file)

        shortcode_response: Response = shortcode(
            session=self._client, video_file=video_file
        )

        upload_info: UploadInfo = UploadInfo.model_validate(shortcode_response.json())

        initialize_video_upload(
            session=self._client, upload_info=upload_info, video_file=video_file
        )

        upload_video_file_to_s3(
            session=self._client, upload_info=upload_info, video_file=video_file
        )

        transcoding_response: Response = transcode_video_after_upload(
            session=self._client, upload_info=upload_info
        )

        return Video.model_validate(transcoding_response.json())

    def __enter__(self) -> "StreamableClient":
        """Enter the context manager.

        Returns:
            The client instance for use in the with statement
        """
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """Exit the context manager and clean up resources.

        Automatically calls logout() to close the session and HTTP client.

        Args:
            exc_type: Exception type (if any)
            exc_val: Exception value (if any)
            exc_tb: Exception traceback (if any)
        """
        self.logout()
