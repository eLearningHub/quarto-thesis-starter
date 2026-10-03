"""CI check of what `pixi run word` (and `pixi run pdf`) made.

    python .github/scripts/check_output.py [concordia]
"""
import glob
import re
import sys
import zipfile

docx = glob.glob("_book/*.docx")
assert docx, "no Word file in _book/"
xml = zipfile.ZipFile(docx[0]).read("word/document.xml").decode()
print("Word file:", docx[0])

if "concordia" in sys.argv[1:]:
    sections = re.findall(r"<w:sectPr.*?</w:sectPr>", xml, re.S)
    found = []
    for s in sections:
        fmt = re.search(r'w:fmt="(\w+)"', s)
        start = re.search(r'w:start="(\d+)"', s)
        found.append((fmt.group(1) if fmt else "decimal", start.group(1) if start else None, "footerReference" in s))
    expected = [("lowerRoman", "1", False), ("lowerRoman", "3", True), ("decimal", "1", True)]
    assert found == expected, f"sections {found}, expected {expected}"
    for text in ["SCHOOL OF GRADUATE STUDIES", "Abstract", "Table of Contents"]:
        assert text in xml, f"front pages lack {text!r}"
    print("Concordia sections: title/signature unnumbered, front pages from iii, chapters from 1")

pdfs = glob.glob("_book/*.pdf")
if pdfs:
    data = open(pdfs[0], "rb").read()
    assert re.search(rb"pdfaid:part(>|=\")2", data), "PDF isn't marked PDF/A-2"
    print("PDF:", pdfs[0], "PDF/A-2")
