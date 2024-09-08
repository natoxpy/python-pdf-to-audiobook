class TextSegments:
    _txt: list[str]

    def __init__(self, txt: list[str]) -> None:
        self._txt = txt

    def __repr__(self) -> str:
        return f"<TextSegments size={len(self._txt)}>"


def segmentParser(text: str):
    return TextSegments(["Hello", "world"])
