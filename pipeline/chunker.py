"""Splits parsed documents into smaller chunks."""

import json
from pathlib import Path

from pipeline.parser import ParsedDocument
from config import CHUNK_SIZE, OVERLAP


def clean_text(text):
    """Cleanup: Fixing hyphenation, extra whitespace, etc."""
    # Eg: 'mito-\n chondrial' OR 'mito-\nchondrial'  'mitochondrial"
    text = text.replace("-\n ", "").replace("-\n", "")

    # Eg: "hello\n\n\n\nworld" to "hello\n\nworld"
    while "\n\n\n" in text:
        text = text.replace("\n\n\n", "\n\n")

    # Eg: "hello  world" to "hello world"
    while "  " in text:
        text = text.replace("  ", " ")

    return text.strip()


def split_text(text, max_size, overlap=OVERLAP):
    """Split text into chunks under max_size chars, with 10% overlap.
    For each chunk, find the best break point (paragraph > line > space > hard chop).
    Then add overlap by carrying over the tail of each chunk into the next one.
    """
    if len(text) <= max_size: # skip splittng 
        return [text]

    # step 1: split into clean non-overlapping chunks first
    chunks = []
    while len(text) > max_size:
        # find the best place to cut
        cut = text.rfind("\n\n", 0, max_size)       # try paragraph break
        if cut == -1:
            cut = text.rfind("\n", 0, max_size)     # try line break
        if cut == -1:
            cut = text.rfind(" ", 0, max_size)      # try space
        if cut == -1:
            cut = max_size                           # max_size

        chunks.append(text[:cut].strip())
        text = text[cut:].strip()

    if text:
        chunks.append(text)

    # step 2: add overlap
    if overlap > 0 and len(chunks) > 1: #except the first chunk
        overlapped = [chunks[0]]
        for i in range(1, len(chunks)):
            # add the overlap chars of previous chunk to each chunk
            prev_tail = chunks[i - 1][-overlap:]
            overlapped.append(prev_tail + " " + chunks[i])
        chunks = overlapped

    return chunks


def chunk_document(doc, chunk_size=CHUNK_SIZE):
    """Take a ParsedDocument and return a list of chunk dicts."""
    chunks = []

    for section in doc.sections:
        cleaned = clean_text(section.text)
        if not cleaned:
            continue

        pieces = split_text(cleaned, chunk_size)

        for piece in pieces:
            piece = piece.strip()

            # merging section and subsection names for the chunk
            sec_label = section.section_name or "Unknown Section"
            if section.subsection_name:
                sec_label += f" - {section.subsection_name}"
            header = f"[Paper: {doc.paper_title}] [Section: {sec_label}]"

            # unique id for this chunk
            chunk_id = f"{doc.filename}_chunk_{len(chunks)}"

            chunks.append({
                "chunk_id": chunk_id,
                "text": piece,
                "contextualized_text": f"{header}\n\n{piece}",
                "source_pdf": doc.filename,
                "paper_title": doc.paper_title,
                "section_name": section.section_name,
                "subsection_name": section.subsection_name,
                "page_numbers": section.page_numbers,
                "chunk_index": len(chunks),
                "char_count": len(piece),
            })

    return chunks


def save_chunks(chunks, output_path):
    """Dump all chunks to a JSONL file."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        for chunk in chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")
