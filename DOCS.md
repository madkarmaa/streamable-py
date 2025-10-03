<a id="streamable"></a>

# streamable

Unofficial Python wrapper for the undocumented API of <a href="https://streamable.com">streamable.com</a>.

This package provides a comprehensive Python interface for interacting with
the undocumented Streamable.com API, enabling video uploads, account management,
and various other operations.

Authentication:
    This library supports email + password authentication only.
    Google and Facebook login methods are not supported.

Limitations:
    - Free account limits: 250MB file size, 10 minute duration per video

<a id="streamable.api.exceptions"></a>

# streamable.api.exceptions

Custom exceptions for the Streamable.com API client.

This module defines all custom exception classes used throughout the library
to handle various error conditions when interacting with the Streamable.com API.

<a id="streamable.api.exceptions.StreamableError"></a>

## StreamableError Objects

```python
class StreamableError(Exception)
```

Base exception class for all Streamable.com API related errors.

**Arguments**:

- `message` - Error message describing the issue

<a id="streamable.api.exceptions.StreamableError.__init__"></a>

#### \_\_init\_\_

```python
def __init__(message: str) -> None
```

Initialize the exception with a message.

**Arguments**:

- `message` - Error message describing the issue

<a id="streamable.api.exceptions.EmailAlreadyInUseError"></a>

## EmailAlreadyInUseError Objects

```python
class EmailAlreadyInUseError(StreamableError)
```

Raised when attempting to create an account with an email that's already registered.

<a id="streamable.api.exceptions.InvalidCredentialsError"></a>

## InvalidCredentialsError Objects

```python
class InvalidCredentialsError(StreamableError)
```

Raised when login credentials are invalid.

This exception is raised when attempting to authenticate with incorrect
email/password combination or when the current password is wrong during
password change operations.

<a id="streamable.api.exceptions.InvalidSessionError"></a>

## InvalidSessionError Objects

```python
class InvalidSessionError(StreamableError)
```

Raised when attempting to perform operations without proper authentication.

This exception is raised when:
- The client is not authenticated
- The session has expired
- No session cookie is found

<a id="streamable.api.exceptions.PasswordValidationError"></a>

## PasswordValidationError Objects

```python
class PasswordValidationError(StreamableError)
```

Raised when password validation fails.

This exception is raised when a password doesn't meet the requirements
set by Streamable.com (e.g., minimum length, character requirements).

<a id="streamable.api.exceptions.InvalidPlayerColorError"></a>

## InvalidPlayerColorError Objects

```python
class InvalidPlayerColorError(StreamableError)
```

Raised when an invalid color format is provided for the video player.

The color must be a valid hexadecimal color code in the format ``RRGGBB``.

**Arguments**:

- `color` - The invalid color string that was provided

<a id="streamable.api.exceptions.InvalidPlayerColorError.__init__"></a>

#### \_\_init\_\_

```python
def __init__(color: str) -> None
```

Initialize with the invalid color that was provided.

**Arguments**:

- `color` - The invalid color string that was provided

<a id="streamable.api.exceptions.InvalidPrivacySettingsError"></a>

## InvalidPrivacySettingsError Objects

```python
class InvalidPrivacySettingsError(StreamableError)
```

Raised when invalid or no privacy settings are provided.

<a id="streamable.api.exceptions.LabelAlreadyExistsError"></a>

## LabelAlreadyExistsError Objects

```python
class LabelAlreadyExistsError(StreamableError)
```

Raised when attempting to create a label that already exists.

**Arguments**:

- `label_name` - The name of the label that already exists

<a id="streamable.api.exceptions.LabelAlreadyExistsError.__init__"></a>

#### \_\_init\_\_

```python
def __init__(label_name: str) -> None
```

Initialize with the name of the label that already exists.

**Arguments**:

- `label_name` - The name of the label that already exists

<a id="streamable.api.exceptions.LabelNotFoundError"></a>

## LabelNotFoundError Objects

```python
class LabelNotFoundError(StreamableError)
```

Raised when a specified label is not found.

**Arguments**:

- `label_name` - The name of the label that was not found

<a id="streamable.api.exceptions.LabelNotFoundError.__init__"></a>

#### \_\_init\_\_

```python
def __init__(label_id: int) -> None
```

Initialize with the ID of the label that was not found.

**Arguments**:

- `label_id` - The ID of the label that was not found

<a id="streamable.api.exceptions.VideoTooLargeError"></a>

## VideoTooLargeError Objects

```python
class VideoTooLargeError(StreamableError)
```

Raised when a video file exceeds the maximum allowed file size.

For free Streamable.com accounts, the maximum file size is 250MB.

**Arguments**:

- `video_file` - Path to the video file that is too large
- `size` - Actual size of the file in bytes
- `max_size` - Maximum allowed size in bytes

<a id="streamable.api.exceptions.VideoTooLargeError.__init__"></a>

#### \_\_init\_\_

```python
def __init__(video_file: Path, size: int, max_size: int) -> None
```

Initialize with file size information.

**Arguments**:

- `video_file` - Path to the video file that is too large
- `size` - Actual size of the file in bytes
- `max_size` - Maximum allowed size in bytes

<a id="streamable.api.exceptions.VideoTooLongError"></a>

## VideoTooLongError Objects

```python
class VideoTooLongError(StreamableError)
```

Raised when a video file exceeds the maximum allowed duration.

For free Streamable.com accounts, the maximum video duration is 10 minutes.

**Arguments**:

- `video_file` - Path to the video file that is too long
- `length` - Actual duration of the video in milliseconds
- `max_length` - Maximum allowed duration in milliseconds

<a id="streamable.api.exceptions.VideoTooLongError.__init__"></a>

#### \_\_init\_\_

```python
def __init__(video_file: Path, *, length: int, max_length: int) -> None
```

Initialize with video duration information.

**Arguments**:

- `video_file` - Path to the video file that is too long
- `length` - Actual duration of the video in milliseconds
- `max_length` - Maximum allowed duration in milliseconds

<a id="streamable.api.client"></a>

# streamable.api.client

High-level client for Streamable.com API operations.

This module provides the main StreamableClient class which offers a
convenient interface for all Streamable.com operations including
authentication, video uploads, and account management.

<a id="streamable.api.client.StreamableClient"></a>

## StreamableClient Objects

```python
class StreamableClient()
```

High-level client for Streamable.com API operations.

This class provides a convenient interface for interacting with Streamable.com.

Supports context manager usage.

Authentication:
Only email + password authentication is supported by this client.
Google and Facebook login methods are not available.

**Example**:

    ```python
    from streamable import StreamableClient, AccountInfo
    from pathlib import Path

    with StreamableClient() as client:
        account_info = AccountInfo(email="user@example.com", password="password123")
        client.login(account_info)
        video = client.upload_video(Path("video.mp4"))
        print(f"Uploaded: {video.url}")
    ```
  

**Attributes**:

- `is_authenticated` - Whether the client is currently authenticated
- `unsafe_httpx_client` - Direct access to the underlying HTTP client (use with caution)

<a id="streamable.api.client.StreamableClient.__init__"></a>

#### \_\_init\_\_

```python
def __init__() -> None
```

Initialize a new StreamableClient instance.

<a id="streamable.api.client.StreamableClient.is_authenticated"></a>

#### is\_authenticated

```python
@property
def is_authenticated() -> bool
```

Check if the client is currently authenticated.

**Returns**:

  True if the client has valid authentication, False otherwise

<a id="streamable.api.client.StreamableClient.unsafe_httpx_client"></a>

#### unsafe\_httpx\_client

```python
@property
def unsafe_httpx_client() -> Client
```

Get direct access to the underlying HTTP client.

**Warnings**:

  This provides direct access to the HTTPX client. Use with caution
  as improper use may affect authentication or session state.
  

**Returns**:

  The underlying HTTPX Client instance

<a id="streamable.api.client.StreamableClient.signup"></a>

#### signup

```python
def signup(account_info: AccountInfo) -> StreamableUser
```

Create a new Streamable.com account and authenticate.

**Arguments**:

- `account_info` - Account credentials for the new account (email + password only)
  

**Returns**:

  User information for the newly created account
  

**Raises**:

- `EmailAlreadyInUseError` - If the email is already registered
  

**Notes**:

  This will close any existing session before creating a new one.
  Only email + password registration is supported - Google and Facebook
  signup methods are not available.

<a id="streamable.api.client.StreamableClient.login"></a>

#### login

```python
def login(account_info: AccountInfo) -> StreamableUser
```

Authenticate with Streamable.com using email + password credentials.

**Arguments**:

- `account_info` - Account credentials for authentication (email + password only)
  

**Returns**:

  User information for the authenticated account
  

**Raises**:

- `InvalidCredentialsError` - If the credentials are invalid
  

**Notes**:

  This will close any existing session before creating a new one.
  Only email + password authentication is supported - Google and Facebook
  login methods are not available.

<a id="streamable.api.client.StreamableClient.logout"></a>

#### logout

```python
def logout() -> None
```

Log out and close the current session.

This closes the HTTP client and resets the authentication state.
After logout, you'll need to call login() or signup() again to
perform authenticated operations.

<a id="streamable.api.client.StreamableClient.get_user_info"></a>

#### get\_user\_info

```python
def get_user_info() -> StreamableUser
```

Get the current user information.

**Returns**:

  Current user information
  

**Raises**:

- `InvalidSessionError` - If not authenticated

<a id="streamable.api.client.StreamableClient.change_password"></a>

#### change\_password

```python
def change_password(new_password: str) -> None
```

Change the user's password.

**Arguments**:

- `new_password` - The new password to set
  

**Raises**:

- `InvalidSessionError` - If not authenticated
- `PasswordValidationError` - If password validation fails
- `InvalidCredentialsError` - If current password is incorrect
  

**Notes**:

  The client's stored account info is automatically updated with the new password.

<a id="streamable.api.client.StreamableClient.change_player_color"></a>

#### change\_player\_color

```python
def change_player_color(color: str) -> None
```

Change the video player color theme.

Sets the color theme for the video player interface. The color must be
a valid hexadecimal color code in `RRGGBB` format.

**Arguments**:

- `color` - Hex color code in `RRGGBB` format (e.g., '`FF0080`')
  

**Raises**:

- `InvalidSessionError` - If not authenticated
- `InvalidPlayerColorError` - If the color format is invalid

<a id="streamable.api.client.StreamableClient.change_privacy_settings"></a>

#### change\_privacy\_settings

```python
def change_privacy_settings(
    *,
    allow_download: Optional[bool] = None,
    allow_sharing: Optional[bool] = None,
    hide_view_count: Optional[bool] = None,
    visibility: Optional[Literal["public",
                                 "private"]] = None) -> PrivacySettings
```

Change privacy settings for videos.

**Arguments**:

- `allow_download` - Whether to allow video downloads (optional)
- `allow_sharing` - Whether to allow video sharing (optional)
- `hide_view_count` - Whether to hide view counts (optional)
- `visibility` - Video visibility setting (optional)
  

**Returns**:

  Updated privacy settings
  

**Raises**:

- `InvalidSessionError` - If not authenticated
- `InvalidPrivacySettingsError` - If no settings are provided

<a id="streamable.api.client.StreamableClient.create_label"></a>

#### create\_label

```python
def create_label(name: str) -> Label
```

Create a new label.

**Arguments**:

- `name` - Name of the label to create
  

**Returns**:

  The created label
  

**Raises**:

- `InvalidSessionError` - If not authenticated
- `LabelAlreadyExistsError` - If a label with this name already exists

<a id="streamable.api.client.StreamableClient.rename_label"></a>

#### rename\_label

```python
def rename_label(label: Union[int, Label], new_name: str) -> Label
```

Rename an existing label.

**Arguments**:

- `label` - Label ID or Label instance to rename
- `new_name` - New name for the label
  

**Returns**:

  The updated label
  

**Raises**:

- `InvalidSessionError` - If not authenticated

<a id="streamable.api.client.StreamableClient.delete_label"></a>

#### delete\_label

```python
def delete_label(label: Union[int, Label]) -> None
```

Delete a label.

**Arguments**:

- `label` - Label ID or Label instance to delete
  

**Raises**:

- `InvalidSessionError` - If not authenticated
  

**Notes**:

  No error is raised if the label doesn't exist.

<a id="streamable.api.client.StreamableClient.get_user_labels"></a>

#### get\_user\_labels

```python
def get_user_labels() -> list[UserLabel]
```

Get all user labels.

**Returns**:

  List of user labels with usage counts
  

**Raises**:

- `InvalidSessionError` - If not authenticated

<a id="streamable.api.client.StreamableClient.get_label_by_name"></a>

#### get\_label\_by\_name

```python
def get_label_by_name(name: str) -> Optional[UserLabel]
```

Find a label by name.

**Arguments**:

- `name` - Name of the label to find
  

**Returns**:

  The label if found, None otherwise
  

**Raises**:

- `InvalidSessionError` - If not authenticated

<a id="streamable.api.client.StreamableClient.upload_video"></a>

#### upload\_video

```python
def upload_video(video_file: Path) -> Video
```

Upload a video file to Streamable.com.

**Arguments**:

- `video_file` - Path to the video file to upload
  

**Returns**:

  Information about the uploaded video
  

**Raises**:

- `InvalidSessionError` - If not authenticated
- `VideoTooLargeError` - If file exceeds 250MB limit
- `VideoTooLongError` - If video exceeds 10 minute limit
- `ValueError` - If the file doesn't exist or is not a valid video
  

**Notes**:

  Free account limits: Maximum 250MB file size and 10 minute duration.
  The method automatically validates these constraints before upload.

<a id="streamable.api.client.StreamableClient.__enter__"></a>

#### \_\_enter\_\_

```python
def __enter__() -> "StreamableClient"
```

Enter the context manager.

**Returns**:

  The client instance for use in the with statement

<a id="streamable.api.client.StreamableClient.__exit__"></a>

#### \_\_exit\_\_

```python
def __exit__(exc_type: Optional[Type[BaseException]],
             exc_val: Optional[BaseException],
             exc_tb: Optional[TracebackType]) -> None
```

Exit the context manager and clean up resources.

Automatically calls logout() to close the session and HTTP client.

**Arguments**:

- `exc_type` - Exception type (if any)
- `exc_val` - Exception value (if any)
- `exc_tb` - Exception traceback (if any)

<a id="streamable.api"></a>

# streamable.api

Core API functions for Streamable.com communication.

This module contains all the low-level API functions that directly
interact with the Streamable.com endpoints.

<a id="streamable.api.URLBuilder"></a>

## URLBuilder Objects

```python
class URLBuilder()
```

Helper class for building URLs with path and query parameters.

**Arguments**:

- `base_url` - The base URL to build from
- `path_parts` - Initial path components (optional)
- `query_params` - Initial query parameters (optional)

<a id="streamable.api.URLBuilder.__init__"></a>

#### \_\_init\_\_

```python
def __init__(base_url: str,
             path_parts: list[str] | None = None,
             query_params: dict[str, str] | None = None)
```

Initialize the URLBuilder.

**Arguments**:

- `base_url` - The base URL to build from
- `path_parts` - Initial path components (optional)
- `query_params` - Initial query parameters (optional)

<a id="streamable.api.URLBuilder.path"></a>

#### path

```python
def path(*parts: str) -> "URLBuilder"
```

Add path components to the URL.

**Arguments**:

- `*parts` - Path components to add
  

**Returns**:

  A new URLBuilder instance with the added path components

<a id="streamable.api.URLBuilder.query"></a>

#### query

```python
def query(**params: str) -> "URLBuilder"
```

Add query parameters to the URL.

**Arguments**:

- `**params` - Query parameters as keyword arguments
  

**Returns**:

  A new URLBuilder instance with the added query parameters

<a id="streamable.api.URLBuilder.build"></a>

#### build

```python
def build() -> str
```

Build the final URL string.

**Returns**:

  The complete URL with base, path, and query parameters

<a id="streamable.api.URLBuilder.__str__"></a>

#### \_\_str\_\_

```python
def __str__() -> str
```

Return the built URL as a string.

**Returns**:

  The complete URL string

<a id="streamable.api.signup"></a>

#### signup

```python
def signup(session: Client, *, account_info: AccountInfo) -> Response
```

Create a new Streamable.com account.

**Arguments**:

- `session` - HTTP client session
- `account_info` - Account credentials for the new account
  

**Returns**:

  HTTP response from the signup request
  

**Raises**:

- `EmailAlreadyInUseError` - If the email is already registered

<a id="streamable.api.login"></a>

#### login

```python
def login(session: Client, *, account_info: AccountInfo) -> Response
```

Authenticate with Streamable.com.

**Arguments**:

- `session` - HTTP client session
- `account_info` - Account credentials for authentication
  

**Returns**:

  HTTP response from the login request
  

**Raises**:

- `InvalidCredentialsError` - If the credentials are invalid

<a id="streamable.api.change_password"></a>

#### change\_password

```python
def change_password(session: Client, *, current_password: str,
                    new_password: str) -> Response
```

Change the user's password.

**Arguments**:

- `session` - HTTP client session (must be authenticated)
- `current_password` - The user's current password
- `new_password` - The new password to set
  

**Returns**:

  HTTP response from the password change request
  

**Raises**:

- `InvalidSessionError` - If no session cookie is found
- `PasswordValidationError` - If password validation fails
- `InvalidCredentialsError` - If current password is incorrect

<a id="streamable.api.user_info"></a>

#### user\_info

```python
def user_info(session: Client) -> Response
```

Get current user information.

**Arguments**:

- `session` - HTTP client session (must be authenticated)
  

**Returns**:

  HTTP response containing user information

<a id="streamable.api.change_player_color"></a>

#### change\_player\_color

```python
def change_player_color(session: Client, *, color: str) -> Response
```

Change the user's video player color.

**Arguments**:

- `session` - HTTP client session (must be authenticated)
- `color` - Hex color code (e.g., '`FF0080`')
  

**Returns**:

  HTTP response from the color change request
  

**Raises**:

- `InvalidPlayerColorError` - If the color format is invalid

<a id="streamable.api.change_privacy_settings"></a>

#### change\_privacy\_settings

```python
def change_privacy_settings(
        session: Client,
        *,
        allow_download: Optional[bool] = None,
        allow_sharing: Optional[bool] = None,
        hide_view_count: Optional[bool] = None,
        visibility: Optional[Literal["public", "private"]] = None) -> Response
```

Change the user's privacy settings.

**Arguments**:

- `session` - HTTP client session (must be authenticated)
- `allow_download` - Whether to allow video downloads (optional)
- `allow_sharing` - Whether to allow video sharing (optional)
- `hide_view_count` - Whether to hide view counts (optional)
- `visibility` - Video visibility setting (optional)
  

**Returns**:

  HTTP response from the privacy settings change request
  

**Raises**:

- `InvalidPrivacySettingsError` - If no settings are provided

<a id="streamable.api.create_label"></a>

#### create\_label

```python
def create_label(session: Client, *, name: str) -> Response
```

Create a new label.

**Arguments**:

- `session` - HTTP client session (must be authenticated)
- `name` - Name of the label to create
  

**Returns**:

  HTTP response from the label creation request
  

**Raises**:

- `LabelAlreadyExistsError` - If a label with this name already exists

<a id="streamable.api.rename_label"></a>

#### rename\_label

```python
def rename_label(session: Client, *, label_id: int, new_name: str) -> Response
```

Rename an existing label.

**Arguments**:

- `session` - HTTP client session (must be authenticated)
- `label_id` - ID of the label to rename
- `new_name` - New name for the label
  

**Returns**:

  HTTP response from the label rename request

<a id="streamable.api.delete_label"></a>

#### delete\_label

```python
def delete_label(session: Client, *, label_id: int) -> Response
```

Delete a label.

**Arguments**:

- `session` - HTTP client session (must be authenticated)
- `label_id` - ID of the label to delete
  

**Returns**:

  HTTP response from the label deletion request
  

**Notes**:

  There is no API-level check for label existence

<a id="streamable.api.labels"></a>

#### labels

```python
def labels(session: Client) -> Response
```

Get all user labels.

**Arguments**:

- `session` - HTTP client session (must be authenticated)
  

**Returns**:

  HTTP response containing the list of user labels

<a id="streamable.api.shortcode"></a>

#### shortcode

```python
def shortcode(session: Client, *, video_file: Path) -> Response
```

Generate a shortcode for video upload.

This is the first step in the video upload process, which generates
upload credentials and S3 information.

**Arguments**:

- `session` - HTTP client session
- `video_file` - Path to the video file to upload
  

**Returns**:

  HTTP response containing upload information

<a id="streamable.api.initialize_video_upload"></a>

#### initialize\_video\_upload

```python
def initialize_video_upload(session: Client,
                            *,
                            upload_info: UploadInfo,
                            video_file: Path,
                            title: Optional[str] = None) -> Response
```

Initialize a video upload with metadata.

This sets up the video record in Streamable's database before
the actual file upload to S3.

**Arguments**:

- `session` - HTTP client session
- `upload_info` - Upload information from shortcode generation
- `video_file` - Path to the video file to upload
- `title` - Optional video title (defaults to filename)
  

**Returns**:

  HTTP response from the initialization request

<a id="streamable.api.cancel_video_upload"></a>

#### cancel\_video\_upload

```python
def cancel_video_upload(session: Client, *, shortcode: str) -> Response
```

Cancel a video upload.

**Arguments**:

- `session` - HTTP client session
- `shortcode` - Shortcode of the upload to cancel
  

**Returns**:

  HTTP response from the cancellation request

<a id="streamable.api.upload_video_file_to_s3"></a>

#### upload\_video\_file\_to\_s3

```python
def upload_video_file_to_s3(session: Client, *, upload_info: UploadInfo,
                            video_file: Path) -> Response
```

Upload the video file to AWS S3.

This performs the actual file upload using the credentials
and information provided by the shortcode generation.

**Arguments**:

- `session` - HTTP client session
- `upload_info` - Upload information from shortcode generation
- `video_file` - Path to the video file to upload
  

**Returns**:

  HTTP response from the S3 upload

<a id="streamable.api.transcode_video_after_upload"></a>

#### transcode\_video\_after\_upload

```python
def transcode_video_after_upload(session: Client, *,
                                 upload_info: UploadInfo) -> Response
```

Start video transcoding after upload.

This is the final step in the upload process, which triggers
the video processing and will make the video available for playback.

**Arguments**:

- `session` - HTTP client session
- `upload_info` - Upload information from shortcode generation
  

**Returns**:

  HTTP response containing the processed video information

<a id="streamable.api.models"></a>

# streamable.api.models

Pydantic models for Streamable.com API requests and responses.

<a id="streamable.api.models.AccountInfo"></a>

## AccountInfo Objects

```python
class AccountInfo(BaseModel)
```

Account information for Streamable.com authentication.

This model represents the basic authentication credentials needed
to interact with the Streamable.com API using email + password authentication.

**Notes**:

  Only email + password authentication is supported by this library.
  Google and Facebook login methods are not available.
  

**Attributes**:

- `username` - User's email address (aliased as 'email' in the constructor)
- `password` - User's password (minimum 8 characters with complexity requirements)

<a id="streamable.api.models.AccountInfo.new"></a>

#### new

```python
@staticmethod
def new() -> "AccountInfo"
```

Generate a new random AccountInfo instance.

Creates an account with a random email address and password
that meets Streamable.com's requirements.

**Returns**:

  A new AccountInfo instance with random credentials

<a id="streamable.api.models.AccountInfo.validate_password_requirements"></a>

#### validate\_password\_requirements

```python
@field_validator("password", mode="after")
@classmethod
def validate_password_requirements(cls, value: str) -> str
```

Validate that password meets Streamable.com requirements.

The password must contain:
- At least one uppercase letter (A-Z)
- At least one lowercase letter (a-z)
- At least one digit (0-9)

**Arguments**:

- `value` - The password to validate
  

**Returns**:

  The validated password
  

**Raises**:

- `ValueError` - If password doesn't meet requirements

<a id="streamable.api.models.LoginRequest"></a>

## LoginRequest Objects

```python
class LoginRequest(AccountInfo)
```

Request model for user login operations.

<a id="streamable.api.models.LoginRequest.new"></a>

#### new

```python
@staticmethod
def new() -> "LoginRequest"
```

Generate a new random LoginRequest.

**Returns**:

  A new LoginRequest instance with random credentials

<a id="streamable.api.models.LoginRequest.from_account_info"></a>

#### from\_account\_info

```python
@staticmethod
def from_account_info(account_info: AccountInfo) -> "LoginRequest"
```

Create a LoginRequest from existing AccountInfo.

**Arguments**:

- `account_info` - The account information to convert
  

**Returns**:

  A new LoginRequest instance

<a id="streamable.api.models.CreateAccountRequest"></a>

## CreateAccountRequest Objects

```python
class CreateAccountRequest(AccountInfo)
```

Request model for account creation operations.

<a id="streamable.api.models.CreateAccountRequest.verification_redirect"></a>

#### verification\_redirect

```python
@computed_field
@property
def verification_redirect(
) -> Literal["https://streamable.com?alert=verified"]
```

URL for email verification redirect.

**Returns**:

  The verification redirect URL

<a id="streamable.api.models.CreateAccountRequest.email"></a>

#### email

```python
@computed_field
@property
def email() -> str
```

Email address for account creation.

**Returns**:

  The username as email string

<a id="streamable.api.models.CreateAccountRequest.new"></a>

#### new

```python
@staticmethod
def new() -> "CreateAccountRequest"
```

Generate a new random CreateAccountRequest.

**Returns**:

  A new CreateAccountRequest instance with random credentials

<a id="streamable.api.models.CreateAccountRequest.from_account_info"></a>

#### from\_account\_info

```python
@staticmethod
def from_account_info(account_info: AccountInfo) -> "CreateAccountRequest"
```

Create a CreateAccountRequest from existing AccountInfo.

**Arguments**:

- `account_info` - The account information to convert
  

**Returns**:

  A new CreateAccountRequest instance

<a id="streamable.api.models.ChangePasswordRequest"></a>

## ChangePasswordRequest Objects

```python
class ChangePasswordRequest(BaseModel)
```

Request model for changing user password.

**Attributes**:

- `current_password` - The user's current password
- `new_password` - The new password to set
- `session` - The current session ID

<a id="streamable.api.models.ChangePlayerColorRequest"></a>

## ChangePlayerColorRequest Objects

```python
class ChangePlayerColorRequest(BaseModel)
```

Request model for changing video player color.

The color must be a valid hexadecimal color code in `RRGGBB` format.

**Attributes**:

- `color` - Hex color code in `RRGGBB` format (e.g., '`FF0080`')

<a id="streamable.api.models.ChangePrivacySettingsRequest"></a>

## ChangePrivacySettingsRequest Objects

```python
class ChangePrivacySettingsRequest(BaseModel)
```

Request model for changing video privacy settings.

**Attributes**:

- `allow_download` - Whether to allow video downloads
- `allow_sharing` - Whether to allow video sharing
- `hide_view_count` - Whether to hide the view count
- `visibility` - Video visibility ('public' or 'private')

<a id="streamable.api.models.ChangePrivacySettingsRequest.domain_restrictions"></a>

#### domain\_restrictions

```python
@computed_field
@property
def domain_restrictions() -> Literal["off"]
```

Domain restrictions setting.

Currently always set to 'off'.

**Returns**:

  Always returns 'off'

<a id="streamable.api.models.CreateLabelRequest"></a>

## CreateLabelRequest Objects

```python
class CreateLabelRequest(BaseModel)
```

Request model for creating a new label.

**Attributes**:

- `name` - The name of the label to create

<a id="streamable.api.models.RenameLabelRequest"></a>

## RenameLabelRequest Objects

```python
class RenameLabelRequest(CreateLabelRequest)
```

Request model for renaming an existing label.

<a id="streamable.api.models.InitializeVideoUploadRequest"></a>

## InitializeVideoUploadRequest Objects

```python
class InitializeVideoUploadRequest(BaseModel)
```

Request model for initializing a video upload.

**Attributes**:

- `original_name` - The original filename of the video
- `original_size` - The size of the video file in bytes
- `title` - The title to assign to the uploaded video

<a id="streamable.api.models.InitializeVideoUploadRequest.upload_source"></a>

#### upload\_source

```python
@computed_field
@property
def upload_source() -> Literal["web"]
```

Source of the upload.

**Returns**:

  Always returns 'web'

<a id="streamable.api.models.ErrorResponse"></a>

## ErrorResponse Objects

```python
class ErrorResponse(BaseModel)
```

Model for API error responses.

Represents error information returned by the Streamable.com API
when requests fail.

**Attributes**:

- `error` - The error type
- `message` - Human-readable error message

<a id="streamable.api.models.PrivacySettings"></a>

## PrivacySettings Objects

```python
class PrivacySettings(BaseModel)
```

Model for user privacy settings.

**Attributes**:

- `visibility` - Video visibility setting ('public' or 'private')
- `allow_sharing` - Whether videos can be shared
- `allow_download` - Whether videos can be downloaded
- `hide_view_count` - Whether to hide view counts

<a id="streamable.api.models.StreamableUnauthenticatedUser"></a>

## StreamableUnauthenticatedUser Objects

```python
class StreamableUnauthenticatedUser(BaseModel)
```

Model for basic user information available without authentication.

**Attributes**:

- `socket` - WebSocket connection URL
- `total_plays` - Total number of video plays
- `total_uploads` - Total number of uploads
- `total_clips` - Total number of clips
- `total_videos` - Total number of videos
- `embed_plays` - Number of embedded plays (might be `None`)
- `total_embeds` - Total number of embeds

<a id="streamable.api.models.StreamableUser"></a>

## StreamableUser Objects

```python
class StreamableUser(StreamableUnauthenticatedUser)
```

Model for authenticated user information.

Extends StreamableUnauthenticatedUser with additional information
that's only available to authenticated users.

**Attributes**:

- `id` - Unique user identifier
- `user_name` - Username/display name
- `email` - User's email address
- `date_added` - Account creation timestamp
- `color` - User's selected player color
- `plays_remaining` - Number of remaining plays (for plan limits)
- `requests_remaining` - Number of remaining API requests
- `allow_download` - Whether downloads are allowed (might be `None`)
- `remove_branding` - Whether branding is removed (might be `None`)
- `hide_sharing` - Whether sharing is hidden (might be `None`)
- `country` - User's country code
- `privacy_settings` - User's privacy configuration

<a id="streamable.api.models.PlanPricing"></a>

## PlanPricing Objects

```python
class PlanPricing(BaseModel)
```

Model for subscription plan pricing information.

**Attributes**:

- `cadence` - Billing frequency ('monthly' or 'annual')
- `name` - Name of the pricing tier
- `price` - Price amount

<a id="streamable.api.models.Feature"></a>

## Feature Objects

```python
class Feature(BaseModel)
```

Model for a plan feature description.

**Attributes**:

- `label` - Short feature name/title
- `description` - Detailed feature description

<a id="streamable.api.models.Plan"></a>

## Plan Objects

```python
class Plan(BaseModel)
```

Model for a Streamable.com subscription plan.

**Attributes**:

- `name` - Plan name
- `description` - Plan description
- `monthly` - Monthly pricing information
- `annual` - Annual pricing information
- `features` - List of plan features

<a id="streamable.api.models.StorageLimits"></a>

## StorageLimits Objects

```python
class StorageLimits(BaseModel)
```

Model for storage limit information.

**Attributes**:

- `exceeded` - Whether storage limits have been exceeded

<a id="streamable.api.models.Limits"></a>

## Limits Objects

```python
class Limits(BaseModel)
```

Model for various account limits.

**Attributes**:

- `storage` - Storage-related limits

<a id="streamable.api.models.Label"></a>

## Label Objects

```python
class Label(BaseModel)
```

Model for a basic label.

**Attributes**:

- `id` - Unique label identifier
- `name` - Label name

<a id="streamable.api.models.UserLabel"></a>

## UserLabel Objects

```python
class UserLabel(Label)
```

Model for a user label with additional metadata.

Extends Label with usage statistics.

**Attributes**:

- `count` - Number of videos with this label

<a id="streamable.api.models.UserLabel.to_label"></a>

#### to\_label

```python
def to_label() -> Label
```

Convert to a basic Label instance.

**Returns**:

  A Label instance without the count field

<a id="streamable.api.models.UserLabels"></a>

## UserLabels Objects

```python
class UserLabels(BaseModel)
```

Model for a collection of user labels.

**Attributes**:

- `userLabels` - List of user labels

<a id="streamable.api.models.Credentials"></a>

## Credentials Objects

```python
class Credentials(BaseModel)
```

Model for AWS temporary credentials.

Contains the temporary AWS credentials needed for S3 upload.

**Attributes**:

- `accessKeyId` - AWS access key ID
- `secretAccessKey` - AWS secret access key
- `sessionToken` - AWS session token for temporary credentials

<a id="streamable.api.models.Fields"></a>

## Fields Objects

```python
class Fields(BaseModel)
```

Model for S3 upload form fields.

Contains all the required fields for AWS S3 signed upload.

**Attributes**:

- `key` - S3 object key/path
- `acl` - Access control list setting
- `bucket` - S3 bucket name
- `X_Amz_Algorithm` - AWS signature algorithm
- `X_Amz_Credential` - AWS credential string
- `X_Amz_Date` - Request date
- `X_Amz_Security_Token` - AWS security token
- `Policy` - Base64-encoded upload policy
- `X_Amz_Signature` - AWS request signature

<a id="streamable.api.models.PlanLimits"></a>

## PlanLimits Objects

```python
class PlanLimits(BaseModel)
```

Model for plan limits information.

Contains flags indicating various plan limitations.

**Attributes**:

- `is_exceeding_free_plan_limits` - Whether free plan limits are exceeded
- `is_exceeding_free_plan_duration_limit` - Whether duration limit is exceeded
- `is_exceeding_free_plan_size_limit` - Whether size limit is exceeded
- `should_restrict_playback` - Whether playback should be restricted
- `has_owner_without_plan` - Whether the owner has no plan

<a id="streamable.api.models.Video"></a>

## Video Objects

```python
class Video(BaseModel)
```

Model representing a successfully uploaded Streamable video.

Contains the essential information returned after a video
has been uploaded and processed by Streamable.com.

**Attributes**:

- `shortcode` - Unique video identifier/shortcode used in URLs
- `date_added` - Upload timestamp (Unix timestamp)
- `url` - Full Streamable video URL (https://streamable.com/{shortcode})
- `plan_limits` - Plan limitation flags and restrictions

<a id="streamable.api.models.Options"></a>

## Options Objects

```python
class Options(BaseModel)
```

Model for video processing options.

**Attributes**:

- `preset` - Processing preset to use
- `shortcode` - Video shortcode
- `screenshot` - Whether to generate screenshot

<a id="streamable.api.models.TranscoderOptions"></a>

## TranscoderOptions Objects

```python
class TranscoderOptions(BaseModel)
```

Model for video transcoding options.

**Attributes**:

- `url` - S3 URL of the uploaded video
- `token` - Authentication token
- `shortcode` - Video shortcode
- `size` - Video file size

<a id="streamable.api.models.UploadInfo"></a>

## UploadInfo Objects

```python
class UploadInfo(BaseModel)
```

Model containing complete upload configuration and credentials.

**Attributes**:

- `accelerated` - Whether accelerated upload is enabled
- `bucket` - S3 bucket name
- `credentials` - AWS temporary credentials
- `fields` - S3 upload form fields
- `url` - Upload URL
- `video` - Video information
- `options` - Processing options
- `shortcode` - Video shortcode
- `key` - S3 object key
- `time` - Upload timestamp
- `transcoder` - Transcoding service name (optional)
- `transcoder_options` - Transcoding configuration

<a id="streamable.utils.s3"></a>

# streamable.utils.s3

AWS S3 Signature V4 utility for generating authentication headers.

This module provides functions to calculate AWS Signature V4 signatures
and build headers for Streamable S3 bucket upload requests.

https://docs.aws.amazon.com/AmazonS3/latest/API/sig-v4-header-based-auth.html

<a id="streamable.utils.s3.calculate_aws_s3_v4_signature"></a>

#### calculate\_aws\_s3\_v4\_signature

```python
def calculate_aws_s3_v4_signature(
        method: str,
        host: str,
        path: str,
        access_key: str,
        secret_key: str,
        session_token: str,
        region: str,
        timestamp: str,
        payload_hash: Union[Literal["UNSIGNED-PAYLOAD"],
                            str] = "UNSIGNED-PAYLOAD",
        query_params: Optional[dict[str, str]] = None,
        extra_headers: Optional[dict[str,
                                     str]] = None) -> tuple[str, str, str]
```

Calculate AWS S3 V4 signature.

**Arguments**:

- `method` - HTTP method (e.g., 'PUT', 'GET')
- `host` - Host header value (e.g., 'some-bucket.s3.amazonaws.com')
- `path` - Request path (e.g., '/some/key')
- `access_key` - AWS access key ID
- `secret_key` - AWS secret access key
- `session_token` - AWS session token
- `region` - AWS region (e.g., 'us-east-1')
- `timestamp` - ISO8601 timestamp (e.g., '20250929T151031Z')
- `payload_hash` - Hash of payload or 'UNSIGNED-PAYLOAD' (default)
- `query_params` - Optional query string parameters
- `extra_headers` - Optional additional headers to sign
  

**Returns**:

  Tuple of (authorization_header, signed_headers, credential_scope)

<a id="streamable.utils.s3.build_s3_upload_headers"></a>

#### build\_s3\_upload\_headers

```python
def build_s3_upload_headers(
        upload_info: UploadInfo,
        content_length: int,
        use_current_timestamp: bool = True) -> dict[str, str]
```

Build headers for the Streamable S3 bucket upload request from the UploadInfo model.

**Arguments**:

- `upload_info` - UploadInfo pydantic model instance
- `content_length` - Size of the file being uploaded in bytes
- `use_current_timestamp` - If True, generate a new timestamp (must use for actual uploads)
  

**Returns**:

  Dictionary of headers ready for the PUT request

<a id="streamable.utils"></a>

# streamable.utils

Utility functions for Streamable.py.

<a id="streamable.utils.random_string"></a>

#### random\_string

```python
def random_string(length: int, *charsets: str) -> str
```

Generate a random string with characters from the provided charsets.

Ensures at least one character from each charset is included in the result.
The remaining positions are filled with random characters from all charsets combined.

**Arguments**:

- `length` - The desired length of the random string (if less than number of charsets, it will be increased)
- `*charsets` - Variable number of character sets to choose from
  

**Returns**:

  A randomly generated string of the specified length
  

**Raises**:

- `ValueError` - If no charsets are provided
  

**Example**:

    ```python
    random_string(10, "abc", "123")  # 'a2cb13abc2'
    ```

<a id="streamable.utils.random_email_domain"></a>

#### random\_email\_domain

```python
def random_email_domain() -> str
```

Return a random email domain from a predefined list of common providers.

**Returns**:

  A random email domain string (e.g., 'gmail.com', 'yahoo.com')
  

**Example**:

    ```python
    random_email_domain()  # 'gmail.com'
    ```

<a id="streamable.utils.rgb_to_hex"></a>

#### rgb\_to\_hex

```python
def rgb_to_hex(r: int, g: int, b: int) -> str
```

Convert RGB color values to hexadecimal color code.

**Arguments**:

- `r` - Red component (0-255)
- `g` - Green component (0-255)
- `b` - Blue component (0-255)
  

**Returns**:

  Hexadecimal color code in format `RRGGBB`
  

**Raises**:

- `ValueError` - If any RGB value is not between 0 and 255
  

**Example**:

    ```python
    rgb_to_hex(255, 0, 128)  # `FF0080`
    ```

<a id="streamable.utils.get_video_duration"></a>

#### get\_video\_duration

```python
def get_video_duration(video_file: Path) -> int
```

Get the duration of a video file in milliseconds.

**Arguments**:

- `video_file` - Path to the video file
  

**Returns**:

  Duration in milliseconds
  

**Raises**:

- `ValueError` - If the file is not a valid video file or doesn't exist
  

**Example**:

    ```python
    duration = get_video_duration(Path("video.mp4"))
    print(f"Video is {duration / 1000} seconds long")
    ```

<a id="streamable.utils.ensure_is_not_more_than_10_minutes"></a>

#### ensure\_is\_not\_more\_than\_10\_minutes

```python
def ensure_is_not_more_than_10_minutes(video_file: Path) -> None
```

Validate that a video file meets Streamable's free plan duration limit.

Checks if the video duration is within the 10-minute limit imposed
by Streamable.com for free accounts. This validation is automatically
performed before upload.

**Arguments**:

- `video_file` - Path to the video file to check
  

**Raises**:

- `VideoTooLongError` - If the video is longer than 10 minutes
- `ValueError` - If the file is not a valid video file

<a id="streamable.utils.ensure_is_not_more_than_250mb"></a>

#### ensure\_is\_not\_more\_than\_250mb

```python
def ensure_is_not_more_than_250mb(file: Path) -> None
```

Validate that a file meets Streamable's free plan size limit.

Checks if the file size is within the 250MB limit imposed by
Streamable.com for free accounts. This validation is automatically
performed before upload.

**Arguments**:

- `file` - Path to the file to check
  

**Raises**:

- `VideoTooLargeError` - If the file is larger than 250MB
- `ValueError` - If the file doesn't exist

<a id="streamable.utils.stream_file"></a>

#### stream\_file

```python
def stream_file(
    file: Path,
    *,
    chunk_size: int = 8 * 1024 * 1024,
    progress_cb: Optional[Callable[[float], None]] = None,
    complete_cb: Optional[Callable[[], None]] = None
) -> Generator[bytes, None, None]
```

Stream a file in chunks with optional progress tracking.

**Arguments**:

- `file` - Path to the file to stream
- `chunk_size` - Size of each chunk in bytes (default: 8MB)
- `progress_cb` - Optional callback for progress updates (receives percentage)
- `complete_cb` - Optional callback called when streaming is complete
  

**Yields**:

  Chunks of file data as bytes
  

**Raises**:

- `ValueError` - If the file doesn't exist or is not a valid file
  

**Example**:

    ```python
    def progress(pct):
        print(f"Progress: {pct:.1f}%")

    for chunk in stream_file(Path("video.mp4"), progress_cb=progress):
        # Process chunk
        pass
    ```

