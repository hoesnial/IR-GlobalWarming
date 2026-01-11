"""
Modul Preprocessing untuk Text Processing
Meliputi: tokenisasi, case folding, stopword removal, dan stemming
"""

import re
import json
from typing import List, Dict
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory


class TextPreprocessor:
    """
    Class untuk melakukan preprocessing teks bahasa Indonesia
    """
    
    def __init__(self):
        """Inisialisasi stemmer dan stopword remover"""
        # Inisialisasi Sastrawi stemmer
        stemmer_factory = StemmerFactory()
        self.stemmer = stemmer_factory.create_stemmer()
        
        # Inisialisasi stopword remover
        stopword_factory = StopWordRemoverFactory()
        self.stopword_remover = stopword_factory.create_stop_word_remover()
        
        # Load stopwords untuk digunakan secara terpisah jika diperlukan
        self.stopwords = stopword_factory.get_stop_words()
    
    def case_folding(self, text: str) -> str:
        """
        Mengubah teks menjadi lowercase
        
        Args:
            text: Teks input
            
        Returns:
            Teks dalam lowercase
        """
        return text.lower()
    
    def remove_punctuation(self, text: str) -> str:
        """
        Menghapus tanda baca dari teks
        
        Args:
            text: Teks input
            
        Returns:
            Teks tanpa tanda baca
        """
        # Hapus semua karakter non-alfanumerik kecuali spasi
        text = re.sub(r'[^\w\s]', ' ', text)
        # Hapus angka
        text = re.sub(r'\d+', '', text)
        # Hapus spasi berlebih
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def tokenize(self, text: str) -> List[str]:
        """
        Memecah teks menjadi token (kata-kata)
        
        Args:
            text: Teks input
            
        Returns:
            List of tokens
        """
        return text.split()
    
    def remove_stopwords(self, tokens: List[str]) -> List[str]:
        """
        Menghapus stopwords dari list tokens
        
        Args:
            tokens: List of tokens
            
        Returns:
            List of tokens tanpa stopwords
        """
        return [token for token in tokens if token not in self.stopwords]
    
    def stem_tokens(self, tokens: List[str]) -> List[str]:
        """
        Melakukan stemming pada list tokens
        
        Args:
            tokens: List of tokens
            
        Returns:
            List of stemmed tokens
        """
        return [self.stemmer.stem(token) for token in tokens]
    
    def preprocess(self, text: str, remove_stopwords: bool = True, 
                   use_stemming: bool = True) -> List[str]:
        """
        Melakukan preprocessing lengkap pada teks
        
        Args:
            text: Teks input
            remove_stopwords: Flag untuk menghapus stopwords
            use_stemming: Flag untuk melakukan stemming
            
        Returns:
            List of preprocessed tokens
        """
        # Case folding
        text = self.case_folding(text)
        
        # Remove punctuation
        text = self.remove_punctuation(text)
        
        # Tokenisasi
        tokens = self.tokenize(text)
        
        # Remove stopwords
        if remove_stopwords:
            tokens = self.remove_stopwords(tokens)
        
        # Stemming
        if use_stemming:
            tokens = self.stem_tokens(tokens)
        
        # Filter token kosong
        tokens = [token for token in tokens if token.strip()]
        
        return tokens
    
    def preprocess_documents(self, documents: List[Dict], 
                           text_field: str = 'content') -> List[Dict]:
        """
        Preprocessing batch untuk multiple documents
        
        Args:
            documents: List of document dictionaries
            text_field: Field name yang berisi teks untuk diproses
            
        Returns:
            List of documents dengan field 'tokens' tambahan
        """
        processed_docs = []
        
        for doc in documents:
            doc_copy = doc.copy()
            text = doc_copy.get(text_field, '')
            
            # Preprocess text
            tokens = self.preprocess(text)
            doc_copy['tokens'] = tokens
            doc_copy['processed_text'] = ' '.join(tokens)
            
            processed_docs.append(doc_copy)
        
        return processed_docs


def main():
    """Function untuk testing"""
    # Contoh penggunaan
    preprocessor = TextPreprocessor()
    
    # Test dengan satu kalimat
    text = "Pemanasan Global adalah peningkatan suhu rata-rata atmosfer, laut, dan daratan Bumi."
    print("Original text:")
    print(text)
    print("\nPreprocessed tokens:")
    tokens = preprocessor.preprocess(text)
    print(tokens)
    print("\nProcessed text:")
    print(' '.join(tokens))
    
    # Test dengan dokumen dari file
    print("\n" + "="*80)
    print("Testing dengan dokumen dari file:")
    print("="*80)
    
    try:
        with open('../data/documents.json', 'r', encoding='utf-8') as f:
            documents = json.load(f)
        
        # Preprocess first 3 documents
        processed = preprocessor.preprocess_documents(documents[:3])
        
        for doc in processed:
            print(f"\nDocument ID: {doc['id']}")
            print(f"Title: {doc['title']}")
            print(f"Tokens ({len(doc['tokens'])}): {doc['tokens'][:20]}...")
    
    except FileNotFoundError:
        print("File documents.json tidak ditemukan. Pastikan path benar.")


if __name__ == "__main__":
    main()
