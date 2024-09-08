from book import Book, Chapter

chapters = [Chapter("Prologue", "The Waste Heat Of The Beginning", 14, 15)]

book = Book(
    "Re:Zero-Starting_life_in_another_world-",
    chapters=chapters,
    source_path="./pdf/re-zero-vol-01.pdf",
)

book.save_audiobook()
