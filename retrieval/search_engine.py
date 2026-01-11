"""
Modul Retrieval untuk Information Retrieval System
Meliputi: Query Processing, Document Ranking, dan Search
"""

import math
from typing import List, Dict, Tuple
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class SearchEngine:
    """
    Class untuk melakukan pencarian dokumen
    """
    
    def __init__(self, inverted_index, tfidf_calculator):
        """
        Inisialisasi search engine
        
        Args:
            inverted_index: Objek InvertedIndex
            tfidf_calculator: Objek TFIDFCalculator
        """
        self.index = inverted_index
        self.tfidf = tfidf_calculator
    
    def cosine_similarity(self, vector1: Dict[str, float], 
                         vector2: Dict[str, float]) -> float:
        """
        Menghitung cosine similarity antara dua vektor
        
        Args:
            vector1: Dictionary {term: weight}
            vector2: Dictionary {term: weight}
            
        Returns:
            Cosine similarity score (0-1)
        """
        # Dapatkan terms yang ada di kedua vektor
        common_terms = set(vector1.keys()) & set(vector2.keys())
        
        if not common_terms:
            return 0.0
        
        # Hitung dot product
        dot_product = sum(vector1[term] * vector2[term] for term in common_terms)
        
        # Hitung magnitude
        magnitude1 = math.sqrt(sum(weight ** 2 for weight in vector1.values()))
        magnitude2 = math.sqrt(sum(weight ** 2 for weight in vector2.values()))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        # Cosine similarity
        return dot_product / (magnitude1 * magnitude2)
    
    def boolean_search(self, query_terms: List[str], operator: str = 'AND') -> List[int]:
        """
        Boolean search dengan operator AND/OR
        
        Args:
            query_terms: List of query terms
            operator: 'AND' atau 'OR'
            
        Returns:
            List of document IDs yang memenuhi query
        """
        if not query_terms:
            return []
        
        # Dapatkan posting list untuk setiap term
        posting_lists = []
        for term in query_terms:
            postings = self.index.get_postings(term)
            doc_ids = set(doc_id for doc_id, _ in postings)
            posting_lists.append(doc_ids)
        
        # Kombinasikan dengan operator
        if operator == 'AND':
            # Intersection
            result = posting_lists[0]
            for doc_ids in posting_lists[1:]:
                result = result & doc_ids
        else:  # OR
            # Union
            result = set()
            for doc_ids in posting_lists:
                result = result | doc_ids
        
        return list(result)
    
    def vector_space_search(self, query_terms: List[str], 
                          top_k: int = 10) -> List[Tuple[int, float]]:
        """
        Vector Space Model search dengan cosine similarity
        
        Args:
            query_terms: List of query terms
            top_k: Jumlah dokumen teratas yang dikembalikan
            
        Returns:
            List of (doc_id, similarity_score) tuples, sorted by score
        """
        # Hitung query vector
        query_vector = self.tfidf.calculate_query_vector(query_terms)
        
        if not query_vector:
            return []
        
        # Dapatkan kandidat dokumen (dokumen yang mengandung minimal satu query term)
        candidate_docs = set()
        for term in query_terms:
            postings = self.index.get_postings(term)
            for doc_id, _ in postings:
                candidate_docs.add(doc_id)
        
        # Hitung similarity untuk setiap kandidat
        scores = []
        for doc_id in candidate_docs:
            # Hitung document vector hanya untuk terms yang ada di query
            doc_vector = self.tfidf.calculate_document_vector(doc_id, query_terms)
            
            # Hitung cosine similarity
            similarity = self.cosine_similarity(query_vector, doc_vector)
            
            if similarity > 0:
                scores.append((doc_id, similarity))
        
        # Sort by similarity (descending)
        scores.sort(key=lambda x: x[1], reverse=True)
        
        return scores[:top_k]
    
    def search(self, query: str, preprocessor, method: str = 'vector', 
              top_k: int = 10) -> List[Dict]:
        """
        Melakukan pencarian dokumen berdasarkan query
        
        Args:
            query: Query string
            preprocessor: Objek TextPreprocessor
            method: Metode pencarian ('vector', 'boolean_and', 'boolean_or')
            top_k: Jumlah hasil teratas (untuk vector space)
            
        Returns:
            List of document dictionaries dengan score
        """
        # Preprocess query
        query_terms = preprocessor.preprocess(query)
        
        if not query_terms:
            return []
        
        print(f"Query terms: {query_terms}")
        
        # Lakukan pencarian berdasarkan metode
        if method == 'vector':
            results = self.vector_space_search(query_terms, top_k)
            
            # Format hasil
            formatted_results = []
            for doc_id, score in results:
                doc = self.index.documents.get(doc_id, {})
                formatted_results.append({
                    'doc_id': doc_id,
                    'score': score,
                    'title': doc.get('title', ''),
                    'content': doc.get('content', ''),
                    'author': doc.get('author', ''),
                    'date': doc.get('date', ''),
                    'category': doc.get('category', '')
                })
            
            return formatted_results
        
        elif method in ['boolean_and', 'boolean_or']:
            operator = 'AND' if method == 'boolean_and' else 'OR'
            doc_ids = self.boolean_search(query_terms, operator)
            
            # Format hasil
            formatted_results = []
            for doc_id in doc_ids[:top_k]:
                doc = self.index.documents.get(doc_id, {})
                formatted_results.append({
                    'doc_id': doc_id,
                    'score': 1.0,  # Boolean search tidak ada score
                    'title': doc.get('title', ''),
                    'content': doc.get('content', ''),
                    'author': doc.get('author', ''),
                    'date': doc.get('date', ''),
                    'category': doc.get('category', '')
                })
            
            return formatted_results
        
        else:
            raise ValueError(f"Unknown search method: {method}")
    
    def get_document_by_id(self, doc_id: int) -> Dict:
        """
        Mendapatkan dokumen berdasarkan ID
        
        Args:
            doc_id: ID dokumen
            
        Returns:
            Document dictionary
        """
        return self.index.documents.get(doc_id, {})
    
    def get_related_documents(self, doc_id: int, top_k: int = 5) -> List[Dict]:
        """
        Mendapatkan dokumen yang mirip dengan dokumen tertentu
        
        Args:
            doc_id: ID dokumen referensi
            top_k: Jumlah dokumen mirip yang dikembalikan
            
        Returns:
            List of similar documents dengan score
        """
        # Dapatkan document vector
        doc_vector = self.tfidf.calculate_document_vector(doc_id)
        
        if not doc_vector:
            return []
        
        # Hitung similarity dengan dokumen lain
        scores = []
        for other_doc_id in self.index.documents.keys():
            if other_doc_id == doc_id:
                continue
            
            # Hitung vector untuk dokumen lain
            other_vector = self.tfidf.calculate_document_vector(
                other_doc_id, 
                list(doc_vector.keys())
            )
            
            # Hitung similarity
            similarity = self.cosine_similarity(doc_vector, other_vector)
            
            if similarity > 0:
                scores.append((other_doc_id, similarity))
        
        # Sort by similarity
        scores.sort(key=lambda x: x[1], reverse=True)
        
        # Format hasil
        results = []
        for other_doc_id, score in scores[:top_k]:
            doc = self.index.documents.get(other_doc_id, {})
            results.append({
                'doc_id': other_doc_id,
                'score': score,
                'title': doc.get('title', ''),
                'content': doc.get('content', ''),
                'author': doc.get('author', ''),
                'date': doc.get('date', ''),
                'category': doc.get('category', '')
            })
        
        return results


def main():
    """Function untuk testing"""
    print("="*80)
    print("Testing Search Engine")
    print("="*80)
    
    # Import modules
    from preprocessing.text_processor import TextPreprocessor
    from indexing.indexer import InvertedIndex, TFIDFCalculator
    import os
    
    # Load index
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.abspath(os.path.join(base_dir, '..', 'data'))
    index_path = os.path.join(data_dir, 'inverted_index.pkl')
    
    if not os.path.exists(index_path):
        print(f"Index file tidak ditemukan: {index_path}")
        print("Jalankan indexer.py terlebih dahulu untuk membuat index")
        return
    
    # Load inverted index
    inv_index = InvertedIndex()
    inv_index.load_index(index_path)
    
    # Inisialisasi TF-IDF calculator
    tfidf_calc = TFIDFCalculator(inv_index)
    
    # Inisialisasi search engine
    search_engine = SearchEngine(inv_index, tfidf_calc)
    
    # Inisialisasi preprocessor
    preprocessor = TextPreprocessor()
    
    # Test queries
    queries = [
        "pemanasan global dan efek rumah kaca",
        "energi terbarukan solusi",
        "dampak perubahan iklim",
        "emisi karbon transportasi"
    ]
    
    for query in queries:
        print(f"\n{'='*80}")
        print(f"Query: {query}")
        print('='*80)
        
        # Vector space search
        results = search_engine.search(query, preprocessor, method='vector', top_k=5)
        
        print(f"\nDitemukan {len(results)} dokumen relevan:\n")
        
        for i, doc in enumerate(results, 1):
            print(f"{i}. [{doc['doc_id']}] {doc['title']}")
            print(f"   Score: {doc['score']:.4f}")
            print(f"   Kategori: {doc['category']}")
            print(f"   Excerpt: {doc['content'][:100]}...")
            print()
    
    # Test related documents
    print(f"\n{'='*80}")
    print("Testing Related Documents")
    print('='*80)
    
    doc_id = 1
    related = search_engine.get_related_documents(doc_id, top_k=3)
    
    ref_doc = search_engine.get_document_by_id(doc_id)
    print(f"\nDokumen Referensi [{doc_id}]: {ref_doc.get('title', '')}")
    print(f"\nDokumen Mirip:\n")
    
    for i, doc in enumerate(related, 1):
        print(f"{i}. [{doc['doc_id']}] {doc['title']}")
        print(f"   Similarity: {doc['score']:.4f}")
        print(f"   Kategori: {doc['category']}")
        print()


if __name__ == "__main__":
    main()
