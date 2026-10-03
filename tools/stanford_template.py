"""Build the Stanford reference document from Stanford's format rules.

    pixi run stanford            (main text double-spaced)
    pixi run stanford -- 1.5     (one-and-a-half spacing)

Stanford publishes rules rather than a template:
https://studentservices.stanford.edu/my-academics/earn-my-degree/graduate-degree-progress/dissertations-and-theses/prepare-your-work-0
This starts from pandoc's own reference document and applies them:

  letter paper; inner margin 1.5 in (left, single-sided), all others 1 in
  page numbers centred at the foot, half an inch from the edge
  Times New Roman 12 pt, black throughout (pandoc's headings are blue)
  main text double or one-and-a-half spaced; footnotes, quotations,
  tables, captions and the bibliography single-spaced
  each chapter on a new page, chapters numbered from 1

It writes universities/stanford/reference.docx and footer.txt (which footer
carries the page number). The front pages are written by front-pages.lua
from _quarto-stanford.yml.
"""

import subprocess
import sys
from io import BytesIO
from pathlib import Path

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "universities" / "stanford"
FONT = "Times New Roman"
SINGLE = ["Footnote Text", "Block Text", "Compact", "Image Caption", "Table Caption",
          "Captioned Figure", "Bibliography", "Figure", "Table"]


def pandoc_reference() -> Document:
    data = subprocess.run(["pandoc", "--print-default-data-file", "reference.docx"],
                          capture_output=True, check=True).stdout
    return Document(BytesIO(data))


def set_font(rpr) -> None:
    """Times New Roman in black, replacing theme fonts and colours."""
    fonts = rpr.find(qn("w:rFonts"))
    if fonts is None:
        fonts = OxmlElement("w:rFonts")
        rpr.insert(0, fonts)
    for attr in list(fonts.attrib):
        if attr.endswith("Theme"):
            del fonts.attrib[attr]
    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        fonts.set(qn(attr), FONT)
    for color in rpr.findall(qn("w:color")):
        rpr.remove(color)


def build(spacing: float) -> str:
    doc = pandoc_reference()
    styles = doc.styles

    # Document defaults, then every style: one font, black.
    defaults = styles.element.find(qn("w:docDefaults")).find(qn("w:rPrDefault")).find(qn("w:rPr"))
    set_font(defaults)
    for style in styles:
        if style.type in (WD_STYLE_TYPE.PARAGRAPH, WD_STYLE_TYPE.CHARACTER, WD_STYLE_TYPE.TABLE):
            set_font(style.element.get_or_add_rPr())

    styles["Normal"].font.size = Pt(12)
    for name in ["Body Text", "First Paragraph"]:
        styles[name].paragraph_format.line_spacing = spacing
    names = {s.name for s in styles}
    for name in SINGLE:
        if name in names:
            styles[name].paragraph_format.line_spacing = 1.0

    headings = {"Heading 1": (14, True, False), "Heading 2": (12, True, False), "Heading 3": (12, True, True)}
    for name, (size, bold, italic) in headings.items():
        s = styles[name]
        s.font.size, s.font.bold, s.font.italic = Pt(size), bold, italic
        s.paragraph_format.space_before, s.paragraph_format.space_after = Pt(18), Pt(12)
    styles["Heading 1"].paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    styles["Heading 1"].paragraph_format.page_break_before = True

    def add(name, align, bold=False, size=12, after=12, line=None):
        s = styles[name] if name in names else styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
        s.base_style = styles["Normal"]
        s.quick_style = True
        s.font.bold, s.font.size = bold, Pt(size)
        s.paragraph_format.alignment = align
        s.paragraph_format.space_before, s.paragraph_format.space_after = Pt(0), Pt(after)
        s.paragraph_format.line_spacing = line or 1.0

    # Front pages (front-pages.lua). The title page's lines are about 27 pt
    # apart, as in Stanford's specimen title pages.
    add("Title Page Line", WD_ALIGN_PARAGRAPH.CENTER, after=0, line=Pt(27))
    add("Front Heading", WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=14, after=18)

    section = doc.sections[0]
    section.page_width, section.page_height = Inches(8.5), Inches(11)
    section.left_margin = Inches(1.5)
    section.right_margin = section.top_margin = section.bottom_margin = Inches(1)
    section.header_distance = section.footer_distance = Inches(0.5)

    # A centred page number in the footer, counted from 1 in the chapters.
    section.footer.is_linked_to_previous = False
    paragraph = section.footer.paragraphs[0]
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    page = OxmlElement("w:fldSimple")
    page.set(qn("w:instr"), "PAGE")
    run = OxmlElement("w:r")
    text = OxmlElement("w:t")
    text.text = "1"
    run.append(text)
    page.append(run)
    paragraph._p.append(page)
    sect = section._sectPr
    numbering = sect.find(qn("w:pgNumType"))
    if numbering is None:
        numbering = OxmlElement("w:pgNumType")
        sect.append(numbering)
    numbering.set(qn("w:start"), "1")

    OUT.mkdir(parents=True, exist_ok=True)
    doc.save(OUT / "reference.docx")
    return sect.find(qn("w:footerReference")).get(qn("r:id"))


def main() -> None:
    spacing = 1.5 if "1.5" in sys.argv[1:] else 2.0
    rid = build(spacing)
    (OUT / "footer.txt").write_text(rid + "\n", encoding="utf-8")
    words = "one-and-a-half" if spacing == 1.5 else "double"
    print(f"universities/stanford/reference.docx: Stanford's format rules, {words}-spaced (page numbers in {rid})")
    print("Next: switch on the profile in _quarto.yml, fill in _quarto-stanford.yml, then `pixi run word`.")


if __name__ == "__main__":
    main()
