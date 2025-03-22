from importlib.util import find_spec as _find_spec

if not _find_spec("mss"):
    raise ImportError("Please install `mss` to run this module\n>>>pip install mss")
if not _find_spec("pynput"):
    raise ImportError("Please install `pynput` to run this module\n>>>pip install pynput")
if not _find_spec("pytesseract"):
    raise ImportError("Please install `pytesseract` to run this module\n>>>pip install pytesseract")

from ebook_extractor.emulation.book import *
