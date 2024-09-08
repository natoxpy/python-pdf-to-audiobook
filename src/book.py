from dataclasses import dataclass


@dataclass
class Chapter:
    title: str
    subtitle: str
    page_start: int
    page_end: int


@dataclass
class Book:
    title: str
    chapters: list[Chapter]
    source_path: str
