from typing import override as _override, ContextManager as _ContextManager, Any as _Any
from time import sleep as _sleep

from pynput.keyboard import Controller as _Controller, Key as _Key
from numpy import ndarray as _ndarray, array as _array
from pytesseract import image_to_string as _image_to_string
from mss import mss as _mss
from mss.base import MSSBase as _MSSBase

from ebook_extractor.emulation.types import SupportedLanguage as _SupportedLanguage
from ebook_extractor.prototype import Book as _Book, Page as _Page, IndexedBook as _IndexedBook

_LANGUAGE_MAPPING: dict[str, str] = {
    "chinese_simplified": "chi_sim", "chinese_traditional": "chi_tra", "german": "deu", "english": "eng",
    "french": "fra", "italian": "ita", "japanese": "jpn", "latin": "lat"
}


class Page(_Page):
    def __init__(self, content: _ndarray, page_number: int) -> None:
        super().__init__(page_number)
        self._content: _ndarray = content

    @_override
    def to_image(self) -> _ndarray:
        return self._content

    @_override
    def to_text(self, language: _SupportedLanguage = "english") -> str:
        return _image_to_string(self._content, lang=_LANGUAGE_MAPPING[language])


class Book(_Book, _ContextManager):
    def __init__(self, from_page: int, to_page: int, location: tuple[int, int, int, int] = (0, 0, 720, 480),
                 page_turner: str | _Key = _Key.right) -> None:
        super().__init__(from_page, to_page)
        self._location: tuple[int, int, int, int] = location
        if isinstance(page_turner, str) and len(page_turner) != 1:
            raise ValueError("`page_turner` must be one single key")
        self._page_turner: str | _Key = page_turner
        self._keyboard: _Controller = _Controller()
        self._mss: _MSSBase = _mss()

    def close(self) -> None:
        self._mss.close()

    @_override
    def __exit__(self, exc_type: _Any, exc_val: _Any, exc_tb: _Any) -> None:
        self.close()

    def screenshot(self) -> _ndarray:
        return _array(self._mss.grab(dict(zip(("left", "top", "width", "height"), self._location))))

    @_override
    def next_page(self) -> Page:
        if self._from_page > self._to_page:
            raise StopIteration
        try:
            return Page(self.screenshot(), self._from_page)
        finally:
            self._keyboard.press(self._page_turner)
            self._keyboard.release(self._page_turner)
            self._from_page += 1


class IndexedBook(_IndexedBook):
    def __init__(self, book: Book) -> None:
        super().__init__(book._from_page, book._to_page)
        self._book: Book = book
        self._offset: int = self._from_page
        self._pages: list[Page] = []

    def process(self, time_interval: float = .5) -> None:
        for page in self._book:
            self._pages.append(page)
            _sleep(time_interval)

    @_override
    def turn_to(self, page_number: int) -> Page:
        return self._pages[page_number - self._offset]

    @_override
    def pages(self) -> list[Page]:
        return self._pages
