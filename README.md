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

## فارسی

پایان‌نامه‌تان در Word است و دانشگاه یک الگوی Word داده. این پوشه فصل‌ها را به
متن ساده (کوارتو) می‌آورد و یک فایل Word واحد، در الگوی دانشگاه، با ارجاع‌های
زوترو و فهرست منابع تحویل می‌دهد. مراحل همان مراحل بالاست. برای پایان‌نامه‌ی
فارسی، در `_quarto.yml` دو خط `lang: fa` و `dir: rtl` را از حالت توضیح خارج
کنید. راهنمای کامل: [پایان‌نامه‌تان را با متن ساده بنویسید](https://www.collegica.org/software/markdown-thesis/fa/).
