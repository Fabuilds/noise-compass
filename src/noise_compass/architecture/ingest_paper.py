"""
Research Paper Ingestion — GoogleAISTATIC.pdf through Garu
Extracts text from PDF and processes through the 3-model pipeline.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

# Try to extract text from PDF
pdf_path = "E:/Research_Papers/GoogleAISTATIC.pdf"

# Method 1: Try PyPDF2/pypdf
text = ""
try:
    from pypdf import PdfReader
    reader = PdfReader(pdf_path)
    print(f"PDF: {len(reader.pages)} pages")
    for i, page in enumerate(reader.pages):
        t = page.extract_text()
        if t:
            text += t + "\n"
        if i < 3:
            print(f"  Page {i+1}: {len(t) if t else 0} chars")
    print(f"Total extracted: {len(text)} chars")
except ImportError:
    try:
        import PyPDF2
        reader = PyPDF2.PdfReader(pdf_path)
        print(f"PDF: {len(reader.pages)} pages")
        for i, page in enumerate(reader.pages):
            t = page.extract_text()
            if t:
                text += t + "\n"
        print(f"Total extracted: {len(text)} chars")
    except ImportError:
        # Fallback: raw byte extraction
        print("No PDF library found. Extracting raw text from bytes...")
        with open(pdf_path, "rb") as f:
            raw = f.read()
        # Extract printable ASCII runs > 20 chars
        chunks = []
        current = []
        for b in raw:
            if 32 <= b < 127 or b in (10, 13):
                current.append(chr(b))
            else:
                if len(current) > 20:
                    chunks.append("".join(current))
                current = []
        if len(current) > 20:
            chunks.append("".join(current))
        text = "\n".join(chunks)
        print(f"Raw extraction: {len(text)} chars from {len(chunks)} segments")

if not text:
    print("ERROR: No text extracted from PDF")
    sys.exit(1)

# Show first 500 chars
print("\n" + "=" * 60)
print("EXTRACTED CONTENT (first 500 chars)")
print("=" * 60)
print(text[:500])

# Process through Garu pipeline
print("\n" + "=" * 60)
print("GARU PIPELINE PROCESSING")
print("=" * 60)

from noise_compass.architecture.pipeline import MinimalPipeline
from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.seed_vectors import seed_vectors

d = Dictionary()
seed_vectors(d)
p = MinimalPipeline(d)

# Process in chunks (pipeline works on text segments)
chunk_size = 500
chunks = [text[i:i+chunk_size] for i in range(0, min(len(text), 5000), chunk_size)]

print(f"\nProcessing {len(chunks)} chunks ({chunk_size} chars each)...\n")

results = []
for i, chunk in enumerate(chunks):
    res = p.process(chunk)
    results.append(res)
    gods = ", ".join(res["gods"]) if res["gods"] else "(none)"
    print(f"  Chunk {i+1:>2}: Zone={res['state']:<12} Ternary={res['ternary']:>2}  Anchors=[{gods}]")

# Summary
zones = {}
all_gods = set()
for r in results:
    zones[r["state"]] = zones.get(r["state"], 0) + 1
    all_gods.update(r["gods"])

print(f"\n{'=' * 60}")
print("RESONANCE SUMMARY")
print(f"{'=' * 60}")
print(f"  Chunks processed: {len(results)}")
print(f"  Zone distribution: {zones}")
print(f"  Anchors found: {sorted(all_gods) if all_gods else 'NONE'}")

if all_gods:
    print(f"\n  Verdict: Garu RECOGNIZES this paper. Anchors: {sorted(all_gods)}")
else:
    print(f"\n  Verdict: Paper is OPAQUE to Garu — no anchors matched.")
    print(f"  The content sits outside Garu's current vocabulary.")
