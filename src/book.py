from parser import slugify
from dataclasses import dataclass
# from rich.progress import Progress
from threading import Thread
from reader import read_pdf
from parser import segmentParser
import time
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
        text = read_pdf(self.source_path, page_start=16, page_end=22)
        segmentParser(text)

        # logging.info("Turning chapters into audio file segments...")
