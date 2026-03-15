"""Parses PDFs into structured sections using Docling."""

from dataclasses import dataclass
from pathlib import Path

from docling.document_converter import DocumentConverter
from config import SKIP_SECTIONS


@dataclass
class Section:
    """One logical section (or subsection) from a PDF."""
    section_name: str
    subsection_name: str | None
    text: str
    page_numbers: list[int]


@dataclass
class ParsedDocument:
    """Holds all the parsed sections from a single PDF."""
    filename: str
    paper_title: str
    sections: list[Section]


def parse_pdf(path: Path) -> ParsedDocument:
    """
    Convert a PDF file into a ParsedDocument with sections.
    Input: filepath of the PDF
    Output: ParsedDocument object
    """

    converter = DocumentConverter()
    doc = converter.convert(str(path)).document

    paper_title = ""
    sections = []

    # below variables are to track the current section
    section_name = ""
    subsection_name = None
    current_parts = []       # text pieces in the current section
    current_pages = set()    # page numbers seen for this section

    for item, level in doc.iterate_items():
        page_no = item.prov[0].page_no # fetch page number

        if item.label == "title": 
            if not paper_title:
                paper_title = item.text.strip()

        elif item.label == "section_header":
            # we hit a new section, so save whatever we collected for the previous one
            joined = "\n".join(current_parts).strip()
            if joined and section_name.strip().lower() not in SKIP_SECTIONS:
                sections.append(Section(section_name, subsection_name, joined, sorted(current_pages)))

            # level 1 = top-level section
            if level == 1:
                section_name = item.text.strip()
                subsection_name = None
                
            # any other level is assumed to be a subsection
            else:
                subsection_name = item.text.strip()

            # reset for the new section
            current_parts = []
            current_pages = {page_no}

        elif item.label in ["text", "paragraph", "list_item"]: # body text
            current_parts.append(item.text)
            current_pages.add(page_no)

        elif item.label == "table":
            table_md = item.export_to_markdown(doc)
            if table_md:
                current_parts.append(f"\n{table_md}\n")
                current_pages.add(page_no)

    # save the last section
    joined = "\n".join(current_parts).strip()
    if joined and section_name.strip().lower() not in SKIP_SECTIONS:
        sections.append(Section(section_name, subsection_name, joined, sorted(current_pages)))

    # falls back to filename if it couldn't find a title
    if not paper_title:
        paper_title = path.name

    return ParsedDocument(path.name, paper_title, sections)
