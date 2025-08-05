#!/usr/bin/env python3
"""extract_pdf.py

A simple command-line utility to extract all text from a PDF and save it as
<filename>.txt in the same directory. Requires the third-party package
`pdfplumber`.

Usage
-----
    python extract_pdf.py /path/to/file.pdf

If pdfplumber is not installed, run:
    pip install pdfplumber

The script writes the extracted text using UTF-8 encoding. Pages that contain
no extractable text will be skipped silently.
"""
import sys
import pathlib
from typing import Iterable, Union

try:
    import pdfplumber
except ImportError as exc:
    sys.exit(
        "pdfplumber is not installed. Install it with `pip install pdfplumber` "
        "and retry."
    )


def extract_text(pdf_path: Union[str, pathlib.Path]) -> Iterable[str]:
    """Yield text of each page in *pdf_path* (UTF-8)."""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            yield text


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("Usage: python extract_pdf.py <file.pdf>")

    pdf_path = pathlib.Path(sys.argv[1]).expanduser().resolve()

    if not pdf_path.is_file():
        sys.exit(f"File not found: {pdf_path}")
    if pdf_path.suffix.lower() != ".pdf":
        sys.exit("Input file must have a .pdf extension")

    txt_path = pdf_path.with_suffix(".txt")

    try:
        with txt_path.open("w", encoding="utf-8") as out_file:
            for page_text in extract_text(pdf_path):
                out_file.write(page_text + "\n")
    except Exception as exc:
        sys.exit(f"Failed to write {txt_path}: {exc}")

    print(f"Text saved to {txt_path}")


if __name__ == "__main__":
    main()
