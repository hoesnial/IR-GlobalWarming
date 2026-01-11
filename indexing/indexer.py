"""
Modul Indexing untuk Information Retrieval
Meliputi: Inverted Index, TF-IDF, dan Document Indexing
"""

import json
import math
import pickle
from collections import defaultdict
from typing import List, Dict, Tuple
import os
import sys

# Add parent directory to path untuk import preprocessing
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class InvertedIndex:
    """
    Class untuk membuat dan mengelola Inverted Index
    """
    
    def __init__(self):
        """Inisialisasi inverted index"""
        self.index = defaultdict(list)  # term -> [(doc_id, frequency), ...]
        self.documents = {}  # doc_id -> document
        self.doc_lengths = {}  # doc_id -> jumlah terms
        self.total_docs = 0
        
    def add_document(self, doc_id: int, tokens: List[str], document: Dict = None):
        """
        Menambahkan dokumen ke inverted index
        
        Args:
            doc_id: ID dokumen
            tokens: List of tokens dari dokumen
            document: Dictionary dokumen lengkap (opsional)
        """
        # Simpan dokumen
        if document:
            self.documents[doc_id] = document
        
        # Hitung frekuensi setiap term
        term_freq = defaultdict(int)
        for token in tokens:
            term_freq[token] += 1
        
        # Update inverted index
        for term, freq in term_freq.items():
            self.index[term].append((doc_id, freq))
        
        # Simpan panjang dokumen
        self.doc_lengths[doc_id] = len(tokens)
        self.total_docs += 1
    
    def get_postings(self, term: str) -> List[Tuple[int, int]]:
        """
        Mendapatkan posting list untuk sebuah term
        
        Args:
            term: Term yang dicari
            
        Returns:
            List of (doc_id, frequency) tuples
        """
        return self.index.get(term, [])
    
    def get_document_frequency(self, term: str) -> int:
        """
        Mendapatkan document frequency untuk sebuah term
        
        Args:
            term: Term yang dicari
            
        Returns:
            Jumlah dokumen yang mengandung term
        """
        return len(self.index.get(term, []))
    
    def save_index(self, filepath: str):
        """
        Menyimpan index ke file
        
        Args:
            filepath: Path untuk menyimpan index
        """
        index_data = {
            'index': dict(self.index),
            'documents': self.documents,
            'doc_lengths': self.doc_lengths,
            'total_docs': self.total_docs
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(index_data, f)
        
        print(f"Index berhasil disimpan ke {filepath}")
    
    def load_index(self, filepath: str):
        """
        Memuat index dari file
        
        Args:
            filepath: Path file index
        """
        with open(filepath, 'rb') as f:
            index_data = pickle.load(f)
        
        self.index = defaultdict(list, index_data['index'])
        self.documents = index_data['documents']
        self.doc_lengths = index_data['doc_lengths']
        self.total_docs = index_data['total_docs']
        
        print(f"Index berhasil dimuat dari {filepath}")
    
    def prune_terms(self, min_df: int = 2, max_df_ratio: float = 1.0) -> int:
        """
        Melakukan seleksi fitur: menghapus term yang jarang muncul (min_df)
        atau terlalu sering muncul (max_df_ratio) dalam corpus.
        
        Args:
            min_df: Hapus term yang muncul di kurang dari min_df dokumen
            max_df_ratio: Hapus term yang muncul di lebih dari ratio * total_doc
            
        Returns:
            Jumlah term yang dihapus
        """
        terms_to_remove = []
        
        for term, postings in self.index.items():
            df = len(postings)
            
            # Filter 1: Rare Term Removal (Sangat efektif mengurangi dimensi)
            if df < min_df:
                terms_to_remove.append(term)
                continue
                
            # Filter 2: Common Term Removal (Statistik Stopword)
            if self.total_docs > 0 and (df / self.total_docs) > max_df_ratio:
                terms_to_remove.append(term)
        
        # Hapus term dari index
        for term in terms_to_remove:
            del self.index[term]
            
        return len(terms_to_remove)
    
    def get_stats(self) -> Dict:
        """
        Mendapatkan statistik index
        
        Returns:
            Dictionary berisi statistik
        """
        return {
            'total_documents': self.total_docs,
            'total_terms': len(self.index),
            'avg_doc_length': sum(self.doc_lengths.values()) / max(self.total_docs, 1)
        }


class TFIDFCalculator:
    """
    Class untuk menghitung TF-IDF
    """
    
    def __init__(self, inverted_index: InvertedIndex):
        """
        Inisialisasi TF-IDF calculator
        
        Args:
            inverted_index: Objek InvertedIndex
        """
        self.index = inverted_index
        self.idf_cache = {}
    
    def calculate_tf(self, term_freq: int, doc_length: int, 
                    normalization: str = 'normalized') -> float:
        """
        Menghitung Term Frequency (TF)
        
        Args:
            term_freq: Frekuensi term dalam dokumen
            doc_length: Panjang dokumen (jumlah total terms)
            normalization: Jenis normalisasi ('normalized', 'log', 'raw')
            
        Returns:
            Nilai TF
        """
        if normalization == 'normalized':
            # TF dengan normalisasi panjang dokumen
            return term_freq / max(doc_length, 1)
        elif normalization == 'log':
            # Log normalization
            return 1 + math.log10(term_freq) if term_freq > 0 else 0
        else:  # raw
            return term_freq
    
    def calculate_idf(self, term: str) -> float:
        """
        Menghitung Inverse Document Frequency (IDF)
        
        Args:
            term: Term yang akan dihitung IDF-nya
            
        Returns:
            Nilai IDF
        """
        # Cek cache
        if term in self.idf_cache:
            return self.idf_cache[term]
        
        # Hitung IDF
        doc_freq = self.index.get_document_frequency(term)
        
        if doc_freq == 0:
            idf = 0
        else:
            # IDF = log(N / df)
            idf = math.log10(self.index.total_docs / doc_freq)
        
        # Simpan ke cache
        self.idf_cache[term] = idf
        
        return idf
    
    def calculate_tfidf(self, term: str, doc_id: int) -> float:
        """
        Menghitung TF-IDF untuk term dalam dokumen
        
        Args:
            term: Term
            doc_id: ID dokumen
            
        Returns:
            Nilai TF-IDF
        """
        # Dapatkan term frequency
        postings = self.index.get_postings(term)
        term_freq = 0
        
        for d_id, freq in postings:
            if d_id == doc_id:
                term_freq = freq
                break
        
        if term_freq == 0:
            return 0.0
        
        # Hitung TF
        doc_length = self.index.doc_lengths.get(doc_id, 1)
        tf = self.calculate_tf(term_freq, doc_length)
        
        # Hitung IDF
        idf = self.calculate_idf(term)
        
        # TF-IDF
        return tf * idf
    
    def calculate_document_vector(self, doc_id: int, terms: List[str] = None) -> Dict[str, float]:
        """
        Menghitung vector TF-IDF untuk dokumen
        
        Args:
            doc_id: ID dokumen
            terms: List of terms (jika None, gunakan semua terms di dokumen)
            
        Returns:
            Dictionary {term: tfidf_score}
        """
        vector = {}
        
        if terms is None:
            # Dapatkan semua terms dari dokumen
            terms = set()
            for term, postings in self.index.index.items():
                for d_id, _ in postings:
                    if d_id == doc_id:
                        terms.add(term)
                        break
        
        # Hitung TF-IDF untuk setiap term
        for term in terms:
            tfidf = self.calculate_tfidf(term, doc_id)
            if tfidf > 0:
                vector[term] = tfidf
        
        return vector
    
    def calculate_query_vector(self, query_terms: List[str]) -> Dict[str, float]:
        """
        Menghitung vector TF-IDF untuk query
        
        Args:
            query_terms: List of query terms
            
        Returns:
            Dictionary {term: tfidf_score}
        """
        vector = {}
        
        # Hitung term frequency dalam query
        term_freq = defaultdict(int)
        for term in query_terms:
            term_freq[term] += 1
        
        # Hitung TF-IDF untuk setiap unique term
        query_length = len(query_terms)
        
        for term, freq in term_freq.items():
            # TF untuk query
            tf = self.calculate_tf(freq, query_length)
            
            # IDF
            idf = self.calculate_idf(term)
            
            # TF-IDF
            vector[term] = tf * idf
        
        return vector


def build_index_from_documents(source_path: str, output_file: str = None, 
                             min_df: int = 2) -> InvertedIndex:
    """
    Membuat inverted index dari dokumen (file JSON atau direktori)
    
    Args:
        source_path: Path ke file JSON atau Direktori data
        output_file: Path untuk menyimpan index (opsional)
        min_df: Minimum document frequency untuk seleksi fitur
        
    Returns:
        Objek InvertedIndex
    """
    from preprocessing.text_processor import TextPreprocessor
    from indexing.document_loader import DocumentLoader
    import os
    
    # Load dokumen menggunakan DocumentLoader
    loader = DocumentLoader()
    
    if os.path.isdir(source_path):
        print(f"Scanning directory: {source_path}")
        documents = loader.load_from_directory(source_path)
    elif os.path.isfile(source_path) and source_path.endswith('.json'):
        documents = loader.load_json(source_path)
    else:
        print(f"Warning: {source_path} bukan direktori atau file JSON valid.")
        documents = []
    
    # Inisialisasi preprocessor dan index
    print("Menginisialisasi preprocessor...")
    preprocessor = TextPreprocessor()
    inverted_index = InvertedIndex()
    
    print(f"\nMemproses {len(documents)} dokumen...")
    print("Tip: Proses ini butuh waktu untuk dokumen banyak. Tunggu sebentar!\n")
    
    # Process setiap dokumen dengan progress indicator
    import time
    start_time = time.time()
    
    for i, doc in enumerate(documents, 1):
        doc_id = doc['id']
        
        # Progress indicator setiap 10 dokumen
        if i % 10 == 0 or i == 1:
            elapsed = time.time() - start_time
            avg_time = elapsed / i
            remaining = (len(documents) - i) * avg_time
            print(f"Progress: {i}/{len(documents)} dokumen ({i*100//len(documents)}%) - Estimasi sisa: {remaining:.1f}s")
        
        # Preprocess title dan content
        title_tokens = preprocessor.preprocess(doc['title'])
        content_tokens = preprocessor.preprocess(doc['content'])
        
        # Gabungkan tokens (title diberi bobot lebih)
        all_tokens = title_tokens * 2 + content_tokens  # title direplikasi 2x
        
        # Tambahkan ke index
        inverted_index.add_document(doc_id, all_tokens, doc)
    
    total_time = time.time() - start_time
    print(f"\n✓ Selesai memproses {len(documents)} dokumen dalam {total_time:.2f} detik")
    print(f"  Rata-rata: {total_time/len(documents):.2f} detik per dokumen")
    
    # --- SELEKSI FITUR (Feature Selection) ---
    print("\nMelakukan Seleksi Fitur (Feature Selection)...")
    initial_terms = len(inverted_index.index)
    
    # Hapus term yang muncul di kurang dari min_df dokumen
    removed_count = inverted_index.prune_terms(min_df=min_df)
    
    print(f"  - Total Terms Awal: {initial_terms}")
    print(f"  - Dihapus (muncul di < {min_df} dokumen): {removed_count}")
    print(f"  - Total Terms Akhir: {len(inverted_index.index)}")
    print(f"  - Reduksi Dimensi: {(removed_count/initial_terms)*100:.2f}%")
    
    # Statistik
    stats = inverted_index.get_stats()
    print("\nStatistik Index Akhir:")
    print(f"  Total dokumen: {stats['total_documents']}")
    print(f"  Total unique terms: {stats['total_terms']}")
    print(f"  Rata-rata panjang dokumen: {stats['avg_doc_length']:.2f}")
    
    # Simpan index jika output_file diberikan
    if output_file:
        inverted_index.save_index(output_file)
    
    return inverted_index


def main():
    """Function untuk testing"""
    print("="*80)
    print("Testing Inverted Index dan TF-IDF")
    print("="*80)
    
    # Build index
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.abspath(os.path.join(base_dir, '..', 'data'))
    docs_path = os.path.join(data_dir, 'documents.json')
    index_path = os.path.join(data_dir, 'inverted_index.pkl')
    
    if os.path.exists(docs_path):
        # Build index
        inv_index = build_index_from_documents(docs_path, index_path)
        
        # Test TF-IDF
        print("\n" + "="*80)
        print("Testing TF-IDF Calculator")
        print("="*80)
        
        tfidf_calc = TFIDFCalculator(inv_index)
        
        # Contoh query
        from preprocessing.text_processor import TextPreprocessor
        preprocessor = TextPreprocessor()
        
        query = "pemanasan global emisi karbon"
        query_tokens = preprocessor.preprocess(query)
        
        print(f"\nQuery: {query}")
        print(f"Query tokens: {query_tokens}")
        
        # Hitung query vector
        query_vector = tfidf_calc.calculate_query_vector(query_tokens)
        print(f"\nQuery TF-IDF vector:")
        for term, score in sorted(query_vector.items(), key=lambda x: x[1], reverse=True):
            print(f"  {term}: {score:.4f}")
        
        # Hitung document vector untuk dokumen pertama
        doc_vector = tfidf_calc.calculate_document_vector(1)
        print(f"\nDokumen 1 TF-IDF vector (top 10 terms):")
        for term, score in sorted(doc_vector.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {term}: {score:.4f}")
    
    else:
        print(f"File {docs_path} tidak ditemukan!")


if __name__ == "__main__":
    main()
