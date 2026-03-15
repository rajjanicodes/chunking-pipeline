"""Chunking pipeline to parse PDFs and save them chunks."""

from pipeline.parser import parse_pdf
from pipeline.chunker import chunk_document, save_chunks
from config import PDF_DIR, OUTPUT_PATH


def main():
    # grab all PDFs from the input folder
    pdf_files = sorted(PDF_DIR.glob("*.pdf"))
    if not pdf_files:
        print(f"No PDFs found in {PDF_DIR}")
        return

    print(f"Found {len(pdf_files)} PDFs to process\n")

    all_chunks = []
    for pdf_path in pdf_files:
        print(f"Parsing: {pdf_path.name}")

        # Step 1: convert PDF into structured sections
        doc = parse_pdf(pdf_path)
        print(f"  -> {len(doc.sections)} sections found")

        # Step 2: break sections into smaller chunks
        chunks = chunk_document(doc)
        print(f"  -> {len(chunks)} chunks created")
        all_chunks.extend(chunks)

    print(f"\nTotal chunks: {len(all_chunks)}")
    if all_chunks:
        avg = sum(len(c["text"]) for c in all_chunks) / len(all_chunks)
        print(f"Avg chunk size: {avg:.0f} chars")

    # Step 3: save all_chunks to a JSONL file
    save_chunks(all_chunks, OUTPUT_PATH)
    print(f"Saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
