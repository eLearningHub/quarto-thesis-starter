"""CI check of what `pixi run word` (and `pixi run pdf`) made.

    python .github/scripts/check_output.py [concordia|stanford]
"""
import glob
import re
import sys
import zipfile

docx = glob.glob("_book/*.docx")
assert docx, "no Word file in _book/"
xml = zipfile.ZipFile(docx[0]).read("word/document.xml").decode()
print("Word file:", docx[0])

def sections():
    found = []
    for s in re.findall(r"<w:sectPr.*?</w:sectPr>", xml, re.S):
        fmt = re.search(r'w:fmt="(\w+)"', s)
        start = re.search(r'w:start="(\d+)"', s)
        left = re.search(r'w:left="(\d+)"', s)
        found.append((fmt.group(1) if fmt else "decimal", start.group(1) if start else None,
                      "footerReference" in s, left.group(1) if left else None))
    return found


if "concordia" in sys.argv[1:]:
    expected = [("lowerRoman", "1", False, "1440"), ("lowerRoman", "3", True, "1440"), ("decimal", "1", True, "1440")]
    assert sections() == expected, f"sections {sections()}, expected {expected}"
    for text in ["SCHOOL OF GRADUATE STUDIES", "Abstract", "Table of Contents"]:
        assert text in xml, f"front pages lack {text!r}"
    print("Concordia: title/signature unnumbered, front pages from iii, chapters from 1")

if "stanford" in sys.argv[1:]:
    expected = [("lowerRoman", "1", False, "2160"), ("lowerRoman", "4", True, "2160"), ("decimal", "1", True, "2160")]
    assert sections() == expected, f"sections {sections()}, expected {expected}"
    for text in ["AND THE COMMITTEE ON GRADUATE STUDIES", "Abstract", "Table of Contents", "List of Illustrations"]:
        assert text in xml, f"front pages lack {text!r}"
    print("Stanford: title page unnumbered, front pages from iv, chapters from 1, inner margin 1.5 in")

pdfs = glob.glob("_book/*.pdf")
if pdfs:
    data = open(pdfs[0], "rb").read()
    assert re.search(rb"pdfaid:part(>|=\")2", data), "PDF isn't marked PDF/A-2"
    print("PDF:", pdfs[0], "PDF/A-2")
