import re
import string
from secrets import randbelow
from typing import Any, Optional, Generic, TypeVar
from pydantic import BaseModel, Field, EmailStr, field_validator, computed_field
from ..utils import random_string, random_email_domain


PASSWORD_MIN_LENGTH: int = 8


class AccountInfo(BaseModel):
    username: EmailStr = Field(..., alias="email", frozen=True)
    password: str = Field(..., min_length=PASSWORD_MIN_LENGTH, frozen=True)

    @staticmethod
    def new() -> "AccountInfo":
        email = f"{random_string(randbelow(21), string.ascii_lowercase, string.digits)}@{random_email_domain()}"
        password = random_string(
            randbelow(13) + PASSWORD_MIN_LENGTH,  # 8 to 20 characters
            string.ascii_lowercase,
            string.ascii_uppercase,
            string.digits,
        )
        return AccountInfo(email=email, password=password)

    @field_validator("password", mode="after")
    @classmethod
    def validate_password_requirements(cls, value: str) -> str:
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
    @staticmethod
    def new() -> "LoginRequest":
        account_info: AccountInfo = AccountInfo.new()
        return LoginRequest.from_account_info(account_info)

    @staticmethod
    def from_account_info(account_info: AccountInfo) -> "LoginRequest":
        return LoginRequest(
            email=account_info.username,
            password=account_info.password,
        )


class CreateAccountRequest(AccountInfo):
    @computed_field
    @property
    def verification_redirect(self) -> str:
        return "https://streamable.com?alert=verified"

    @computed_field
    @property
    def email(self) -> str:
        return self.username

    @staticmethod
    def new() -> "CreateAccountRequest":
        account_info: AccountInfo = AccountInfo.new()
        return CreateAccountRequest.from_account_info(account_info)

    @staticmethod
    def from_account_info(account_info: AccountInfo) -> "CreateAccountRequest":
        return CreateAccountRequest(
            email=account_info.username,
            password=account_info.password,
        )


class ErrorResponse(BaseModel):
    error: str
    message: str


class PlanOptions(BaseModel):
    price: str
    stripe_id: str


class UnauthenticatedPlanOptions(PlanOptions):
    paypal_id: str
    paypal_id_notrial: str


TPlan = TypeVar("TPlan", bound=PlanOptions)


class PrivacySettings(BaseModel):
    VERSION: int
    visibility: str
    allow_sharing: bool
    allow_download: bool
    allowed_domain: str
    hide_view_count: bool
    domain_restrictions: str


class StreamableUserBase(BaseModel, Generic[TPlan]):
    plan_name: str
    plan_price: int
    plan_annual: bool
    plan_plays: int
    plan_requests: int
    plan_max_length: int
    plan_max_size: float
    plan_hide_branding: bool
    plan_options: dict[str, TPlan]
    socket: str
    stale: int
    total_plays: int
    total_uploads: int
    total_clips: int
    total_videos: int
    embed_plays: int
    total_embeds: int
    no_trial: bool
    promos: list[str]


class StreamableUnauthenticatedUser(StreamableUserBase[UnauthenticatedPlanOptions]):
    pass


class StreamableUser(StreamableUserBase[PlanOptions]):
    id: int
    user_name: str
    email: str
    date_added: int
    privacy: int
    bio: str
    default_sub: Optional[str]
    stream_key: Optional[str]
    pro: Optional[Any]
    ad_tags: Optional[Any]
    photo_url: Optional[str]
    watermark_url: Optional[str]
    parent: Optional[Any]
    twitter: str
    embed_options: Optional[Any]
    subreddits: Optional[Any]
    watermark_link: Optional[str]
    plan: Optional[Any]
    dark_mode: Optional[bool]
    plays_remaining: int
    requests_remaining: int
    allow_download: Optional[bool]
    remove_branding: bool
    hide_sharing: Optional[Any]
    allowed_domain: str
    disable_streamable: bool
    subscription_status: Optional[str]
    payment_processor: Optional[str]
    hosting_provider: bool
    email_verified: bool
    requires_email_verification: bool
    restricted: bool
    password_set: bool
    beta: bool
    color: str
    country: str
    isp: str
    privacy_settings: PrivacySettings
    terms_accepted: Optional[Any]


class PlanPricing(BaseModel):
    id: str
    cadence: str
    name: str
    price: float


class Feature(BaseModel):
    label: str
    description: str


class Plan(BaseModel):
    name: str
    description: str
    monthly: PlanPricing
    annual: PlanPricing
    features: list[Feature]
    productId: str


class StorageLimits(BaseModel):
    exceeded: bool


class Limits(BaseModel):
    storage: StorageLimits


class SubscriptionInfo(BaseModel):
    availablePlans: list[Plan]
    currentPlan: Optional[Plan] = None
    nextPlan: Optional[Plan] = None
    card: Optional[str] = None
    limits: Limits
