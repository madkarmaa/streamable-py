from secrets import choice, SystemRandom
from pathlib import Path
from pymediainfo import MediaInfo, Track
from typing import Callable, Generator, Optional


def random_string(length: int, *charsets: str) -> str:
    length = max(len(charsets), length)  # ensure length is at least number of charsets

    if not charsets:
        raise ValueError("At least one charset must be provided")

    # ensure at least one character from each charset
    result: list[str] = [choice(charset) for charset in charsets]

    # fill remaining positions with random characters from all charsets combined
    result.extend(choice("".join(charsets)) for _ in range(length - len(charsets)))

    SystemRandom().shuffle(result)
    return "".join(result)


def random_email_domain() -> str:
    return choice(
        [
            "gmail.com",
            "yahoo.com",
            "hotmail.com",
            "aol.com",
            "hotmail.co.uk",
            "hotmail.fr",
            "msn.com",
            "yahoo.fr",
            "wanadoo.fr",
            "orange.fr",
            "comcast.net",
            "yahoo.co.uk",
            "yahoo.com.br",
            "yahoo.co.in",
            "live.com",
            "rediffmail.com",
            "free.fr",
            "gmx.de",
            "web.de",
            "yandex.ru",
            "ymail.com",
            "libero.it",
            "outlook.com",
            "uol.com.br",
            "bol.com.br",
            "mail.ru",
            "cox.net",
            "hotmail.it",
            "sbcglobal.net",
            "sfr.fr",
            "live.fr",
            "verizon.net",
            "live.co.uk",
            "googlemail.com",
            "yahoo.es",
            "ig.com.br",
            "live.nl",
            "bigpond.com",
            "terra.com.br",
            "yahoo.it",
            "neuf.fr",
            "yahoo.de",
            "alice.it",
            "rocketmail.com",
            "att.net",
            "laposte.net",
            "facebook.com",
            "bellsouth.net",
            "yahoo.in",
            "hotmail.es",
            "charter.net",
            "yahoo.ca",
            "yahoo.com.au",
            "rambler.ru",
            "hotmail.de",
            "tiscali.it",
            "shaw.ca",
            "yahoo.co.jp",
            "sky.com",
            "earthlink.net",
            "optonline.net",
            "freenet.de",
            "t-online.de",
            "aliceadsl.fr",
            "virgilio.it",
            "home.nl",
            "qq.com",
            "telenet.be",
            "me.com",
            "yahoo.com.ar",
            "tiscali.co.uk",
            "yahoo.com.mx",
            "voila.fr",
            "gmx.net",
            "mail.com",
            "planet.nl",
            "tin.it",
            "live.it",
            "ntlworld.com",
            "arcor.de",
            "yahoo.co.id",
            "frontiernet.net",
            "hetnet.nl",
            "live.com.au",
            "yahoo.com.sg",
            "zonnet.nl",
            "club-internet.fr",
            "juno.com",
            "optusnet.com.au",
            "blueyonder.co.uk",
            "bluewin.ch",
            "skynet.be",
            "sympatico.ca",
            "windstream.net",
            "mac.com",
            "centurytel.net",
            "chello.nl",
            "live.ca",
            "aim.com",
            "bigpond.net.au",
        ]
    )


def rgb_to_hex(r: int, g: int, b: int) -> str:
    for val, name in [(r, "red"), (g, "green"), (b, "blue")]:
        if not 0 <= val <= 255:
            raise ValueError(
                f"{name} value must be an integer between 0 and 255, got {val}"
            )

    return f"#{r:02X}{g:02X}{b:02X}"


def _ensure_is_file(path: Path) -> None:
    path = path.resolve()
    if not path.is_file() or not path.exists():
        raise ValueError(f"Path '{path}' is not a valid file")


def get_video_duration(video_file: Path) -> int:
    video_file = video_file.resolve()
    _ensure_is_file(video_file)

    media_info: MediaInfo = MediaInfo.parse(video_file)
    tracks: list[Track] = media_info.tracks  # type: ignore - the library has no type hints :(

    # https://github.com/sbraz/pymediainfo?tab=readme-ov-file#example-snippet-1
    for track in tracks:
        if track.track_type == "Video":
            return int(track.duration)  # again, no type hints

    raise ValueError(f"File '{video_file}' is not a valid video file")


def is_more_than_10_minutes(duration_ms: int) -> bool:
    return duration_ms > 10 * 60 * 1000  # 10 minutes in milliseconds


def is_more_than_250mb(file: Path) -> bool:
    file = file.resolve()
    _ensure_is_file(file)
    return file.stat().st_size > 250 * 1024 * 1024  # 250 MB in bytes


def stream_file(
    file: Path,
    *,
    chunk_size: int = 1024 * 8,
    progress_cb: Optional[Callable[[float], None]] = None,
    complete_cb: Optional[Callable[[], None]] = None,
) -> Generator[bytes, None, None]:
    file = file.resolve()
    _ensure_is_file(file)

    file_size: int = file.stat().st_size
    bytes_sent: int = 0

    with file.open("rb") as f:
        while chunk := f.read(chunk_size):
            yield chunk
            bytes_sent += len(chunk)

            if progress_cb is not None:
                progress_cb(bytes_sent / file_size * 100)

    if complete_cb is not None:
        complete_cb()
