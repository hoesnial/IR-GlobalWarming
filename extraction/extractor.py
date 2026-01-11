"""
Modul Extraction untuk Ekstraksi Informasi dari Dokumen
Meliputi: Text Summarization, Keyword Extraction, Named Entity Recognition
"""

from typing import List, Dict, Tuple
from collections import Counter
import re
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class KeywordExtractor:
    """
    Class untuk ekstraksi keyword dari dokumen
    """
    
    def __init__(self, tfidf_calculator=None):
        """
        Inisialisasi keyword extractor
        
        Args:
            tfidf_calculator: Objek TFIDFCalculator (opsional)
        """
        self.tfidf = tfidf_calculator
    
    def extract_by_frequency(self, tokens: List[str], top_k: int = 10) -> List[Tuple[str, int]]:
        """
        Ekstraksi keyword berdasarkan frekuensi
        
        Args:
            tokens: List of tokens
            top_k: Jumlah keyword teratas
            
        Returns:
            List of (keyword, frequency) tuples
        """
        # Hitung frekuensi
        freq = Counter(tokens)
        
        # Ambil top k
        return freq.most_common(top_k)
    
    def extract_by_tfidf(self, doc_id: int, top_k: int = 10) -> List[Tuple[str, float]]:
        """
        Ekstraksi keyword berdasarkan TF-IDF score
        
        Args:
            doc_id: ID dokumen
            top_k: Jumlah keyword teratas
            
        Returns:
            List of (keyword, tfidf_score) tuples
        """
        if not self.tfidf:
            raise ValueError("TF-IDF calculator tidak tersedia")
        
        # Hitung document vector
        doc_vector = self.tfidf.calculate_document_vector(doc_id)
        
        # Sort by TF-IDF score
        keywords = sorted(doc_vector.items(), key=lambda x: x[1], reverse=True)
        
        return keywords[:top_k]
    
    def extract_keywords(self, text: str, preprocessor, method: str = 'frequency', 
                        top_k: int = 10) -> List[Tuple[str, float]]:
        """
        Ekstraksi keyword dari teks
        
        Args:
            text: Teks input
            preprocessor: Objek TextPreprocessor
            method: Metode ekstraksi ('frequency' atau 'tfidf')
            top_k: Jumlah keyword teratas
            
        Returns:
            List of (keyword, score) tuples
        """
        # Preprocess text
        tokens = preprocessor.preprocess(text)
        
        if method == 'frequency':
            return self.extract_by_frequency(tokens, top_k)
        else:
            raise ValueError(f"Method {method} tidak tersedia untuk teks standalone")


class TextSummarizer:
    """
    Class untuk membuat ringkasan dokumen
    """
    
    def __init__(self):
        """Inisialisasi summarizer"""
        pass
    
    def split_sentences(self, text: str) -> List[str]:
        """
        Memecah teks menjadi kalimat
        
        Args:
            text: Teks input
            
        Returns:
            List of sentences
        """
        # Split by period, exclamation, or question mark followed by space
        sentences = re.split(r'[.!?]+\s+', text)
        
        # Clean and filter
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences
    
    def score_sentences(self, sentences: List[str], keywords: List[str]) -> Dict[int, float]:
        """
        Memberikan score pada kalimat berdasarkan keyword
        
        Args:
            sentences: List of sentences
            keywords: List of important keywords
            
        Returns:
            Dictionary {sentence_index: score}
        """
        scores = {}
        
        # Lowercase keywords untuk matching
        keywords_lower = [k.lower() for k in keywords]
        
        for i, sentence in enumerate(sentences):
            sentence_lower = sentence.lower()
            
            # Hitung jumlah keywords dalam kalimat
            score = sum(1 for keyword in keywords_lower if keyword in sentence_lower)
            
            # Normalisasi dengan panjang kalimat
            words = sentence.split()
            if words:
                score = score / len(words)
            
            scores[i] = score
        
        return scores
    
    def extractive_summary(self, text: str, keywords: List[str], 
                          num_sentences: int = 3) -> str:
        """
        Membuat ringkasan ekstraktif berdasarkan keyword
        
        Args:
            text: Teks lengkap
            keywords: List of important keywords
            num_sentences: Jumlah kalimat dalam ringkasan
            
        Returns:
            Summary text
        """
        # Split menjadi kalimat
        sentences = self.split_sentences(text)
        
        if len(sentences) <= num_sentences:
            return text
        
        # Score kalimat
        scores = self.score_sentences(sentences, keywords)
        
        # Pilih top sentences
        top_indices = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)[:num_sentences]
        
        # Sort berdasarkan urutan asli
        top_indices.sort()
        
        # Gabungkan kalimat
        summary = '. '.join(sentences[i] for i in top_indices)
        
        return summary + '.'
    
    def simple_summary(self, text: str, num_sentences: int = 3) -> str:
        """
        Membuat ringkasan sederhana (kalimat pertama)
        
        Args:
            text: Teks lengkap
            num_sentences: Jumlah kalimat pertama yang diambil
            
        Returns:
            Summary text
        """
        sentences = self.split_sentences(text)
        
        # Ambil n kalimat pertama
        summary_sentences = sentences[:num_sentences]
        
        return '. '.join(summary_sentences) + '.'


class EntityExtractor:
    """
    Class untuk ekstraksi entitas dari teks (simple pattern-based)
    """
    
    def __init__(self):
        """Inisialisasi entity extractor"""
        # Pola untuk mengenali entitas terkait pemanasan global
        self.patterns = {
            'gas_rumah_kaca': [
                'karbon dioksida', 'co2', 'metana', 'ch4', 
                'dinitrogen oksida', 'n2o', 'gas rumah kaca'
            ],
            'energi': [
                'energi surya', 'energi angin', 'energi terbarukan',
                'energi hidro', 'energi geotermal', 'biomassa',
                'bahan bakar fosil', 'batu bara', 'minyak', 'gas alam'
            ],
            'dampak': [
                'pemanasan global', 'perubahan iklim', 'kenaikan suhu',
                'pencairan es', 'kenaikan permukaan laut', 'banjir',
                'kekeringan', 'badai', 'kebakaran hutan'
            ],
            'lokasi': [
                'arktik', 'antartika', 'greenland', 'amazon',
                'kutub', 'pesisir', 'hutan tropis'
            ],
            'solusi': [
                'reboisasi', 'aforestasi', 'carbon capture',
                'kendaraan listrik', 'transportasi umum',
                'paris agreement', 'protokol kyoto', 'green economy'
            ]
        }
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Ekstraksi entitas dari teks
        
        Args:
            text: Teks input
            
        Returns:
            Dictionary {entity_type: [entities]}
        """
        text_lower = text.lower()
        entities = {}
        
        for entity_type, patterns in self.patterns.items():
            found_entities = []
            
            for pattern in patterns:
                if pattern in text_lower:
                    found_entities.append(pattern)
            
            if found_entities:
                entities[entity_type] = found_entities
        
        return entities
    
    def extract_numbers(self, text: str) -> List[Tuple[str, str]]:
        """
        Ekstraksi angka dan statistik dari teks
        
        Args:
            text: Teks input
            
        Returns:
            List of (number, context) tuples
        """
        # Pattern untuk angka dengan konteks
        pattern = r'(\d+(?:\.\d+)?)\s*(%|derajat|celsius|cm|meter|ton|miliar|juta|ribu)'
        
        matches = re.findall(pattern, text.lower())
        
        return matches


def extract_document_info(document: Dict, preprocessor, tfidf_calculator=None) -> Dict:
    """
    Ekstraksi informasi lengkap dari dokumen
    
    Args:
        document: Document dictionary
        preprocessor: Objek TextPreprocessor
        tfidf_calculator: Objek TFIDFCalculator (opsional)
        
    Returns:
        Dictionary berisi informasi yang diekstrak
    """
    text = document.get('content', '')
    
    # Keyword extraction
    keyword_extractor = KeywordExtractor(tfidf_calculator)
    
    if tfidf_calculator and 'id' in document:
        keywords = keyword_extractor.extract_by_tfidf(document['id'], top_k=10)
    else:
        keywords = keyword_extractor.extract_keywords(text, preprocessor, top_k=10)
    
    # Text summarization
    summarizer = TextSummarizer()
    keyword_list = [k[0] for k in keywords[:5]]
    summary = summarizer.extractive_summary(text, keyword_list, num_sentences=3)
    
    # Entity extraction
    entity_extractor = EntityExtractor()
    entities = entity_extractor.extract_entities(text)
    numbers = entity_extractor.extract_numbers(text)
    
    return {
        'keywords': keywords,
        'summary': summary,
        'entities': entities,
        'statistics': numbers
    }


def main():
    """Function untuk testing"""
    print("="*80)
    print("Testing Extraction Module")
    print("="*80)
    
    from preprocessing.text_processor import TextPreprocessor
    import json
    
    # Load dokumen
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.abspath(os.path.join(base_dir, '..', 'data'))
    docs_path = os.path.join(data_dir, 'documents.json')
    
    if not os.path.exists(docs_path):
        print(f"File {docs_path} tidak ditemukan!")
        return
    
    with open(docs_path, 'r', encoding='utf-8') as f:
        documents = json.load(f)
    
    # Test dengan dokumen pertama
    doc = documents[0]
    
    print(f"\nDokumen: {doc['title']}")
    print("="*80)
    
    # Inisialisasi preprocessor
    preprocessor = TextPreprocessor()
    
    # Ekstraksi informasi
    info = extract_document_info(doc, preprocessor)
    
    print("\n1. KEYWORDS (Top 10):")
    for i, (keyword, score) in enumerate(info['keywords'], 1):
        print(f"   {i}. {keyword}: {score:.2f}")
    
    print("\n2. SUMMARY:")
    print(f"   {info['summary']}")
    
    print("\n3. ENTITIES:")
    for entity_type, entities in info['entities'].items():
        print(f"   {entity_type}: {', '.join(entities)}")
    
    print("\n4. STATISTICS:")
    for number, unit in info['statistics']:
        print(f"   {number} {unit}")
    
    # Test dengan beberapa dokumen lain
    print("\n" + "="*80)
    print("Testing dengan dokumen lain:")
    print("="*80)
    
    for doc in documents[5:8]:
        print(f"\nDokumen [{doc['id']}]: {doc['title']}")
        info = extract_document_info(doc, preprocessor)
        print(f"Keywords: {', '.join([k[0] for k in info['keywords'][:5]])}")
        print(f"Summary: {info['summary'][:100]}...")


if __name__ == "__main__":
    main()
