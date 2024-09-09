from book import Book, Chapter

book = Book(
    "Re:Zero - Starting life in another world - volume 1",
    chapters=[
        Chapter("Prologue", "The Waste Heat of the Beginning", 14, 15),
        Chapter("Chapter 1", "The End of the Beginning", 16, 76),
        Chapter("Chapter 2", "A Struggle Too Late", 77, 120),
        Chapter("Chapter 3", "Ending and Beginning", 121, 134),
        Chapter("Chapter 4", "Fourth Time's  the Charm", 135, 173),
        Chapter("Chapter 5", "Starting Life in Another World", 174, 214),
        Chapter("Epilogue", "The Moon Is Watching", 215, 223),
        Chapter("Afterword", None, 224, 229),
    ],
    source_path="./pdf/re-zero-vol-01.pdf",
    
)

book.save_audiobook('./output')
