from secrets import choice, SystemRandom


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
