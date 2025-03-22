from threading import Thread as _Thread
from time import sleep as _sleep
from tkinter import Event as _Event

from customtkinter import CTk as _CTk, StringVar as _StringVar, CTkLabel as _CTkLabel, CTkEntry as _CTkEntry, \
    CTkOptionMenu as _CTkOptionMenu, CTkToplevel as _CTkToplevel, CTkCanvas as _CTkCanvas
from pynput.keyboard import GlobalHotKeys as _GlobalHotKeys, Key as _Key

from ebook_extractor import save_as_pdf as _save_as_pdf, save_as_images as _save_as_images
from ebook_extractor.emulation import Book as _Book


def page_number_validation(d: str) -> bool:
    if d == "":
        return True
    try:
        return (n := int(d)) == float(d) and 0 < n < 10000
    except ValueError:
        return False


class Region(object):
    def __init__(self) -> None:
        self.is_selecting: bool = False
        self._x0: int = 0
        self._y0: int = 0
        self._x1: int = 0
        self._y1: int = 0
        self._origin: bool = False
        self._destination: bool = False

    def set_origin(self, x: int, y: int) -> None:
        self._x0, self._y0 = x, y
        self._origin = True

    def set_destination(self, x: int, y: int) -> None:
        self._x1, self._y1 = x, y
        self._destination = True

    def ready(self) -> bool:
        return self._origin and self._destination and not self.is_selecting

    def normalize(self) -> tuple[int, int, int, int]:
        x0, y0, x1, y1 = self._x0, self._y0, self._x1, self._y1
        if x0 > x1:
            x0, x1 = x1, x0
        if y0 > y1:
            y0, y1 = y1, y0
        return x0, y0, x1, y1

    def convert(self) -> tuple[int, int, int, int]:
        x0, y0, x1, y1 = self.normalize()
        return x0, y0, x1 - x0, y1 - y0

    def size(self) -> tuple[int, int]:
        return abs(self._x1 - self._x0), abs(self._y1 - self._y0)


class EbookTerminator(object):
    def __init__(self, padx: int = 4, pady: int = 2) -> None:
        self._px: int = padx
        self._py: int = pady
        self._root: _CTk = _CTk()
        self._root.title("Ebook Extractor")
        self._root.geometry("580x80")
        self._root.resizable(False, False)
        self._from_page: _StringVar = _StringVar(self._root, "1")
        self._to_page: _StringVar = _StringVar(self._root, "2")
        self._format: _StringVar = _StringVar(self._root, "PDF")
        self._page_turner: _StringVar = _StringVar(self._root, "<➡>")
        self._path: _StringVar = _StringVar(self._root, "output.pdf")
        self._instruction: _StringVar = _StringVar(self._root, "Press <shift>+<f4> to continue")
        self._region: Region = Region()
        self._extraction_thread = _Thread(target=self.extract, daemon=True)

    def select_region(self) -> None:
        self._instruction.set("Click to start selection")
        dialog = _CTkToplevel(self._root)
        dialog.overrideredirect(True)
        dialog.attributes("-top", True)
        dialog.attributes("-alpha", .25)
        width, height = dialog.winfo_screenwidth(), dialog.winfo_screenheight()
        dialog.geometry(f"{width}x{height}+0+0")
        canvas = _CTkCanvas(dialog, width=width, height=height)
        canvas.pack()

        def set_origin(e: _Event) -> None:
            x, y = e.x, e.y
            self._region.set_origin(x, y)
            self._region.is_selecting = True
            canvas.delete("area", "text0", "text1")
            canvas.create_text(x, y - 10, text=f"({x}, {y})", tags="text0")

        def set_destination(e: _Event) -> None:
            if not self._region.is_selecting:
                return
            x, y = e.x, e.y
            self._region.set_destination(x, y)
            canvas.delete("area", "text1")
            canvas.create_rectangle(self._region.normalize(), fill="white", tags="area")
            size = self._region.size()
            canvas.create_text(x, y + 10, text=f"{size[0]}x{size[1]}", tags="text1")

        def release_destination(_) -> None:
            self._region.is_selecting = False

        def confirm(_) -> None:
            if not self._region.ready():
                return
            dialog.unbind("<Button-1>")
            dialog.unbind("<Motion>")
            dialog.unbind("<ButtonRelease-1>")
            dialog.unbind("<KeyPress-Return>")
            dialog.destroy()
            key = {"<➡>": _Key.right, "<space>": _Key.space, "<enter>": _Key.enter}[self._page_turner.get()]
            _Thread(target=self.extract, args=(_Book(int(self._from_page.get()), int(self._to_page.get()),
                                                     self._region.convert(), key),), daemon=True).start()

        dialog.bind("<Button-1>", set_origin)
        dialog.bind("<Motion>", set_destination)
        dialog.bind("<ButtonRelease-1>", release_destination)
        dialog.bind("<KeyPress-Return>", confirm)

    def extract(self, book: _Book) -> None:
        self._instruction.set("Click on your ebook application to yield focus (3)")
        _sleep(1)
        self._instruction.set("Click on your ebook application to yield focus (2)")
        _sleep(1)
        self._instruction.set("Click on your ebook application to yield focus (1)")
        _sleep(1)
        self._instruction.set("Exporting...")
        match self._format.get():
            case "PDF":
                _save_as_pdf(book, self._path.get())
            case "Text PDF":
                _save_as_pdf(book, self._path.get(), True)
            case "Images":
                _save_as_images(book, self._path.get())
        book.close()
        self._instruction.set(f"File saved at {self._path.get()}")
        _sleep(1)
        self._root.destroy()

    def run(self) -> None:
        from_page_label = _CTkLabel(self._root, text="From Page")
        from_page_entry = _CTkEntry(self._root, width=48, textvariable=self._from_page, justify="center",
                                    validate="all",
                                    validatecommand=(self._root.register(page_number_validation), "%P"))
        to_page_label = _CTkLabel(self._root, text="To Page")
        to_page_entry = _CTkEntry(self._root, width=48, textvariable=self._to_page, justify="center", validate="all",
                                  validatecommand=(self._root.register(page_number_validation), "%P"))
        save_as_label = _CTkLabel(self._root, text="Save As")
        save_as_option = _CTkOptionMenu(self._root, width=96, variable=self._format,
                                        values=["PDF", "Text PDF", "Images"])
        page_turner_option = _CTkOptionMenu(self._root, variable=self._page_turner,
                                            values=["<➡>", "<space>", "<enter>"])
        save_as_entry = _CTkEntry(self._root, width=96, textvariable=self._path, justify="center")
        instruction_label = _CTkLabel(self._root, textvariable=self._instruction)
        from_page_label.grid(row=0, column=0, sticky="NSEW", ipadx=self._px, ipady=self._py, padx=self._px,
                             pady=self._py)
        from_page_entry.grid(row=0, column=1, sticky="NSEW", ipadx=self._px, ipady=self._py, padx=self._px,
                             pady=self._py)
        to_page_label.grid(row=0, column=2, sticky="NSEW", ipadx=self._px, ipady=self._py, padx=self._px, pady=self._py)
        to_page_entry.grid(row=0, column=3, sticky="NSEW", ipadx=self._px, ipady=self._py, padx=self._px, pady=self._py)
        save_as_label.grid(row=0, column=4, sticky="NSEW", ipadx=self._px, ipady=self._py, padx=self._px, pady=self._py)
        save_as_option.grid(row=0, column=5, sticky="NSEW", ipadx=self._px, ipady=self._py, padx=self._px,
                            pady=self._py)
        page_turner_option.grid(row=0, column=6, sticky="NSEW", ipadx=self._px, ipady=self._py, padx=self._px,
                                pady=self._py)
        save_as_entry.grid(row=1, column=0, columnspan=2, sticky="NSEW", ipadx=self._px, ipady=self._py, padx=self._px,
                           pady=self._py)
        instruction_label.grid(row=1, column=2, columnspan=5, sticky="NSEW", ipadx=self._px, ipady=self._py,
                               padx=self._px, pady=self._py)
        _GlobalHotKeys({
            "<shift>+<f4>": self.select_region,
            "<esc>": self._root.destroy
        }).start()
        self._root.mainloop()


def __entry__() -> None:
    EbookTerminator().run()
