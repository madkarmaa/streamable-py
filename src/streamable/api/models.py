"""Pydantic models for Streamable.com API requests and responses."""

import re
import string
from secrets import randbelow
from typing import Literal, Optional, Annotated
from pydantic import (
    BaseModel,
    Field,
    EmailStr,
    field_validator,
    computed_field,
    ConfigDict,
    StringConstraints,
)
from ..utils import random_string, random_email_domain


PASSWORD_MIN_LENGTH: int = 8


class AccountInfo(BaseModel, validate_assignment=True):
    """Account information for Streamable.com authentication.

    This model represents the basic authentication credentials needed
    to interact with the Streamable.com API using email + password authentication.

    Note:
        Only email + password authentication is supported by this library.
        Google and Facebook login methods are not available.

    Attributes:
        username: User's email address (aliased as 'email' in the constructor)
        password: User's password (minimum 8 characters with complexity requirements)
    """

    username: EmailStr = Field(..., alias="email", frozen=True)
    password: str = Field(..., min_length=PASSWORD_MIN_LENGTH)

    @staticmethod
    def new() -> "AccountInfo":
        """Generate a new random AccountInfo instance.

        Creates an account with a random email address and password
        that meets Streamable.com's requirements.

        Returns:
            A new AccountInfo instance with random credentials
        """
        email: str = f"{random_string(randbelow(21), string.ascii_lowercase, string.digits)}@{random_email_domain()}"
        password: str = random_string(
            randbelow(13) + PASSWORD_MIN_LENGTH,  # 8 to 20 characters
            string.ascii_lowercase,
            string.ascii_uppercase,
            string.digits,
        )
        return AccountInfo(email=email, password=password)

    @field_validator("password", mode="after")
    @classmethod
    def validate_password_requirements(cls, value: str) -> str:
        """Validate that password meets Streamable.com requirements.

        The password must contain:
        - At least one uppercase letter (A-Z)
        - At least one lowercase letter (a-z)
        - At least one digit (0-9)

        Args:
            value: The password to validate

        Returns:
            The validated password

        Raises:
            ValueError: If password doesn't meet requirements
        """
        if not re.search(r"[A-Z]", value):
            raise ValueError(
                "Password must contain at least one uppercase letter (A–Z)."
            )
        if not re.search(r"[a-z]", value):
            raise ValueError(
                "Password must contain at least one lowercase letter (a–z)."
            )
        if not re.search(r"\d", value):
            raise ValueError("Password must contain at least one digit (0–9).")
        return value


class LoginRequest(AccountInfo):
    """Request model for user login operations."""

    @staticmethod
    def new() -> "LoginRequest":
        """Generate a new random LoginRequest.

        Returns:
            A new LoginRequest instance with random credentials
        """
        account_info: AccountInfo = AccountInfo.new()
        return LoginRequest.from_account_info(account_info)

    @staticmethod
    def from_account_info(account_info: AccountInfo) -> "LoginRequest":
        """Create a LoginRequest from existing AccountInfo.

        Args:
            account_info: The account information to convert

        Returns:
            A new LoginRequest instance
        """
        return LoginRequest(
            email=account_info.username,
            password=account_info.password,
        )


class CreateAccountRequest(AccountInfo):
    """Request model for account creation operations."""

    @computed_field
    @property
    def verification_redirect(self) -> Literal["https://streamable.com?alert=verified"]:
        """URL for email verification redirect.

        Returns:
            The verification redirect URL
        """
        return "https://streamable.com?alert=verified"

    @computed_field
    @property
    def email(self) -> str:
        """Email address for account creation.

        Returns:
            The username as email string
        """
        return self.username

    @staticmethod
    def new() -> "CreateAccountRequest":
        """Generate a new random CreateAccountRequest.

        Returns:
            A new CreateAccountRequest instance with random credentials
        """
        account_info: AccountInfo = AccountInfo.new()
        return CreateAccountRequest.from_account_info(account_info)

    @staticmethod
    def from_account_info(account_info: AccountInfo) -> "CreateAccountRequest":
        """Create a CreateAccountRequest from existing AccountInfo.

        Args:
            account_info: The account information to convert

        Returns:
            A new CreateAccountRequest instance
        """
        return CreateAccountRequest(
            email=account_info.username,
            password=account_info.password,
        )


class ChangePasswordRequest(BaseModel):
    """Request model for changing user password.

    Attributes:
        current_password: The user's current password
        new_password: The new password to set
        session: The current session ID
    """

    current_password: str
    new_password: str
    session: str


class ChangePlayerColorRequest(BaseModel):
    """Request model for changing video player color.

    The color must be a valid hexadecimal color code in #RRGGBB format.

    Attributes:
        color: Hex color code in #RRGGBB format (e.g., '#FF0080')
    """

    # there is no API-level check for valid colors, so we need to do it ourselves
    color: Annotated[
        str,
        StringConstraints(
            pattern=r"^#[0-9A-Fa-f]{6}$", strip_whitespace=True, to_lower=True
        ),
    ]


class ChangePrivacySettingsRequest(BaseModel):
    """Request model for changing video privacy settings.

    Attributes:
        allow_download: Whether to allow video downloads
        allow_sharing: Whether to allow video sharing
        hide_view_count: Whether to hide the view count
        visibility: Video visibility ('public' or 'private')
    """

    allow_download: Optional[bool] = None
    allow_sharing: Optional[bool] = None
    hide_view_count: Optional[bool] = None
    visibility: Optional[Literal["public", "private"]] = None

    @computed_field
    @property
    def domain_restrictions(self) -> Literal["off"]:
        """Domain restrictions setting.

        Currently always set to 'off'.

        Returns:
            Always returns 'off'
        """
        return "off"


class CreateLabelRequest(BaseModel):
    """Request model for creating a new label.

    Attributes:
        name: The name of the label to create
    """

    name: str


class RenameLabelRequest(CreateLabelRequest):
    """Request model for renaming an existing label."""

    pass


class InitializeVideoUploadRequest(BaseModel):
    """Request model for initializing a video upload.

    Attributes:
        original_name: The original filename of the video
        original_size: The size of the video file in bytes
        title: The title to assign to the uploaded video
    """

    original_name: str
    original_size: int
    title: str

    @computed_field
    @property
    def upload_source(self) -> Literal["web"]:
        """Source of the upload.

        Returns:
            Always returns 'web'
        """
        return "web"


class ErrorResponse(BaseModel):
    """Model for API error responses.

    Represents error information returned by the Streamable.com API
    when requests fail.

    Attributes:
        error: The error type
        message: Human-readable error message
    """

    model_config = ConfigDict(extra="ignore")

    error: str
    message: str


class PrivacySettings(BaseModel):
    """Model for user privacy settings.

    Attributes:
        visibility: Video visibility setting ('public' or 'private')
        allow_sharing: Whether videos can be shared
        allow_download: Whether videos can be downloaded
        hide_view_count: Whether to hide view counts
    """

    model_config = ConfigDict(extra="ignore")

    visibility: Literal["public", "private"]
    allow_sharing: bool
    allow_download: bool
    hide_view_count: bool


class StreamableUnauthenticatedUser(BaseModel):
    """Model for basic user information available without authentication.

    Attributes:
        socket: WebSocket connection URL
        total_plays: Total number of video plays
        total_uploads: Total number of uploads
        total_clips: Total number of clips
        total_videos: Total number of videos
        embed_plays: Number of embedded plays (might be `None`)
        total_embeds: Total number of embeds
    """

    model_config = ConfigDict(extra="ignore")

    socket: str
    total_plays: int
    total_uploads: int
    total_clips: int
    total_videos: int
    embed_plays: Optional[int]
    total_embeds: int


class StreamableUser(StreamableUnauthenticatedUser):
    """Model for authenticated user information.

    Extends StreamableUnauthenticatedUser with additional information
    that's only available to authenticated users.

    Attributes:
        id: Unique user identifier
        user_name: Username/display name
        email: User's email address
        date_added: Account creation timestamp
        color: User's selected player color
        plays_remaining: Number of remaining plays (for plan limits)
        requests_remaining: Number of remaining API requests
        allow_download: Whether downloads are allowed (might be `None`)
        remove_branding: Whether branding is removed (might be `None`)
        hide_sharing: Whether sharing is hidden (might be `None`)
        country: User's country code
        privacy_settings: User's privacy configuration
    """

    model_config = ConfigDict(extra="ignore")

    id: int
    user_name: str
    email: str
    date_added: float
    color: str
    plays_remaining: int
    requests_remaining: int
    allow_download: Optional[bool]
    remove_branding: Optional[bool]
    hide_sharing: Optional[bool]
    country: str
    privacy_settings: PrivacySettings


class PlanPricing(BaseModel):
    """Model for subscription plan pricing information.

    Attributes:
        cadence: Billing frequency ('monthly' or 'annual')
        name: Name of the pricing tier
        price: Price amount
    """

    model_config = ConfigDict(extra="ignore")

    cadence: Literal["monthly", "annual"]
    name: str
    price: float


class Feature(BaseModel):
    """Model for a plan feature description.

    Attributes:
        label: Short feature name/title
        description: Detailed feature description
    """

    label: str
    description: str


class Plan(BaseModel):
    """Model for a Streamable.com subscription plan.

    Attributes:
        name: Plan name
        description: Plan description
        monthly: Monthly pricing information
        annual: Annual pricing information
        features: List of plan features
    """

    model_config = ConfigDict(extra="ignore")

    name: str
    description: str
    monthly: PlanPricing
    annual: PlanPricing
    features: list[Feature]


class StorageLimits(BaseModel):
    """Model for storage limit information.

    Attributes:
        exceeded: Whether storage limits have been exceeded
    """

    exceeded: bool


class Limits(BaseModel):
    """Model for various account limits.

    Attributes:
        storage: Storage-related limits
    """

    storage: StorageLimits


class Label(BaseModel):
    """Model for a basic label.

    Attributes:
        id: Unique label identifier
        name: Label name
    """

    model_config = ConfigDict(extra="ignore")

    id: int
    name: str


class UserLabel(Label):
    """Model for a user label with additional metadata.

    Extends Label with usage statistics.

    Attributes:
        count: Number of videos with this label
    """

    count: int

    def to_label(self) -> Label:
        """Convert to a basic Label instance.

        Returns:
            A Label instance without the count field
        """
        return Label.model_validate(self.model_dump())


class UserLabels(BaseModel):
    """Model for a collection of user labels.

    Attributes:
        userLabels: List of user labels
    """

    userLabels: list[UserLabel]


class Credentials(BaseModel):
    """Model for AWS temporary credentials.

    Contains the temporary AWS credentials needed for S3 upload.

    Attributes:
        accessKeyId: AWS access key ID
        secretAccessKey: AWS secret access key
        sessionToken: AWS session token for temporary credentials
    """

    accessKeyId: str
    secretAccessKey: str
    sessionToken: str


class Fields(BaseModel):
    """Model for S3 upload form fields.

    Contains all the required fields for AWS S3 signed upload.

    Attributes:
        key: S3 object key/path
        acl: Access control list setting
        bucket: S3 bucket name
        X_Amz_Algorithm: AWS signature algorithm
        X_Amz_Credential: AWS credential string
        X_Amz_Date: Request date
        X_Amz_Security_Token: AWS security token
        Policy: Base64-encoded upload policy
        X_Amz_Signature: AWS request signature
    """

    key: str
    acl: str
    bucket: str
    X_Amz_Algorithm: str = Field(alias="X-Amz-Algorithm")
    X_Amz_Credential: str = Field(alias="X-Amz-Credential")
    X_Amz_Date: str = Field(alias="X-Amz-Date")
    X_Amz_Security_Token: str = Field(alias="X-Amz-Security-Token")
    Policy: str
    X_Amz_Signature: str = Field(alias="X-Amz-Signature")


class PlanLimits(BaseModel):
    """Model for plan limits information.

    Contains flags indicating various plan limitations.

    Attributes:
        is_exceeding_free_plan_limits: Whether free plan limits are exceeded
        is_exceeding_free_plan_duration_limit: Whether duration limit is exceeded
        is_exceeding_free_plan_size_limit: Whether size limit is exceeded
        should_restrict_playback: Whether playback should be restricted
        has_owner_without_plan: Whether the owner has no plan
    """

    is_exceeding_free_plan_limits: bool
    is_exceeding_free_plan_duration_limit: bool
    is_exceeding_free_plan_size_limit: bool
    should_restrict_playback: bool
    has_owner_without_plan: bool


class Video(BaseModel):
    """Model representing a successfully uploaded Streamable video.

    Contains the essential information returned after a video
    has been uploaded and processed by Streamable.com.

    Attributes:
        shortcode: Unique video identifier/shortcode used in URLs
        date_added: Upload timestamp (Unix timestamp)
        url: Full Streamable video URL (https://streamable.com/{shortcode})
        plan_limits: Plan limitation flags and restrictions
    """

    model_config = ConfigDict(extra="ignore")

    shortcode: str
    date_added: int
    url: str
    plan_limits: PlanLimits


class Options(BaseModel):
    """Model for video processing options.

    Attributes:
        preset: Processing preset to use
        shortcode: Video shortcode
        screenshot: Whether to generate screenshot
    """

    preset: str
    shortcode: str
    screenshot: bool


class TranscoderOptions(BaseModel):
    """Model for video transcoding options.

    Attributes:
        url: S3 URL of the uploaded video
        token: Authentication token
        shortcode: Video shortcode
        size: Video file size
    """

    url: str
    token: str
    shortcode: str
    size: int


class UploadInfo(BaseModel):
    """Model containing complete upload configuration and credentials.

    Attributes:
        accelerated: Whether accelerated upload is enabled
        bucket: S3 bucket name
        credentials: AWS temporary credentials
        fields: S3 upload form fields
        url: Upload URL
        video: Video information
        options: Processing options
        shortcode: Video shortcode
        key: S3 object key
        time: Upload timestamp
        transcoder: Transcoding service name (optional)
        transcoder_options: Transcoding configuration
    """

    model_config = ConfigDict(extra="ignore")

    accelerated: bool
    bucket: str
    credentials: Credentials
    fields: Fields
    url: str
    video: Video
    options: Options
    shortcode: str
    key: str
    time: int
    transcoder: Optional[str]
    transcoder_options: TranscoderOptions
