from rich.console import Console
import unicodedata
import re

console = Console()


def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = (
            unicodedata.normalize("NFKD", value)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s]+", "-", value).strip("-_")


class TextSegments:
    _txt: list[str]

    def __init__(self, txt: list[str]) -> None:
        self._txt = txt

    def __repr__(self) -> str:
        return f"<TextSegments size={len(self._txt)}>"


def split(text: list[str], delimiter: str):
    c = []
    for t in text:
        ts = t.split(delimiter)
        a = [
            a.strip() if i == len(ts) - 1 else a.strip() + delimiter
            for i, a in enumerate(ts)
        ]
        c += a

    return c


def multisplit(text: str, delimiter: list[str]):
    c = [text]
    for d in delimiter:
        c = split(c, d)

    if c[-1] == "":
        c = c[:-1]

    return c


def segmentParser(text: str):
    segments = multisplit(text, ["…”", "?”", "!”", "."])
    console.log(segments)
    # return TextSegments(["Hello", "world"])
