"""Utility functions for Streamable.py."""

from secrets import choice, SystemRandom
from pathlib import Path
from pymediainfo import MediaInfo, Track
from typing import Callable, Generator, Optional
from ..api.exceptions import VideoTooLargeError, VideoTooLongError


def random_string(length: int, *charsets: str) -> str:
    """Generate a random string with characters from the provided charsets.

    Ensures at least one character from each charset is included in the result.
    The remaining positions are filled with random characters from all charsets combined.

    Args:
        length: The desired length of the random string (if less than number of charsets, it will be increased)
        *charsets: Variable number of character sets to choose from

    Returns:
        A randomly generated string of the specified length

    Raises:
        ValueError: If no charsets are provided

    Example:
    ```python
    random_string(10, "abc", "123")  # 'a2cb13abc2'
    ```
    """
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
    """Return a random email domain from a predefined list of common providers.

    Returns:
        A random email domain string (e.g., 'gmail.com', 'yahoo.com')

    Example:
    ```python
    random_email_domain()  # 'gmail.com'
    ```
    """
    return choice(
        [  # list taken from https://gist.github.com/ef1500/e73d501f84ff3081858c2cabdd683e80
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
    """Convert RGB color values to hexadecimal color code.

    Args:
        r: Red component (0-255)
        g: Green component (0-255)
        b: Blue component (0-255)

    Returns:
        Hexadecimal color code in format #RRGGBB

    Raises:
        ValueError: If any RGB value is not between 0 and 255

    Example:
    ```python
    rgb_to_hex(255, 0, 128)  # #FF0080
    ```
    """
    for val, name in [(r, "red"), (g, "green"), (b, "blue")]:
        if not 0 <= val <= 255:
            raise ValueError(
                f"{name} value must be an integer between 0 and 255, got {val}"
            )

    return f"#{r:02X}{g:02X}{b:02X}"


def _ensure_is_file(path: Path) -> None:
    """Ensure that the given path points to an existing file.

    Args:
        path: Path to validate

    Raises:
        ValueError: If the path is not a valid existing file
    """
    path = path.resolve()
    if not path.is_file() or not path.exists():
        raise ValueError(f"Path '{path}' is not a valid file")


def get_video_duration(video_file: Path) -> int:
    """Get the duration of a video file in milliseconds.

    Args:
        video_file: Path to the video file

    Returns:
        Duration in milliseconds

    Raises:
        ValueError: If the file is not a valid video file or doesn't exist

    Example:
    ```python
    duration = get_video_duration(Path("video.mp4"))
    print(f"Video is {duration / 1000} seconds long")
    ```
    """
    video_file = video_file.resolve()
    _ensure_is_file(video_file)

    media_info: MediaInfo = MediaInfo.parse(video_file)
    tracks: list[Track] = media_info.tracks  # type: ignore - the library has no type hints :(

    # https://github.com/sbraz/pymediainfo?tab=readme-ov-file#example-snippet-1
    for track in tracks:
        if track.track_type == "Video":
            return int(track.duration)  # again, no type hints

    raise ValueError(f"File '{video_file}' is not a valid video file")


def ensure_is_not_more_than_10_minutes(video_file: Path) -> None:
    """Validate that a video file meets Streamable's free plan duration limit.

    Checks if the video duration is within the 10-minute limit imposed
    by Streamable.com for free accounts. This validation is automatically
    performed before upload.

    Args:
        video_file: Path to the video file to check

    Raises:
        VideoTooLongError: If the video is longer than 10 minutes
        ValueError: If the file is not a valid video file
    """
    ten_minutes_ms: int = 10 * 60 * 1000
    video_file = video_file.resolve()

    _ensure_is_file(video_file)
    video_duration: int = get_video_duration(video_file)

    if video_duration > ten_minutes_ms:
        raise VideoTooLongError(
            video_file, length=video_duration, max_length=ten_minutes_ms
        )


def ensure_is_not_more_than_250mb(file: Path) -> None:
    """Validate that a file meets Streamable's free plan size limit.

    Checks if the file size is within the 250MB limit imposed by
    Streamable.com for free accounts. This validation is automatically
    performed before upload.

    Args:
        file: Path to the file to check

    Raises:
        VideoTooLargeError: If the file is larger than 250MB
        ValueError: If the file doesn't exist
    """
    two_hundred_fifty_mb: int = 250 * 1024 * 1024
    file = file.resolve()

    _ensure_is_file(file)
    file_size: int = file.stat().st_size

    if file_size > two_hundred_fifty_mb:
        raise VideoTooLargeError(file, size=file_size, max_size=two_hundred_fifty_mb)


def stream_file(
    file: Path,
    *,
    chunk_size: int = 8 * 1024 * 1024,  # 8 MB
    progress_cb: Optional[Callable[[float], None]] = None,
    complete_cb: Optional[Callable[[], None]] = None,
) -> Generator[bytes, None, None]:
    """Stream a file in chunks with optional progress tracking.

    Args:
        file: Path to the file to stream
        chunk_size: Size of each chunk in bytes (default: 8MB)
        progress_cb: Optional callback for progress updates (receives percentage)
        complete_cb: Optional callback called when streaming is complete

    Yields:
        Chunks of file data as bytes

    Raises:
        ValueError: If the file doesn't exist or is not a valid file

    Example:
    ```python
    def progress(pct):
        print(f"Progress: {pct:.1f}%")

    for chunk in stream_file(Path("video.mp4"), progress_cb=progress):
        # Process chunk
        pass
    ```
    """
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
