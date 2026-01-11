"""
Generator untuk membaca semua PDF di folder data dan menulis documents.json
dengan metadata (author, date, title) yang telah diekstrak.

Cara menjalankan:
    python tools/generate_documents_json.py
"""
import json
import sys
from pathlib import Path
from datetime import datetime

# Suppress PyPDF2 warnings
import warnings
warnings.filterwarnings('ignore')

try:
    from PyPDF2 import PdfReader
except ImportError:
    print("Error: PyPDF2 not found. Install with:")
    print("  pip install PyPDF2")
    sys.exit(1)

# Import extractor
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from extraction.metadata_extractor import extract_metadata

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
OUT_FILE = DATA_DIR / "documents.json"
BACKUP_FILE = DATA_DIR / f"documents.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

def build_entries():
    """Build entries dari semua PDF di folder data"""
    pdfs = sorted(DATA_DIR.glob("*.pdf"))
    if not pdfs:
        print(f"No PDF files found in {DATA_DIR}")
        return []
    
    entries = []
    print(f"\nMembaca {len(pdfs)} file PDF...\n")
    
    for idx, pdf in enumerate(pdfs, start=1):
        print(f"[{idx}/{len(pdfs)}] Processing: {pdf.name}")
        try:
            meta = extract_metadata(str(pdf))
            # Ambil konten untuk ringkasan
            content = meta.get('preview', "")
            if not content or len(content) < 50:
                # Coba ekstrak halaman pertama jika preview kurang
                try:
                    reader = PdfReader(str(pdf))
                    if reader.pages:
                        content = (reader.pages[0].extract_text() or "")[:1500]
                except Exception:
                    pass
            
            # Ambil judul dari nama file PDF
            title = pdf.stem.replace("_", " ").replace("-", " ")
            
            entry = {
                "id": idx,
                "title": title,
                "content": content or "Ringkasan tidak tersedia.",
                "author": meta.get('author') or "Unknown",
                "date": meta.get('date') or "",
                "category": "Pemanasan Global",
                "pdf_path": str(pdf.resolve()),
                "download": ""
            }
            entries.append(entry)
            print(f"  ✓ Title: {title[:80]}")
            print(f"  ✓ Author: {entry['author']}")
            print(f"  ✓ Date: {entry['date'] or '(not found)'}")
            print()
        except Exception as e:
            print(f"  ✗ Error: {e}\n")
    
    return entries

def main():
    """Main entry point"""
    if not DATA_DIR.exists():
        print(f"Error: Data folder not found: {DATA_DIR}")
        sys.exit(1)
    
    # Backup existing JSON
    if OUT_FILE.exists():
        try:
            OUT_FILE.rename(BACKUP_FILE)
            print(f"✓ Backup created: {BACKUP_FILE.name}\n")
        except Exception as e:
            print(f"Warning: Backup failed: {e}\n")
    
    # Build and write
    entries = build_entries()
    
    if not entries:
        print("No entries to write.")
        sys.exit(1)
    
    try:
        with open(OUT_FILE, "w", encoding="utf-8") as f:
            json.dump(entries, f, ensure_ascii=False, indent=4)
        print(f"\n✓ Wrote {len(entries)} entries to {OUT_FILE}")
        print(f"\nSekarang jalankan aplikasi dan klik 'Rebuild Index' untuk memperbarui index.")
    except Exception as e:
        print(f"Error writing file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
