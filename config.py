"""All configurable settings in one place."""

from pathlib import Path

# --- paths ---
PDF_DIR = Path("data/pdfs")
OUTPUT_PATH = Path("output/chunks.jsonl")

# --- chunker ---
CHUNK_SIZE = 2000      # ~512 tokens per chunk
OVERLAP = 200          # 10% overlap for semantic continuity

# --- parser ---
SKIP_SECTIONS = [
    "references", "acknowledgements", "acknowledgment",
    "author contributions", "competing interests",
    "additional files", "supplementary",
    "abbreviations", "declarations", "funding",
    "availability of data",
] # these are the commo section names I assumed to be not useful in the downstream task
