from importlib.util import find_spec as _find_spec

if not _find_spec("customtkinter"):
    raise ImportError("Please install `customtkinter` to run this module\n>>>pip install customtkinter")

from ebook_extractor_cli.__entry__ import __entry__
