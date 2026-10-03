# Quarto thesis starter

Your chapters are in Word. Your university gave you a Word template. This
folder brings the chapters into plain text (Quarto) and gives you back one
Word file, in your template, with your Zotero citations and a bibliography.

From [Write Your Thesis in Plain Text](https://www.collegica.org/software/markdown-thesis/) on Collegica.

## Get it

- **On GitHub:** *Use this template* → *Create a new repository* (private is fine).
- **Without GitHub:** [download the ZIP](https://github.com/eLearningHub/quarto-thesis-starter/archive/refs/heads/main.zip) and unzip it.

## Try the example first

It comes with two example chapters (with Zotero citations, footnotes, a table
and an image) and an example template.

1. Install [pixi](https://pixi.sh), once:
   - Windows (PowerShell): `powershell -ExecutionPolicy Bypass -c "irm -useb https://pixi.sh/install.ps1 | iex"`
   - macOS: `curl -fsSL https://pixi.sh/install.sh | sh`
2. Open this folder in [Positron](https://positron.posit.co) (or any terminal
   in this folder) and run:

   ```
   pixi install
   pixi run import
   pixi run word
   ```

3. Open `_book/Archives-and-Their-Silences.docx`.

`pixi run import` will tell you that chapter 2 ends with a pasted
bibliography. Delete that section in `02-method.qmd` (your thesis makes its
own), then run `pixi run word` again.

## Then your own thesis

1. Delete the example files in `word/` and the `.qmd` chapters made from them.
2. Put your chapters in `word/`, named in order: `01-introduction.docx`,
   `02-literature.docx`, … Accept all tracked changes in Word first.
3. Replace `template.docx` with your university's template.
4. Set your title and name in `_quarto.yml`.
5. `pixi run import`, then `pixi run word`.

Or ask an AI assistant (Claude Code, Codex) to do it: `AGENTS.md` tells it the
rules, starting with *never change your wording*.

## A Concordia University thesis

The Concordia profile makes the thesis the way the School of Graduate
Studies' templates do, doctoral or master's: the title page and signature
page (counted i and ii, not numbered), the abstract and other front pages in
roman numerals from iii, a table of contents and lists of figures and tables,
and the chapters from 1.

1. `pixi run concordia`, once. It downloads Concordia's official template from
   concordia.ca and builds the styles from it on your computer.
2. In `_quarto.yml`, uncomment `profile:` and `default:`, with `concordia`.
3. In `_quarto-concordia.yml`, fill in your degree (`doctoral` or `masters`),
   title, department, committee, abstract and the optional pages.
4. `pixi run word`, then `pixi run pdf` for the PDF/A you submit.

Check the result against the [Thesis Preparation Guide](https://www.concordia.ca/content/dam/sgs/docs/handbooks/thesispreparationguide.pdf):
this starter follows Concordia's templates but isn't made or checked by
Concordia.

## A Stanford University dissertation

Stanford publishes [format rules](https://studentservices.stanford.edu/my-academics/earn-my-degree/graduate-degree-progress/dissertations-and-theses/prepare-your-work-0)
rather than a template. The Stanford profile follows them: the title page laid
out as Stanford's specimen pages (counts as i, not numbered), the abstract
and other front pages in roman numerals from iv (Axess adds the copyright
page ii and signature page iii itself, so your file must not contain them),
a table of contents and lists of tables and illustrations, chapters from 1;
a 1.5-inch inner margin and one inch elsewhere, Times New Roman 12 in black,
main text double-spaced.

1. `pixi run stanford`, once (`pixi run stanford -- 1.5` for one-and-a-half
   spacing).
2. In `_quarto.yml`, uncomment `profile:` and `default:`, with `stanford`.
3. In `_quarto-stanford.yml`, fill in your title, department or program,
   degree, name, month and year, abstract and the optional pages.
4. `pixi run word`, then `pixi run pdf`.

This follows Stanford's published rules but isn't made or checked by
Stanford; check the result against them before you submit.

## The PDF you submit

`pixi run pdf` turns the Word file into PDF/A, the archival PDF most
universities ask for, with the table of contents and lists filled in. It
needs [LibreOffice](https://www.libreoffice.org) (free), installed once.

## فارسی

پایان‌نامه‌تان در Word است و دانشگاه یک الگوی Word داده. این پوشه فصل‌ها را به
متن ساده (کوارتو) می‌آورد و یک فایل Word واحد، در الگوی دانشگاه، با ارجاع‌های
زوترو و فهرست منابع تحویل می‌دهد. مراحل همان مراحل بالاست. برای پایان‌نامه‌ی
فارسی، در `_quarto.yml` دو خط `lang: fa` و `dir: rtl` را از حالت توضیح خارج
کنید. راهنمای کامل: [پایان‌نامه‌تان را با متن ساده بنویسید](https://www.collegica.org/software/markdown-thesis/fa/).
