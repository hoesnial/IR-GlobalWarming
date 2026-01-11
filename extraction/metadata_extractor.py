"""
Ekstrak metadata (author, date, title) dari PDF
"""
import re
from datetime import datetime
from typing import Optional, Dict
from PyPDF2 import PdfReader
from pathlib import Path

MONTHS_ID = {
    'januari': 1, 'februari': 2, 'maret': 3, 'april': 4, 'mei': 5, 'juni': 6,
    'juli': 7, 'agustus': 8, 'september': 9, 'oktober': 10, 'november': 11, 'desember': 12
}

def _parse_pdf_date(raw: Optional[str]) -> Optional[str]:
    """Parse tanggal dari metadata PDF format D:YYYYMMDDHHmmSS"""
    if not raw:
        return None
    # Format PDF: D:YYYYMMDDHHmmSS
    m = re.match(r'^D:(\d{4})(\d{2})?(\d{2})?', str(raw))
    if m:
        y = int(m.group(1))
        mo = int(m.group(2) or 1)
        d = int(m.group(3) or 1)
        return f"{y:04d}-{mo:02d}-{d:02d}"
    # Fallback ISO
    try:
        return datetime.fromisoformat(str(raw)).date().isoformat()
    except Exception:
        return None

def _find_author_in_text(text: str) -> Optional[str]:
    """Cari nama penulis dalam teks halaman awal"""
    if not text:
        return None
    patterns = [
        r'(?im)^\s*penulis\s*[:\-]\s*(.+)$',
        r'(?im)^\s*oleh\s+(.+)$',
        r'(?im)^\s*author\s*[:\-]\s*(.+)$',
    ]
    for pat in patterns:
        m = re.search(pat, text)
        if m:
            author = m.group(1).strip()
            author = re.split(r'[,;]|email:|universitas|faculty|department', author, flags=re.I)[0].strip()
            return author[:80]
    # Fallback: baris awal yang tampak seperti nama
    lines = [l.strip() for l in text.splitlines()[:25] if l.strip()]
    for l in lines:
        if 2 <= len(l.split()) <= 6 and re.match(r'^[A-Z][A-Za-z\.\- ]+$', l):
            return l[:80]
    return None

def _find_date_in_text(text: str) -> Optional[str]:
    """Cari tanggal/tahun dalam teks"""
    if not text:
        return None
    # dd/mm/yyyy atau dd-mm-yyyy
    m = re.search(r'(?i)\b(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})\b', text)
    if m:
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return f"{y:04d}-{mo:02d}-{d:02d}"
    # dd Month yyyy (Indonesia)
    m = re.search(r'(?i)\b(\d{1,2})\s+(januari|februari|maret|april|mei|juni|juli|agustus|september|oktober|november|desember)\s+(\d{4})\b', text)
    if m:
        d = int(m.group(1))
        mo = MONTHS_ID[m.group(2).lower()]
        y = int(m.group(3))
        return f"{y:04d}-{mo:02d}-{d:02d}"
    # Month yyyy
    m = re.search(r'(?i)\b(januari|februari|maret|april|mei|juni|juli|agustus|september|oktober|november|desember)\s+(\d{4})\b', text)
    if m:
        mo = MONTHS_ID[m.group(1).lower()]
        y = int(m.group(2))
        return f"{y:04d}-{mo:02d}-01"
    # Label "Tanggal:"
    m = re.search(r'(?im)^\s*tanggal\s*[:\-]\s*(.+)$', text)
    if m:
        return _find_date_in_text(m.group(1))
    # Ambil tahun yang berdiri sendiri (1980–2099)
    m = re.search(r'\b(19[8-9]\d|20\d{2})\b', text)
    if m:
        return f"{int(m.group(1)):04d}-01-01"
    return None

def _find_title(reader: PdfReader, pdf_stem: str) -> str:
    """Ekstrak atau infer judul dari PDF"""
    title = None
    try:
        meta = getattr(reader, 'metadata', None)
        if meta:
            title = getattr(meta, 'title', None) or meta.get('/Title')
    except Exception:
        pass
    if title and str(title).strip():
        return str(title).strip()
    # Fallback: baris paling atas yang panjangnya wajar
    try:
        first_text = (reader.pages[0].extract_text() or "")
        candidates = [l.strip() for l in first_text.splitlines() if l.strip()]
        for l in candidates[:10]:
            if 8 <= len(l) <= 150:
                return l
    except Exception:
        pass
    # Fallback: dari nama file
    return pdf_stem.replace('_', ' ').strip()

def extract_metadata(pdf_path: str, max_pages: int = 3) -> Dict[str, str]:
    """
    Ekstrak metadata (author, date, title, preview) dari PDF
    
    Args:
        pdf_path: Path ke file PDF
        max_pages: Jumlah halaman pertama yang di-scan
        
    Returns:
        Dict dengan keys: author, date, title, preview
    """
    author, date = None, None
    title = None
    text = ""
    try:
        reader = PdfReader(pdf_path)
        title = _find_title(reader, Path(pdf_path).stem)
        meta = getattr(reader, 'metadata', None)
        if meta:
            author = getattr(meta, 'author', None) or meta.get('/Author')
            date = _parse_pdf_date(getattr(meta, 'creation_date', None) or meta.get('/CreationDate')) \
                or _parse_pdf_date(getattr(meta, 'mod_date', None) or meta.get('/ModDate'))
        # Ekstrak teks dari halaman awal
        for page in reader.pages[:max_pages]:
            try:
                text += (page.extract_text() or "") + "\n"
            except Exception:
                continue
        author = author or _find_author_in_text(text)
        date = date or _find_date_in_text(text)
    except Exception:
        pass
    if author:
        author = re.sub(r'\s+', ' ', author).strip()
    return {
        'author': author or 'Unknown',
        'date': date or '',
        'title': title,
        'preview': text[:1500]
    }
