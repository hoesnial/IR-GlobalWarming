
import json
import os
import requests
import re
from urllib.parse import urlparse

class DocumentDownloader:
    """
    Class untuk mendownload dokumen PDF dari URL
    """
    
    def __init__(self, data_dir):
        """
        Inisialisasi DocumentDownloader
        
        Args:
            data_dir: Direktori tujuan penyimpanan file
        """
        self.data_dir = data_dir
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
    
    def get_filename_from_url(self, url):
        """Mendapatkan nama file dari URL"""
        a = urlparse(url)
        return os.path.basename(a.path)
    
    def clean_filename(self, title):
        """Membersihkan judul agar aman untuk nama file"""
        # Hapus karakter ilegal
        clean = re.sub(r'[\\/*?:"<>|]', "", title)
        # Batasi panjang
        clean = clean[:100]
        return clean.strip()
    
    def download_from_json(self, json_path, callback=None):
        """
        Mendownload dokumen berdasarkan file JSON
        
        Args:
            json_path: Path ke file JSON sumber
            callback: Function untuk progress update (message)
        
        Returns:
            Tuple (success_count, fail_count, skipped_count)
        """
        if not os.path.exists(json_path):
            if callback: callback(f"File {json_path} tidak ditemukan!")
            return 0, 0, 0
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                documents = json.load(f)
        except Exception as e:
            if callback: callback(f"Gagal membaca JSON: {e}")
            return 0, 0, 0
            
        success = 0
        fail = 0
        skipped = 0
        
        total = len(documents)
        if callback: callback(f"Memulai proses download untuk {total} dokumen...")
        
        for i, doc in enumerate(documents, 1):
            title = doc.get('title', f'Document {doc.get("id")}')
            url = doc.get('download', '')
            
            if not url or not url.startswith('http'):
                continue
                
            # Tentukan nama file
            # Prioritas 1: Judul dokumen (dibersihkan)
            # Prioritas 2: Nama file dari URL
            filename = self.clean_filename(title) + ".pdf"
            filepath = os.path.join(self.data_dir, filename)
            
            # Cek jika file sudah ada
            if os.path.exists(filepath):
                # if callback: callback(f"[{i}/{total}] SKIP: {filename} (sudah ada)")
                skipped += 1
                continue
            
            # Download
            try:
                if callback: callback(f"[{i}/{total}] Downloading: {filename}...")
                
                response = requests.get(url, stream=True, timeout=15)
                
                # Cek content type harus PDF atau binary
                content_type = response.headers.get('content-type', '').lower()
                
                if response.status_code == 200:
                    with open(filepath, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    success += 1
                else:
                    if callback: callback(f"  FAILED: Status {response.status_code}")
                    fail += 1
                    
            except Exception as e:
                if callback: callback(f"  ERROR: {str(e)}")
                fail += 1
                
        summary = f"Selesai! Sukses: {success}, Gagal: {fail}, Terlewati (Sudah Ada): {skipped}"
        if callback: callback(summary)
        
        return success, fail, skipped
