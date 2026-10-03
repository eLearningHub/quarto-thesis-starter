"""Bring Word chapters into this Quarto thesis.

    pixi run import

For every .docx in word/ (in file-name order) this writes a chapter file
beside _quarto.yml: word/01-archive.docx becomes 01-archive.qmd. Citations
inserted with Zotero or Mendeley become real citations, and the reference
data they carry is gathered into references.json. Images go to images/.

It never overwrites a chapter that already exists: once converted, the .qmd
is the chapter, and the Word file is only the record of where it came from.
To convert a chapter again, delete its .qmd first.

It changes no wording. What it can't fix, it reports: tracked changes that
were never accepted, and a bibliography pasted at the end of a chapter
(Quarto makes the bibliography; a pasted one would appear twice).
"""

import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORD = ROOT / "word"
REFS = ROOT / "references.json"
QUARTO = ROOT / "_quarto.yml"
SKIP = {"template.docx"}
BIB_HEADINGS = re.compile(
    r"^#+\s*(references|bibliography|works cited|sources|منابع|فهرست منابع|کتابنامه|کتاب‌نامه)\s*(\{.*\})?\s*$",
    re.IGNORECASE | re.MULTILINE,
)


def pandoc(*args: str) -> str:
    result = subprocess.run(["pandoc", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    if result.returncode != 0:
        sys.exit(f"pandoc failed: {result.stderr.strip()}")
    return result.stdout


def tracked_changes(docx: Path) -> bool:
    with zipfile.ZipFile(docx) as z:
        xml = z.read("word/document.xml").decode("utf-8", "ignore")
    return "<w:ins " in xml or "<w:del " in xml


def convert(docx: Path, target: Path) -> tuple[list, str]:
    """The chapter's text, and the references its citations carry."""
    text = pandoc(
        str(docx.relative_to(ROOT)), "--from", "docx+citations", "--to", "markdown",
        "--standalone", "--wrap=none", "--extract-media=images",
    )
    refs = []
    # The references travel in the YAML header; read them, then drop the header.
    header = re.match(r"\A---\n(.*?)\n---\n\n?", text, re.S)
    if header:
        tmp = target.with_suffix(".import.md")
        tmp.write_text(text, encoding="utf-8")
        try:
            refs = json.loads(pandoc(str(tmp.relative_to(ROOT)), "--from", "markdown", "--to", "csljson") or "[]")
        finally:
            tmp.unlink()
        text = text[header.end():]
    return refs, text


def update_chapter_list(stems: list[str]) -> None:
    config = QUARTO.read_text(encoding="utf-8")
    block = re.compile(r"(# chapters: start[^\n]*\n)(.*?)(\s*# chapters: end)", re.S)
    if not block.search(config):
        print("  _quarto.yml has no '# chapters: start/end' markers; add the chapters to it yourself.")
        return
    indent = re.search(r"\n(\s*)# chapters: start", config).group(1)
    listing = "".join(f"{indent}- {s}.qmd\n" for s in stems)
    QUARTO.write_text(block.sub(lambda m: m.group(1) + listing.rstrip("\n") + m.group(3), config), encoding="utf-8")


def main() -> None:
    chapters = sorted(p for p in WORD.glob("*.docx") if p.name not in SKIP and not p.name.startswith("~$"))
    if not chapters:
        sys.exit("No Word files in word/. Put your chapters there, named in order: 01-introduction.docx, 02-...")

    references = {str(r["id"]): r for r in json.loads(REFS.read_text(encoding="utf-8"))} if REFS.exists() else {}
    stems, notes = [], []
    for docx in chapters:
        target = ROOT / f"{docx.stem}.qmd"
        stems.append(docx.stem)
        if target.exists():
            print(f"  {target.name}: already converted, left as it is")
            continue
        if tracked_changes(docx):
            notes.append(f"{docx.name} has tracked changes that were never accepted. Accept or reject them in Word, then run this again.")
            stems.pop()
            continue
        refs, text = convert(docx, target)
        for r in refs:
            references[str(r["id"])] = r
        target.write_text(text, encoding="utf-8")
        cites = len(re.findall(r"\[@", text))
        notes_count = len(re.findall(r"^\[\^[^\]]+\]:", text, re.M))
        print(f"  {target.name}: {cites} citations, {notes_count} footnotes, {len(refs)} references")
        if BIB_HEADINGS.search(text):
            notes.append(f"{target.name} ends with a pasted bibliography. Delete that section: the thesis makes its own.")

    REFS.write_text(json.dumps(sorted(references.values(), key=lambda r: str(r["id"])), indent=1, ensure_ascii=False), encoding="utf-8")
    update_chapter_list(stems)
    print(f"  references.json: {len(references)} references")
    for n in notes:
        print(f"\nTo do: {n}")
    print("\nNext: pixi run word")


if __name__ == "__main__":
    main()
