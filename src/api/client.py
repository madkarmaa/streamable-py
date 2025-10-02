from types import TracebackType
from typing import Optional, Type, Union, overload
from httpx import Client, Response
from pathlib import Path
from .exceptions import InvalidSessionError
from . import *
from .models import *
from ..utils import ensure_is_not_more_than_10_minutes, ensure_is_not_more_than_250mb


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
        self._client = Client()

    def get_user_info(self) -> StreamableUser:
        self._ensure_authenticated()
        response: Response = user_info(self._client)
        return StreamableUser.model_validate(response.json())

    def change_password(self, new_password: str) -> None:
        self._ensure_authenticated()
        assert self._account_info is not None

        change_password(
            self._client,
            current_password=self._account_info.password,
            new_password=new_password,
        )

        self._account_info.password = new_password

    def change_player_color(self, color: str) -> None:
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
        self._ensure_authenticated()
        response: Response = create_label(self._client, name=name)
        return Label.model_validate(response.json())

    @overload
    def rename_label(self, label: int, new_name: str) -> Label: ...
    @overload
    def rename_label(self, label: Label, new_name: str) -> Label: ...
    def rename_label(self, label: Union[int, Label], new_name: str) -> Label:
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
        self._ensure_authenticated()

        if isinstance(label, Label):
            label_id: int = label.id
        else:
            label_id: int = label

        delete_label(self._client, label_id=label_id)

    def get_user_labels(self) -> list[UserLabel]:
        self._ensure_authenticated()
        response: Response = labels(self._client)
        return UserLabels.model_validate(response.json()).userLabels

    def get_label_by_name(self, name: str) -> Optional[UserLabel]:
        labels: list[UserLabel] = self.get_user_labels()
        for label in labels:
            if label.name == name:
                return label
        return None

    def upload_video(self, video_file: Path) -> Video:
        video_file = video_file.resolve()

        ensure_is_not_more_than_250mb(video_file)
        ensure_is_not_more_than_10_minutes(video_file)

        shortcode_response: Response = shortcode(
            session=self._client if self._authenticated else None,
            video_file=video_file,
        )

        upload_info: UploadInfo = UploadInfo.model_validate(shortcode_response.json())

        initialize_video_upload(
            session=self._client if self._authenticated else None,
            upload_info=upload_info,
            video_file=video_file,
        )

        upload_video_file_to_s3(
            session=self._client if self._authenticated else None,
            upload_info=upload_info,
            video_file=video_file,
        )

        transcoding_response: Response = transcode_video_after_upload(
            session=self._client if self._authenticated else None,
            upload_info=upload_info,
        )

        return Video.model_validate(transcoding_response.json())

    def __enter__(self) -> "StreamableClient":
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        self.logout()
