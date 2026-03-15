# PDF Chunker

A section-aware parsing and chunking pipeline built for research publications.

This project processes academic PDFs, extracts structured sections, and intelligently divides them into smaller, semantically coherent blocks. Source provenance is preserved within each chunk, optimizing the output for Retrieval-Augmented Generation (RAG) systems.

<br>

## Architecture Overview

```text
PDF Documents  ->  Parser (Docling)  ->  Section Chunker  ->  JSONL Output
(data/pdfs/)                                                  (output/chunks.jsonl)
```

**Key Capabilities:**
* Understands document structure (titles, sections, body, tables).
* Excludes semantic noise (e.g., references, funding statements).
* Prevents cross-section chunking (chunks do not span across semantic boundaries).
* Injects provenance directly into text (`[Paper: Title] [Section: Name]`), so the source context remains visible to the retrieval model.

<br>

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository_url>
cd <repository_name>
```

### 2. Install Dependencies

This project relies on `uv` for fast dependency management.

```bash
uv sync
```

### 3. Run Pipeline

Place input PDFs inside `data/pdfs/`.

```bash
uv run python main.py
```

Results are generated at `output/chunks.jsonl`.

<br>

## Methodology & Decisions

### 1. Parsing Strategy
* **Considered:** PyMuPDF (plain text extraction) and `pdfplumber` (raw text/tables).
* **Selected:** Docling.
* **Why:** Unlike standard plain-text extractors, Docling inherently categorizes elements and preserves logical reading order. This provides robust heading detection out-of-the-box and saves us from writing custom heading detection logic.

### 2. Chunking Strategy
* **Considered:** Document-level chunking (treating the full PDF as one continuous string).
* **Selected:** Section-aware chunking.
* **Why:** Treating a PDF as a continuous string degrades retrieval. By first grouping text inside sections and chunking *within* isolated sections, distinct concepts (e.g., `Methods` vs. `Results`) are never merged. Chunk boundaries respect the document's natural narrative flow.

### 3. Sizing & Overlap
* **Target Size (2000 chars):** Chosen as a balanced middle point. It is large enough to keep useful context together for dense research paragraphs, yet small enough to avoid noisy, overly broad chunks that hurt precision.
* **Overlap (200 chars / 10%):** Small enough to limit text duplication, yet sufficient to maintain semantic continuity. If a concept spans across a chunk boundary, the overlap ensures the next chunk carries over relevant context.

<br>

## Target vs. Skipped Sections

This pipeline deliberately filters content to reduce retrieval noise.

This pipeline is mainly targeting:
* titles
* section headers
* body text
* list items
* tables

It is **not specifically targeting**:
* images
* figures as image content
* captions as a separate figure-understanding pipeline
* scanned PDFs that need strong OCR-first handling

So this is better for text-heavy research papers than image-heavy documents.

<br>

## Tradeoff Summary

| Decision | Why | Downside |
|---|---|---|
| Docling | better structure, headings, tables, reading order | slower, model download on first run |
| Section-aware chunking | cleaner chunks, no cross-section mixing | depends on section detection being good |
| 2000 char size | balanced context vs precision | still a fixed size |
| 10% overlap | better continuity across chunk boundaries | some duplicated text |
| Skip selected sections | less retrieval noise | some questions like funding/citations may not be answered |
| Context inside chunk text | source stays visible to retriever | slightly longer chunk text |

<br>

## Pipeline Structure

```text
├── data/pdfs/            # Directory for input PDFs
├── output/               # Directory for generated chunks
│   └── chunks.jsonl
├── pipeline/
│   ├── parser.py         # Parses PDF structure into distinct sections
│   └── chunker.py        # Splits extracted sections into granular chunks
├── config.py             # Centralized constants and settings
├── main.py               # Main execution script
├── Dockerfile
├── pyproject.toml
└── README.md
```

<br>

## Output Format

The output is formatted as JSON Lines (`.jsonl`), making it immediately ready for embedding models.

```json
{
  "chunk_id": "paper.pdf_chunk_0",
  "text": "Raw chunk text...",
  "contextualized_text": "[Paper: Title] [Section: Methods]\n\nRaw chunk text...",
  "source_pdf": "paper.pdf",
  "paper_title": "Title of the Paper",
  "section_name": "Methods",
  "subsection_name": null,
  "page_numbers": [3, 4],
  "chunk_index": 0,
  "char_count": 1847
}
```

<br>

## Assumptions & Limitations

* **Optimized for Text:** Designed primarily for text-heavy academic papers, not image-heavy or scanned documents requiring OCR.
* **Input Documents:** Input PDFs are structured as standard research-paper style documents.
* **Parser Accuracy:** Accuracy heavily relies on Docling's foundational structure detection and page provenance mapping.
* **Downstream Embedding:** The downstream embedding model performs well with chunks around this size.
