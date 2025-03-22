from os import mkdir as _mkdir
from os.path import exists as _exists

from ebook_extractor.prototype import Book as _Book


def save_as_images(book: _Book, folder: str) -> None:
    if not _exists(folder):
        _mkdir(folder)
    for page in book:
        page.to_pillow().save(f"{folder}/{page.page_number()}.png")
