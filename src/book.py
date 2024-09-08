from parser import slugify
from dataclasses import dataclass
import logging
import os

logging.basicConfig(
    # filename="app.log",
    encoding="utf-8",
    filemode="a",
    format="{asctime} - {levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M",
    level=logging.DEBUG,
)


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

    def save_audiobook(self, dir: str = "./", delete_segments: bool = True):
        logging.info(f"Creating audiobook for {self.title}")
        root_path = os.path.join(dir, slugify(self.title))
        print(root_path)
