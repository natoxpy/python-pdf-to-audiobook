from parser import slugify
from dataclasses import dataclass
from rich.progress import Progress
from rich.console import Console
from threading import Thread, Event
from reader import read_pdf
from gtts import gTTS
from parser import segmentParser, TextSegments
from pydub import AudioSegment
import codecs
import sys
import signal
import time
import logging
import os
import math
import json

console = Console()

# logging.basicConfig(
#     # filename="app.log",
#     encoding="utf-8",
#     filemode="a",
#     format="{asctime} - {levelname} - {message}",
#     style="{",
#     datefmt="%Y-%m-%d %H:%M",
#     level=logging.INFO,
# )


@dataclass
class Chapter:
    title: str
    subtitle: str
    page_start: int
    page_end: int


def separate_title(chapter: Chapter, segments: TextSegments):
    left = []

    if not chapter.subtitle:
        left.append(chapter.title)
        segments._txt[0] = (
            segments._txt[0].replace(f"{chapter.title.upper()}", "").strip()
        )
    else:
        left.append(chapter.title + ". " + chapter.subtitle)
        segments._txt[0] = (
            segments._txt[0]
            .replace(f"{chapter.title.upper()} {chapter.subtitle.upper()}", "")
            .strip()
        )

    return TextSegments(left + segments._txt)


def chuckify(arr: list[str], n: int):
    for i in range(0, len(arr), n):
        yield arr[i : i + n]


exist_event = Event()


class Segment:
    txt: list[str]
    offset: int
    finish: bool
    advance: int
    output_path: str

    def __init__(self, txt: list[str], offset: int, output_path: str):
        self.txt = txt
        self.offset = offset
        self.output_path = output_path
        self.finish = False
        self.advance = 0

    def __repr__(self) -> str:
        return f"<Segment txt_size={len(self.txt)} offset={self.offset} finished={self.finish}>"


def process_segments(segment: Segment):
    if not os.path.exists(segment.output_path):
        os.makedirs(segment.output_path)

    for i, txt in enumerate(segment.txt):
        a = 0
        while True:
            if exist_event.is_set():
                return

            try:
                file_path = os.path.join(
                    segment.output_path, f"chunk-{i + 1 + segment.offset}.mp3"
                )
                if os.path.exists(file_path):
                    try:
                        AudioSegment.from_file(file_path)
                        segment.advance = 1
                        break
                    except Exception as _:
                        os.remove(file_path)

                tts = gTTS(txt)

                tts.save(file_path)
                AudioSegment.from_file(file_path)

                segment.advance = 1
                # print(f'{i + 1 + chunk.offset} length {round(len(file) / 1000)}s')

                break
            except Exception as e:
                if a % 100 == 0:
                    print(f"{segment} is failing {e}")
                if a == 1000:
                    break

                a += 1
                logging.info(e)
                time.sleep(0.1)

    segment.finish = True


def signal_handling(sig, frame):
    exist_event.set()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handling)


def process_chapter(chapter: Chapter, threads: int, source_path: str, output_path: str):
    text = read_pdf(
        source_path,
        page_start=chapter.page_start,
        page_end=chapter.page_end,
    )

    output_path_chapter = os.path.join(
        output_path,
        slugify(chapter.title),
    )

    if not os.path.exists(output_path_chapter):
        os.makedirs(output_path_chapter)

    segments = separate_title(chapter, segmentParser(text))

    # Threads list
    tl = []

    segments_chunks = list(
        chuckify(segments._txt, math.floor(len(segments._txt) / threads))
    )
    # offset
    o = 0
    for segment_txt in segments_chunks:
        segment = Segment(segment_txt, o, os.path.join(output_path_chapter, "segments"))
        o += len(segment_txt)
        tl.append([segment, Thread(target=process_segments, args=(segment,))])

    console.log(f"Processing {chapter.title} with {len(segments_chunks)} threads")

    with Progress() as progress:
        # task progress
        tp = []
        for i, t in enumerate(tl):
            tp.append(
                [
                    progress.add_task(f" - Thread {i + 1}", total=len(t[0].txt)),
                    t[0],
                ]
            )
            t[1].deamon = True
            t[1].start()

        while True:
            e = []
            for t in tp:
                progress.update(t[0], advance=t[1].advance)
                t[1].advance = 0

                if not t[1].finish:
                    e.append(0)

            if len(e) == 0:
                break

            time.sleep(0.001)

    for t in tl:
        t[1].join()

    segments_list = segments._txt
    mapped = []
    chapter_audio = AudioSegment.empty()
    segments_dir = os.path.join(output_path_chapter, "segments")
    chapter_file_audio = os.path.join(output_path_chapter, "audio.mp3")

    with Progress() as progress:
        task = progress.add_task(" - Finishing", total=len(segments_list))

        if os.path.exists(chapter_file_audio):
            progress.update(task, advance=len(segments_list))
        else:
            for i, txt in enumerate(segments_list):
                progress.update(task, advance=1)
                audio = AudioSegment.from_file(
                    os.path.join(segments_dir, f"chunk-{i + 1}.mp3")
                )
                chapter_audio += audio
                mapped.append(
                    {"time": round(len(chapter_audio) / 1000, 3), "segment": txt}
                )

            with codecs.open(
                os.path.join(output_path_chapter, "segment-map.json"), "w", "utf-8"
            ) as f:
                json.dump(mapped, f, indent=4)

            chapter_audio.export(chapter_file_audio)

    console.log(f"Completed processing {chapter.title}")


@dataclass
class Book:
    title: str
    chapters: list[Chapter]
    source_path: str

    def save_audiobook(self, output_path: str = "./", delete_segments: bool = True):
        logging.info(f"Creating audiobook for {self.title} ")

        # Threads number
        threads = 15
        output_path = os.path.join(output_path, slugify(self.title))
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        logging.info(output_path)

        for chapter in self.chapters:
            process_chapter(chapter, threads, self.source_path, output_path)

        with Progress() as progress:
            task = progress.add_task("Final", total=len(self.chapters) + 1)
            audio = AudioSegment.empty()
            mapped = []
            offset = 0

            for chapter in self.chapters:
                output_path_chapter = os.path.join(
                    output_path,
                    slugify(chapter.title),
                )

                chapter_audio = AudioSegment.from_file(
                    os.path.join(output_path_chapter, "audio.mp3")
                )
                audio += chapter_audio

                with codecs.open(
                    os.path.join(
                        output_path_chapter,
                        "segment-map.json",
                    ),
                    "r",
                    "utf-8",
                ) as f:
                    chapter_map = json.load(f)

                    for item in chapter_map:
                        mapped.append(
                            {"time": offset + item["time"], "text": item["segment"]}
                        )
                offset = chapter_map[len(chapter_map) - 1]["time"]
                progress.update(task, advance=1)

            with codecs.open(
                os.path.join(
                    output_path,
                    "segment-map.json",
                ),
                "w",
                "utf-8",
            ) as f:
                json.dump(mapped, f, indent=4)

            audio.export(os.path.join(output_path, "audio.mp3"))
            progress.update(task, advance=1)
