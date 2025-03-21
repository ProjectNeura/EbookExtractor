from abc import ABCMeta as _ABCMeta, abstractmethod as _abstractmethod
from typing import Iterator as _Iterator, Sequence as _Sequence, override as _override, overload as _overload, Any as _Any
from numpy import ndarray as _ndarray


class Page(object, metaclass=_ABCMeta):
    @_overload
    def __init__(self, *args, **kwargs) -> None:
        raise NotImplementedError

    def __init__(self, page_number: int) -> None:
        self._page_number: int = page_number

    def page_number(self) -> int:
        return self._page_number

    @_abstractmethod
    def to_image(self) -> _ndarray:
        raise NotImplementedError

    @_abstractmethod
    def to_text(self) -> str:
        raise NotImplementedError

    @_override
    def __str__(self) -> str:
        return self.to_text()


class Book(_Iterator, metaclass=_ABCMeta):
    @_overload
    def __init__(self, *args, **kwargs) -> None:
        raise NotImplementedError

    def __init__(self, from_page: int, to_page: int) -> None:
        self._from_page: int = from_page
        self._to_page: int = to_page

    @_abstractmethod
    def next_page(self) -> Page:
        raise NotImplementedError

    @_override
    def __next__(self) -> Page:
        return self.next_page()

    def __len__(self) -> int:
        return self._to_page - self._from_page + 1


class IndexedBook(Book, _Sequence, metaclass=_ABCMeta):
    @_overload
    def __init__(self, *args, **kwargs) -> None:
        raise NotImplementedError

    def __init__(self, from_page: int, to_page: int) -> None:
        super().__init__(from_page, to_page)
        self._pointer: int = from_page - 1

    @_override
    def next_page(self) -> Page:
        if self._pointer >= self._to_page:
            raise StopIteration
        self._pointer += 1
        return self.turn_to(self._pointer)

    @_abstractmethod
    def turn_to(self, page_number: int) -> Page:
        raise NotImplementedError

    @_override
    def __getitem__(self, page_number: int) -> Page:
        return self.turn_to(page_number)

    @_abstractmethod
    def pages(self) -> list[Page]:
        raise NotImplementedError
