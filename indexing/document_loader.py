
import json
import os
from typing import List, Dict
import glob
from pypdf import PdfReader


class DocumentLoader:
    """
    Class untuk memuat dokumen dari berbagai format (JSON, TXT, PDF)
    """
    
    def __init__(self):
        """Inisialisasi DocumentLoader"""
        pass
    
    def load_json(self, filepath: str) -> List[Dict]:
        """
        Memuat dokumen dari file JSON format lama
        
        Args:
            filepath: Path file JSON
            
        Returns:
            List of documents
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                documents = json.load(f)
            print(f"Loaded {len(documents)} documents from JSON: {filepath}")
            return documents
        except Exception as e:
            print(f"Error loading JSON {filepath}: {e}")
            return []

    def load_txt(self, filepath: str) -> Dict:
        """
        Memuat dokumen dari file TXT
        
        Args:
            filepath: Path file TXT
            
        Returns:
            Document dictionary
        """
        try:
            filename = os.path.basename(filepath)
            title = os.path.splitext(filename)[0].replace('_', ' ').title()
            
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            return {
                'title': title,
                'content': content,
                'category': 'General',
                'author': 'Unknown',
                'date': 'Unknown',
                'source': filename
            }
        except Exception as e:
            print(f"Error loading TXT {filepath}: {e}")
            return None

    def clean_text(self, text: str) -> str:
        """
        Membersihkan teks dari whitespace berlebih dan karakter aneh
        """
        import re
        # Ganti multiple whitespace/newlines dengan satu spasi
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def load_pdf(self, filepath: str) -> Dict:
        """
        Memuat dokumen dari file PDF
        
        Args:
            filepath: Path file PDF
            
        Returns:
            Document dictionary
        """
        try:
            filename = os.path.basename(filepath)
            # Title guessing from filename
            title = os.path.splitext(filename)[0].replace('_', ' ').title()
            
            reader = PdfReader(filepath)
            content = ""
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    content += text + " "  # Use space instead of newline
            
            cleaned_content = self.clean_text(content)
            
            return {
                'title': title,
                'content': cleaned_content,
                'category': 'General',
                'author': 'Unknown',
                'date': 'Unknown',
                'source': filename
            }
        except Exception as e:
            print(f"Error loading PDF {filepath}: {e}")
            return None

    def load_from_directory(self, directory: str) -> List[Dict]:
        """
        Memindai direktori untuk semua jenis dokumen yang didukung
        Dengan Logika De-duplikasi (Merge JSON metadata + PDF content)
        """
        import re
        
        # Helper untuk normalisasi judul/filename agar bisa dicocokkan
        def normalize_name(name):
            # Bersihkan karakter ilegal dan samakan case untuk konsistensi
            cleaned = re.sub(r'[\\/*?:"<>|]', "", name)
            return cleaned.lower()[:100].strip()

        # 1. Load existing JSON documents
        # Prioritize documents.json if exists, ignore backups
        json_docs = []
        main_json = os.path.join(directory, "documents.json")
        
        if os.path.exists(main_json):
            print(f"Loading main metadata file: {main_json}")
            json_docs.extend(self.load_json(main_json))
        else:
            # Fallback: load all json but skip backups if possible
            json_files = glob.glob(os.path.join(directory, "*.json"))
            for json_file in json_files:
                if "backup" in os.path.basename(json_file).lower():
                    continue
                docs = self.load_json(json_file)
                json_docs.extend(docs)
            
        # Create lookup map based on 'clean filename' implied by title
        # Map: filename_no_ext -> doc_reference
        doc_map = {}
        for doc in json_docs:
            if 'title' in doc:
                clean_name = normalize_name(doc['title'])
                doc_map[clean_name] = doc
            
        # 2. Load PDF files and MERGE if exists
        pdf_files = glob.glob(os.path.join(directory, "*.pdf"))
        
        # List untuk PDF yang benar-benar baru (tidak ada di JSON)
        new_pdf_docs = []
        
        for pdf_file in pdf_files:
            # Load PDF Content
            pdf_doc = self.load_pdf(pdf_file)
            if not pdf_doc:
                continue
                
            # Cek apakah judul file ini cocok dengan salah satu dokumen di JSON
            filename_no_ext_raw = os.path.splitext(os.path.basename(pdf_file))[0]
            filename_no_ext = normalize_name(filename_no_ext_raw)
            
            # Coba match dengan filename normalized
            match_found = False
            if filename_no_ext in doc_map:
                match_found = True
                target_doc = doc_map[filename_no_ext]
            else:
                # Coba fuzzy match sederhana (contains)
                for map_name, doc_ref in doc_map.items():
                    if filename_no_ext in map_name or map_name in filename_no_ext:
                        # Asumsi match jika overlap string cukup panjang (>20 chars)
                        if len(filename_no_ext) > 20: 
                            match_found = True
                            target_doc = doc_ref
                            break
            
            if match_found:
                # MATCH FOUND! Merge content.
                # Kita prioritaskan konten PDF (full text) karena lebih lengkap
                # Tapi pertahankan metadata JSON (ID, Author, Date, dll)
                print(f"Merging PDF content into JSON metadata for: {filename_no_ext_raw}")
                target_doc['content'] = pdf_doc['content']
                target_doc['source_file'] = os.path.basename(pdf_file)
                target_doc['pdf_path'] = os.path.abspath(pdf_file)
            else:
                # No match, this is a standalone PDF
                # IMPORTANT: Only add if absolutely sure it's new.
                # For safety in this user case, we assume JSON is the source of truth.
                # Only add if REALLY no match.
                print(f"New PDF found (no metadata): {filename_no_ext_raw}")
                pdf_doc['source_file'] = os.path.basename(pdf_file)
                pdf_doc['pdf_path'] = os.path.abspath(pdf_file)
                new_pdf_docs.append(pdf_doc)
        
        # 3. Load TXT files (Asumsikan standalone)
        txt_docs = []
        txt_files = glob.glob(os.path.join(directory, "*.txt"))
        for txt_file in txt_files:
            if "stopword" in txt_file.lower() or "requirement" in txt_file.lower():
                continue
            doc = self.load_txt(txt_file)
            if doc:
                # Clean text for TXT too
                doc['content'] = self.clean_text(doc['content'])
                txt_docs.append(doc)
        
        # Gabungkan semua
        all_docs = json_docs + new_pdf_docs + txt_docs
        
        # Assign IDs uniquely for new docs
        max_id = 0
        for doc in all_docs:
            if 'id' in doc:
                max_id = max(max_id, doc['id'])
        
        processed_docs = []
        for doc in all_docs:
            if 'id' not in doc:
                max_id += 1
                doc['id'] = max_id
            processed_docs.append(doc)
            
        print(f"Total Combined Documents: {len(processed_docs)}")
        return processed_docs
