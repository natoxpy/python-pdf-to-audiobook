import pymupdf
import re


def read_pdf(file: str, page_start: int = 0, page_end: int = None):
    doc = pymupdf.open(file)
    content = ""

    if not page_end:
        page_end = len(doc)

    for i in range(page_start, page_end + 1):
        content = content + " " + doc[i - 1].get_text()

    return " ".join(re.split("\s+", content, flags=re.UNICODE)).strip()
