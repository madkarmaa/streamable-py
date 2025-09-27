import re
import string
from secrets import randbelow
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
