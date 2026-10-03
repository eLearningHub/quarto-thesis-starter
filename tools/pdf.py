"""The thesis as PDF/A, from the Word file `pixi run word` made.

    pixi run pdf

Uses LibreOffice (free; install it once from libreoffice.org). It opens the
Word file, fills in the table of contents and the lists of figures and tables
(Word leaves those for the reader to update), and exports PDF/A-2b, the
archival PDF universities such as Concordia ask for.

LibreOffice is driven by a small macro in a throwaway profile, so nothing in
your own LibreOffice settings is touched.
"""

import glob
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOOK = ROOT / "_book"

MACRO = """Sub ExportPdfA(src As String, dst As String)
  Dim load(0) As New com.sun.star.beans.PropertyValue
  load(0).Name = "Hidden" : load(0).Value = True
  doc = StarDesktop.loadComponentFromURL(ConvertToURL(src), "_blank", 0, load())
  ' Twice: filling the contents moves pages, and the second pass gets the numbers right.
  For pass = 1 To 2
    indexes = doc.getDocumentIndexes()
    For i = 0 To indexes.getCount() - 1
      indexes.getByIndex(i).update()
    Next i
    doc.getTextFields().refresh()
  Next pass
  Dim pdf(0) As New com.sun.star.beans.PropertyValue
  pdf(0).Name = "SelectPdfVersion" : pdf(0).Value = 2
  Dim export(1) As New com.sun.star.beans.PropertyValue
  export(0).Name = "FilterName" : export(0).Value = "writer_pdf_Export"
  export(1).Name = "FilterData" : export(1).Value = pdf()
  doc.storeToURL(ConvertToURL(dst), export())
  doc.close(True)
End Sub
"""

DTD = '<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE {kind} PUBLIC "-//OpenOffice.org//DTD OfficeDocument 1.0//EN" "{dtd}">\n'


def soffice() -> str:
    found = shutil.which("soffice") or shutil.which("libreoffice")
    if found:
        return found
    candidates = {
        "Darwin": ["/Applications/LibreOffice.app/Contents/MacOS/soffice"],
        "Windows": [r"C:\Program Files\LibreOffice\program\soffice.exe",
                    r"C:\Program Files (x86)\LibreOffice\program\soffice.exe"],
    }.get(platform.system(), ["/usr/bin/soffice", "/usr/lib/libreoffice/program/soffice"])
    for c in candidates:
        if os.path.exists(c):
            return c
    sys.exit("LibreOffice isn't installed. Install it from https://www.libreoffice.org, then run this again.")


def profile_with_macro(base: Path, office: str) -> Path:
    """A fresh LibreOffice profile whose Standard library holds MACRO.

    LibreOffice builds a new profile on its first start, so let it, then
    replace the empty Module1 it made with MACRO."""
    subprocess.run([office, "--headless", "--norestore", "--terminate_after_init",
                    f"-env:UserInstallation={base.as_uri()}"], capture_output=True, timeout=300)
    module = base / "user" / "basic" / "Standard" / "Module1.xba"
    if not module.exists():
        sys.exit("LibreOffice didn't set up its profile; is it installed correctly?")
    escaped = MACRO.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    module.write_text(
        DTD.format(kind="script:module", dtd="module.dtd")
        + '<script:module xmlns:script="http://openoffice.org/2000/script" script:name="Module1" script:language="StarBasic">'
        + escaped + "</script:module>\n", encoding="utf-8")
    return base


def main() -> None:
    sources = sorted(glob.glob(str(BOOK / "*.docx")))
    if not sources:
        sys.exit("No Word file in _book/. Run `pixi run word` first.")
    src = Path(sources[0])
    dst = src.with_suffix(".pdf")
    with tempfile.TemporaryDirectory() as tmp:
        office = soffice()
        profile = profile_with_macro(Path(tmp), office)
        macro = f'macro:///Standard.Module1.ExportPdfA("{src}","{dst}")'
        result = subprocess.run(
            [office, "--headless", "--norestore", "--nologo",
             f"-env:UserInstallation={profile.as_uri()}", macro],
            capture_output=True, text=True, timeout=600)
    if not dst.exists():
        sys.exit(f"LibreOffice didn't make the PDF.\n{result.stdout}{result.stderr}")
    print(f"{dst.relative_to(ROOT)}: PDF/A-2b, contents and lists filled in")


if __name__ == "__main__":
    main()
