from PIL.Image import fromarray as _fromarray
from textwrap import wrap as _wrap
from fpdf import FPDF as _FPDF

from ebook_extractor.prototype import Book as _Book


def save_as_pdf(book: _Book, path: str, as_text: bool = False) -> None:
    if as_texts:
        text = "\n".join(page.to_text() for page in book)
        a4_width_mm = 210
        pt_to_mm = 0.35
        fontsize_pt = 10
        fontsize_mm = fontsize_pt * pt_to_mm
        margin_bottom_mm = 10
        character_width_mm = 7 * pt_to_mm
        width_text = int(a4_width_mm / character_width_mm)
        pdf = _FPDF(orientation="P", unit="mm", format="A4")
        pdf.set_auto_page_break(True, margin=margin_bottom_mm)
        pdf.add_page()
        pdf.set_font(family="Courier", size=fontsize_pt)
        splitted = text.split('\n')
        for line in splitted:
            lines = _wrap(line, width_text)
            if len(lines) == 0:
                pdf.ln()
            for wrap in lines:
                pdf.cell(0, fontsize_mm, wrap, ln=1)
        pdf.output(path, "F")
    else:
        images = []
        for page in book:
            images.append(_fromarray(page.to_image()))
        images[0].save(path, "PDF", resolution=100, save_all=True, append_images=images[1:])
