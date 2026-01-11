"""
Modul Evaluation untuk mengevaluasi performa Information Retrieval System
Meliputi: Precision, Recall, F1-Score, MAP, dan evaluasi lainnya
"""

from typing import List, Dict, Set
import json
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class IREvaluator:
    """
    Class untuk evaluasi Information Retrieval System
    """
    
    def __init__(self):
        """Inisialisasi evaluator"""
        pass
    
    def precision(self, retrieved: Set[int], relevant: Set[int]) -> float:
        """
        Menghitung Precision
        Precision = |Retrieved ∩ Relevant| / |Retrieved|
        
        Args:
            retrieved: Set of retrieved document IDs
            relevant: Set of relevant document IDs
            
        Returns:
            Precision score (0-1)
        """
        if not retrieved:
            return 0.0
        
        retrieved_and_relevant = retrieved & relevant
        return len(retrieved_and_relevant) / len(retrieved)
    
    def recall(self, retrieved: Set[int], relevant: Set[int]) -> float:
        """
        Menghitung Recall
        Recall = |Retrieved ∩ Relevant| / |Relevant|
        
        Args:
            retrieved: Set of retrieved document IDs
            relevant: Set of relevant document IDs
            
        Returns:
            Recall score (0-1)
        """
        if not relevant:
            return 0.0
        
        retrieved_and_relevant = retrieved & relevant
        return len(retrieved_and_relevant) / len(relevant)
    
    def f1_score(self, precision: float, recall: float) -> float:
        """
        Menghitung F1-Score
        F1 = 2 * (Precision * Recall) / (Precision + Recall)
        
        Args:
            precision: Precision score
            recall: Recall score
            
        Returns:
            F1-Score (0-1)
        """
        if precision + recall == 0:
            return 0.0
        
        return 2 * (precision * recall) / (precision + recall)
    
    def average_precision(self, retrieved_ranked: List[int], relevant: Set[int]) -> float:
        """
        Menghitung Average Precision untuk satu query
        
        Args:
            retrieved_ranked: List of retrieved document IDs (ranked)
            relevant: Set of relevant document IDs
            
        Returns:
            Average Precision score
        """
        if not relevant:
            return 0.0
        
        precisions = []
        relevant_count = 0
        
        for i, doc_id in enumerate(retrieved_ranked, 1):
            if doc_id in relevant:
                relevant_count += 1
                precision_at_i = relevant_count / i
                precisions.append(precision_at_i)
        
        if not precisions:
            return 0.0
        
        return sum(precisions) / len(relevant)
    
    def mean_average_precision(self, results: List[Dict]) -> float:
        """
        Menghitung Mean Average Precision (MAP) untuk multiple queries
        
        Args:
            results: List of dictionaries dengan keys 'retrieved' dan 'relevant'
            
        Returns:
            MAP score
        """
        if not results:
            return 0.0
        
        aps = []
        for result in results:
            ap = self.average_precision(result['retrieved'], result['relevant'])
            aps.append(ap)
        
        return sum(aps) / len(aps)
    
    def precision_at_k(self, retrieved_ranked: List[int], relevant: Set[int], k: int) -> float:
        """
        Menghitung Precision@K
        
        Args:
            retrieved_ranked: List of retrieved document IDs (ranked)
            relevant: Set of relevant document IDs
            k: Cutoff position
            
        Returns:
            Precision@K score
        """
        top_k = set(retrieved_ranked[:k])
        return self.precision(top_k, relevant)
    
    def recall_at_k(self, retrieved_ranked: List[int], relevant: Set[int], k: int) -> float:
        """
        Menghitung Recall@K
        
        Args:
            retrieved_ranked: List of retrieved document IDs (ranked)
            relevant: Set of relevant document IDs
            k: Cutoff position
            
        Returns:
            Recall@K score
        """
        top_k = set(retrieved_ranked[:k])
        return self.recall(top_k, relevant)
    
    def ndcg_at_k(self, retrieved_ranked: List[int], relevance_scores: Dict[int, float], k: int) -> float:
        """
        Menghitung Normalized Discounted Cumulative Gain (NDCG@K)
        
        Args:
            retrieved_ranked: List of retrieved document IDs (ranked)
            relevance_scores: Dictionary {doc_id: relevance_score}
            k: Cutoff position
            
        Returns:
            NDCG@K score
        """
        # DCG@K
        dcg = 0.0
        for i, doc_id in enumerate(retrieved_ranked[:k], 1):
            rel = relevance_scores.get(doc_id, 0)
            dcg += rel / (i if i == 1 else (i * 0.693147))  # log2(i+1) ≈ i * 0.693147 untuk i > 1
        
        # IDCG@K (Ideal DCG)
        ideal_ranked = sorted(relevance_scores.items(), key=lambda x: x[1], reverse=True)
        idcg = 0.0
        for i, (doc_id, rel) in enumerate(ideal_ranked[:k], 1):
            idcg += rel / (i if i == 1 else (i * 0.693147))
        
        if idcg == 0:
            return 0.0
        
        return dcg / idcg
    
    def evaluate_query(self, retrieved_ranked: List[int], relevant: Set[int], k: int = 10) -> Dict:
        """
        Evaluasi lengkap untuk satu query
        
        Args:
            retrieved_ranked: List of retrieved document IDs (ranked)
            relevant: Set of relevant document IDs
            k: Cutoff untuk metrics @K
            
        Returns:
            Dictionary berisi berbagai metrics
        """
        retrieved_set = set(retrieved_ranked)
        
        metrics = {
            'precision': self.precision(retrieved_set, relevant),
            'recall': self.recall(retrieved_set, relevant),
            'average_precision': self.average_precision(retrieved_ranked, relevant),
            'precision_at_k': self.precision_at_k(retrieved_ranked, relevant, k),
            'recall_at_k': self.recall_at_k(retrieved_ranked, relevant, k)
        }
        
        # F1-Score
        metrics['f1_score'] = self.f1_score(metrics['precision'], metrics['recall'])
        
        return metrics
    
    def evaluate_system(self, test_queries: List[Dict], k: int = 10) -> Dict:
        """
        Evaluasi sistem secara keseluruhan dengan multiple queries
        
        Args:
            test_queries: List of dictionaries dengan keys 'query', 'retrieved', 'relevant'
            k: Cutoff untuk metrics @K
            
        Returns:
            Dictionary berisi average metrics
        """
        all_metrics = []
        
        for query_data in test_queries:
            metrics = self.evaluate_query(
                query_data['retrieved'],
                query_data['relevant'],
                k
            )
            all_metrics.append(metrics)
        
        # Hitung average
        avg_metrics = {
            'avg_precision': sum(m['precision'] for m in all_metrics) / len(all_metrics),
            'avg_recall': sum(m['recall'] for m in all_metrics) / len(all_metrics),
            'avg_f1_score': sum(m['f1_score'] for m in all_metrics) / len(all_metrics),
            'map': sum(m['average_precision'] for m in all_metrics) / len(all_metrics),
            f'avg_precision_at_{k}': sum(m['precision_at_k'] for m in all_metrics) / len(all_metrics),
            f'avg_recall_at_{k}': sum(m['recall_at_k'] for m in all_metrics) / len(all_metrics)
        }
        
        return avg_metrics


def create_test_queries() -> List[Dict]:
    """
    Membuat test queries dengan relevance judgments
    
    Returns:
        List of test query dictionaries
    """
    test_queries = [
        {
            'query': 'pemanasan global efek rumah kaca',
            'relevant': {1, 2, 3, 4, 10}  # Doc IDs yang relevan
        },
        {
            'query': 'energi terbarukan solusi',
            'relevant': {6, 8, 11}
        },
        {
            'query': 'dampak perubahan iklim',
            'relevant': {3, 4, 5, 9, 14}
        },
        {
            'query': 'emisi karbon transportasi',
            'relevant': {2, 8}
        },
        {
            'query': 'pencairan es kutub',
            'relevant': {4}
        }
    ]
    
    return test_queries


def evaluate_search_system(search_engine, preprocessor, test_queries: List[Dict], k: int = 10) -> Dict:
    """
    Evaluasi search engine dengan test queries
    
    Args:
        search_engine: Objek SearchEngine
        preprocessor: Objek TextPreprocessor
        test_queries: List of test queries
        k: Cutoff untuk retrieval
        
    Returns:
        Dictionary berisi hasil evaluasi
    """
    evaluator = IREvaluator()
    
    # Jalankan query dan kumpulkan hasil
    results = []
    
    for query_data in test_queries:
        query = query_data['query']
        relevant = query_data['relevant']
        
        # Lakukan search
        search_results = search_engine.search(query, preprocessor, method='vector', top_k=k)
        retrieved = [doc['doc_id'] for doc in search_results]
        
        results.append({
            'query': query,
            'retrieved': retrieved,
            'relevant': relevant
        })
    
    # Evaluasi
    evaluation = evaluator.evaluate_system(results, k)
    
    return evaluation, results


def main():
    """Function untuk testing"""
    print("="*80)
    print("Testing Evaluation Module")
    print("="*80)
    
    # Test dengan data dummy
    print("\n1. Test dengan data dummy:")
    print("-"*80)
    
    evaluator = IREvaluator()
    
    # Contoh retrieved dan relevant documents
    retrieved = [1, 3, 5, 7, 9, 2, 4, 6, 8, 10]
    relevant = {1, 2, 3, 4, 5}
    
    metrics = evaluator.evaluate_query(retrieved, relevant, k=10)
    
    print(f"Retrieved: {retrieved}")
    print(f"Relevant: {relevant}")
    print(f"\nMetrics:")
    for metric, value in metrics.items():
        print(f"  {metric}: {value:.4f}")
    
    # Test dengan search engine jika tersedia
    print("\n" + "="*80)
    print("2. Test dengan Search Engine:")
    print("="*80)
    
    try:
        from preprocessing.text_processor import TextPreprocessor
        from indexing.indexer import InvertedIndex, TFIDFCalculator
        from retrieval.search_engine import SearchEngine
        
        # Load index
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.abspath(os.path.join(base_dir, '..', 'data'))
        index_path = os.path.join(data_dir, 'inverted_index.pkl')
        
        if os.path.exists(index_path):
            # Load inverted index
            inv_index = InvertedIndex()
            inv_index.load_index(index_path)
            
            # Inisialisasi components
            tfidf_calc = TFIDFCalculator(inv_index)
            search_engine = SearchEngine(inv_index, tfidf_calc)
            preprocessor = TextPreprocessor()
            
            # Create test queries
            test_queries = create_test_queries()
            
            # Evaluate
            evaluation, results = evaluate_search_system(
                search_engine, 
                preprocessor, 
                test_queries, 
                k=10
            )
            
            print("\nHasil Evaluasi Sistem:")
            print("-"*80)
            for metric, value in evaluation.items():
                print(f"{metric}: {value:.4f}")
            
            # Detail per query
            print("\n" + "="*80)
            print("Detail Evaluasi per Query:")
            print("="*80)
            
            for i, result in enumerate(results, 1):
                print(f"\nQuery {i}: {result['query']}")
                retrieved_set = set(result['retrieved'])
                relevant = result['relevant']
                
                precision = evaluator.precision(retrieved_set, relevant)
                recall = evaluator.recall(retrieved_set, relevant)
                f1 = evaluator.f1_score(precision, recall)
                
                print(f"  Retrieved: {result['retrieved']}")
                print(f"  Relevant: {relevant}")
                print(f"  Precision: {precision:.4f}")
                print(f"  Recall: {recall:.4f}")
                print(f"  F1-Score: {f1:.4f}")
        
        else:
            print(f"Index file tidak ditemukan: {index_path}")
            print("Jalankan indexer.py terlebih dahulu")
    
    except ImportError as e:
        print(f"Error importing modules: {e}")
        print("Pastikan semua modul tersedia")


if __name__ == "__main__":
    main()
