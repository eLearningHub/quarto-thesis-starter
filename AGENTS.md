# Instructions for an AI assistant working in this folder

This folder is someone's thesis. They are a researcher, not a programmer, and
they may write in English, Persian or another language. It is a Quarto book:
each chapter is a `.qmd` file (Markdown) beside `_quarto.yml`, the Word files
it came from are in `word/`, and `template.docx` is their university's Word
template.

## The rules

1. **Never change the author's wording.** Not to improve it, not to shorten
   it, not to fix grammar unless they ask for that sentence. Convert, arrange
   and check; don't write.
2. **Never overwrite a converted chapter.** Once `word/01-x.docx` is
   `01-x.qmd`, the `.qmd` is the chapter. `pixi run import` already refuses to
   overwrite; don't work around it.
3. **Report, don't hide.** After any change, tell them what you did and what
   you could not do, in plain words, in the language they wrote to you in.

## The tasks

| Command | What it does |
|---|---|
| `pixi install` | Once: installs Quarto and Pandoc for this folder only |
| `pixi run import` | Converts each `word/*.docx` to a chapter, gathers citations into `references.json`, updates the chapter list in `_quarto.yml` |
| `pixi run word` | The whole thesis as one Word file in `template.docx`, in `_book/` |
| `pixi run preview` | A live preview in the browser |
| `pixi run pdf` | The Word file as PDF/A, contents and lists filled in (needs LibreOffice) |
| `pixi run stanford` | Once, for a Stanford dissertation: builds `universities/stanford/reference.docx` from Stanford's format rules (`-- 1.5` for one-and-a-half spacing) |
| `pixi run concordia` | Once, for a Concordia thesis: builds `universities/concordia/reference.docx` from Concordia's official template |

## Moving their chapters in

1. They put their chapters in `word/`, named in order: `01-introduction.docx`,
   `02-literature.docx`, and so on, and their university's template as
   `template.docx` (replacing the example).
2. Run `pixi run import` and read its "To do" lines with them:
   - **tracked changes**: they accept or reject them in Word, then run it again;
   - **a pasted bibliography** at the end of a chapter: delete that section
     (show them first); Quarto makes the bibliography from the citations.
3. Check each chapter against its Word file: headings, footnotes, tables,
   images, and that every citation became `[@...]`. Citations typed by hand
   (not inserted with Zotero or Mendeley) stay as plain text: list them for
   the author; don't guess the source.
4. Set the title and author in `_quarto.yml`. For a right-to-left thesis
   (Persian, Arabic, Hebrew), uncomment `lang` and `dir` there.
5. Run `pixi run word` and tell them where the file is.

## A Concordia University thesis

1. `pixi run concordia` (downloads Concordia's template; never commit what it builds).
2. Uncomment `profile: default: concordia` in `_quarto.yml`.
3. Fill in `_quarto-concordia.yml` with the author: degree level (`doctoral` or
   `masters`), title, department, degree, date, committee, abstract, optional
   pages. Ask them for each value; don't invent names or dates.
4. `pixi run word`, then `pixi run pdf`. Check the page numbers with them:
   title and signature pages unnumbered, abstract iii, first chapter 1.

## A Stanford University dissertation

1. `pixi run stanford`; uncomment the profile in `_quarto.yml` with `stanford`.
2. Fill in `_quarto-stanford.yml` with the author: title, `submitted-to` (their
   department, program or school), degree, name, month and year of
   electronic submission, abstract, optional pages. Ask; don't invent.
3. `pixi run word`, then `pixi run pdf`. The file must not contain a copyright
   or signature page (Axess adds them): the abstract is page iv.

## Known limits, to say plainly

- The template gives the Word file its styles, margins, headers and page
  setup, **not its content**: a title page or declaration printed in the
  template doesn't appear. They add it to the final Word file.
- Citation keys come from Zotero's internal numbers (`@101`). They work. Rename
  them to readable keys only if asked, in both the chapters and
  `references.json`.
- Very complex tables may need redoing; tell them which.
