"""Build the Concordia reference document from Concordia's official template.

    pixi run concordia

Run once, on your computer, before switching on the Concordia profile. It
downloads the School of Graduate Studies' thesis template from concordia.ca
(nothing of Concordia's is stored in this repository), keeps its styles, page
setup and page-number footer, and writes:

  universities/concordia/reference.docx   the styles your Word file gets
  universities/concordia/footer.txt       which footer carries the page number

Both degrees use the same styles and page setup; the front pages that differ
(doctoral or master's) are written by front-pages.lua from _quarto-concordia.yml.
"""

import re
import sys
import urllib.request
import zipfile
from io import BytesIO
from pathlib import Path

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Pt

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "universities" / "concordia"
SOURCE = "https://www.concordia.ca/content/dam/sgs/docs/resources/doctoral-thesis-template.doc"
PAGE = "https://www.concordia.ca/gradstudies/students/thesis-based/process.html"


def download() -> bytes:
    try:
        with urllib.request.urlopen(SOURCE, timeout=60) as r:
            data = r.read()
    except OSError as e:
        sys.exit(f"Couldn't download Concordia's template ({e}).\nCheck {PAGE} for its current address.")
    # Concordia names it .doc, but it is a Word 2007+ (.docx) file inside.
    if not zipfile.is_zipfile(BytesIO(data)) or "word/document.xml" not in zipfile.ZipFile(BytesIO(data)).namelist():
        sys.exit(f"The file at {SOURCE} isn't the Word template any more.\nCheck {PAGE}.")
    return data


def build(data: bytes) -> str:
    doc = Document(BytesIO(data))
    body = doc.element.body
    final = body.find(qn("w:sectPr"))  # the chapters' section: arabic numbering from 1
    footer = final.find(qn("w:footerReference")) if final is not None else None
    if footer is None:
        sys.exit("Concordia's template no longer has a page-number footer where expected; the Concordia profile needs updating.")
    for child in list(body):
        if child is not final:
            body.remove(child)

    styles = doc.styles
    names = {s.name for s in styles}

    def add(name, base="Normal", align=None, bold=None, size=None, after=None):
        s = styles[name] if name in names else styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
        s.base_style = styles[base]
        s.quick_style = True
        if align is not None:
            s.paragraph_format.alignment = align
        if bold is not None:
            s.font.bold = bold
        if size:
            s.font.size = Pt(size)
        if after is not None:
            s.paragraph_format.space_after = Pt(after)

    # The front pages (front-pages.lua).
    add("Front Centered", align=WD_ALIGN_PARAGRAPH.CENTER, after=12)
    add("Front Title", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=16, after=24)
    add("Front Heading", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=14, after=18)
    add("Front Text", align=WD_ALIGN_PARAGRAPH.LEFT, after=12)
    # Styles pandoc writes that Concordia's template doesn't define, so they
    # follow the template's own Normal and Caption.
    for name in ["Body Text", "First Paragraph", "Compact", "Captioned Figure", "Bibliography"]:
        if name not in names:
            add(name)
    for name in ["Image Caption", "Table Caption"]:
        if name not in names:
            add(name, base="Caption" if "Caption" in names else "Normal")
    # Each chapter on a new page.
    styles["Heading 1"].paragraph_format.page_break_before = True

    OUT.mkdir(parents=True, exist_ok=True)
    doc.save(OUT / "reference.docx")
    return footer.get(qn("r:id"))


def main() -> None:
    rid = build(download())
    (OUT / "footer.txt").write_text(rid + "\n", encoding="utf-8")
    print(f"universities/concordia/reference.docx: built from Concordia's template (page numbers in {rid})")
    print("Next: switch on the profile in _quarto.yml, fill in _quarto-concordia.yml, then `pixi run word`.")


if __name__ == "__main__":
    main()
