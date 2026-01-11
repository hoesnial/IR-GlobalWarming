"""
Main Program - Information Retrieval System untuk Dokumen Pemanasan Global
Program utama dengan GUI menggunakan Tkinter
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
import os
import sys
import subprocess

# Add modules to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from preprocessing.text_processor import TextPreprocessor
from indexing.indexer import InvertedIndex, TFIDFCalculator, build_index_from_documents
from retrieval.search_engine import SearchEngine
from extraction.extractor import KeywordExtractor, TextSummarizer, extract_document_info
from evaluation.evaluator import IREvaluator, create_test_queries, evaluate_search_system


class IRSystemGUI:
    """
    GUI untuk Information Retrieval System
    """
    
    def __init__(self, root):
        """
        Inisialisasi GUI
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("Sistem Pencarian Dokumen Pemanasan Global")
        self.root.geometry("1200x800")
        
        # Initialize components
        self.preprocessor = None
        self.inverted_index = None
        self.tfidf_calculator = None
        self.search_engine = None
        self.current_results = []  # Store current search results with PDF paths
        
        # Load atau build index
        self.initialize_system()
        
        # Setup GUI
        self.setup_gui()
    
    def initialize_system(self):
        """Inisialisasi komponen IR system"""
        try:
            # Path files
            base_dir = os.path.dirname(os.path.abspath(__file__))
            data_dir = os.path.join(base_dir, 'data')
            docs_path = os.path.join(data_dir, 'documents.json')
            index_path = os.path.join(data_dir, 'inverted_index.pkl')
            # Simpan data_dir untuk penggunaan di fitur buka PDF
            self.data_dir = data_dir
            
            # Check if documents exist
            if not os.path.exists(docs_path):
                messagebox.showerror("Error", f"File dokumen tidak ditemukan: {docs_path}")
                return
            
            # Initialize preprocessor
            self.preprocessor = TextPreprocessor()
            
            # Load atau build index
            if os.path.exists(index_path):
                print("Loading existing index...")
                self.inverted_index = InvertedIndex()
                self.inverted_index.load_index(index_path)
            else:
                print("Building new index...")
                # Pass data_dir to scan all files
                self.inverted_index = build_index_from_documents(data_dir, index_path)
            
            # Initialize TF-IDF calculator
            self.tfidf_calculator = TFIDFCalculator(self.inverted_index)
            
            # Initialize search engine
            self.search_engine = SearchEngine(self.inverted_index, self.tfidf_calculator)
            
            print("System initialized successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menginisialisasi sistem: {str(e)}")
            print(f"Error: {e}")
    
    def setup_gui(self):
        """Setup GUI components"""
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="Sistem Pencarian & Ekstraksi Dokumen Pemanasan Global",
            font=('Arial', 16, 'bold')
        )
        title_label.grid(row=0, column=0, pady=10)
        
        # Search frame
        search_frame = ttk.LabelFrame(main_frame, text="Pencarian", padding="10")
        search_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        search_frame.columnconfigure(1, weight=1)
        
        # Query input
        ttk.Label(search_frame, text="Query:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.query_entry = ttk.Entry(search_frame, width=50)
        self.query_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        self.query_entry.bind('<Return>', lambda e: self.perform_search())
        
        # Search method
        ttk.Label(search_frame, text="Metode:").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.search_method = tk.StringVar(value='vector')
        method_frame = ttk.Frame(search_frame)
        method_frame.grid(row=1, column=1, sticky=tk.W, padx=5)
        
        ttk.Radiobutton(method_frame, text="Vector Space", variable=self.search_method, 
                       value='vector').pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(method_frame, text="Boolean AND", variable=self.search_method, 
                       value='boolean_and').pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(method_frame, text="Boolean OR", variable=self.search_method, 
                       value='boolean_or').pack(side=tk.LEFT, padx=5)
        
        # Top K
        ttk.Label(search_frame, text="Jumlah Hasil:").grid(row=2, column=0, sticky=tk.W, padx=5)
        self.top_k = tk.IntVar(value=10)
        ttk.Spinbox(search_frame, from_=1, to=15, textvariable=self.top_k, width=10).grid(
            row=2, column=1, sticky=tk.W, padx=5
        )
        
        # Search button
        search_btn = ttk.Button(search_frame, text="Cari", command=self.perform_search)
        search_btn.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Results frame
        results_frame = ttk.LabelFrame(main_frame, text="Hasil Pencarian", padding="10")
        results_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # Results text area with PDF button frame
        text_frame = ttk.Frame(results_frame)
        text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        self.results_text = scrolledtext.ScrolledText(
            text_frame, 
            wrap=tk.WORD, 
            width=120, 
            height=30,
            font=('Consolas', 10)
        )
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Frame untuk tombol buka PDF di samping kanan
        self.pdf_buttons_frame = ttk.Frame(text_frame)
        self.pdf_buttons_frame.grid(row=0, column=1, sticky=(tk.N, tk.S), padx=5)
        
        ttk.Label(self.pdf_buttons_frame, text="Buka PDF:", font=('Arial', 9, 'bold')).pack(pady=5)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, pady=5)
        
        ttk.Button(button_frame, text="Evaluasi Sistem", 
                  command=self.evaluate_system).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Statistik Index", 
                  command=self.show_index_stats).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Lihat Semua Dokumen", 
                  command=self.show_all_documents).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Rebuild Index", 
                  command=self.rebuild_index_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Download PDF", 
                  command=self.download_documents).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Keluar", 
                  command=self.root.quit).pack(side=tk.LEFT, padx=5)
        
        # Status bar
        self.status_var = tk.StringVar(value="Sistem siap")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=5)
    
    def download_documents(self):
        """Mendownload dokumen PDF dari link di JSON"""
        try:
            from indexing.downloader import DocumentDownloader
            import threading
            
            confirm = messagebox.askyesno(
                "Konfirmasi Download", 
                "Sistem akan memeriksa dan mendownload dokumen PDF yang belum ada di folder data.\n\n" +
                "Proses ini membutuhkan koneksi internet. Lanjutkan?"
            )
            
            if not confirm:
                return
            
            # Paths
            base_dir = os.path.dirname(os.path.abspath(__file__))
            data_dir = os.path.join(base_dir, 'data')
            docs_path = os.path.join(data_dir, 'documents.json')
            
            # Callback untuk update UI
            def progress_callback(msg):
                self.status_var.set(msg)
                self.root.update()
                print(msg)
            
            # Jalankan di function local (untuk kesederhanaan, bisa di-thread jika ingin non-blocking total)
            # Tapi karena tkinter butuh update di main thread, kita jalankan langsung saja dengan self.root.update()
            
            self.status_var.set("Menyiapkan download...")
            downloader = DocumentDownloader(data_dir)
            
            success, fail, skipped = downloader.download_from_json(docs_path, progress_callback)
            
            result_msg = f"Proses Selesai.\n\nBerhasil: {success}\nGagal: {fail}\nTerlewati: {skipped}"
            messagebox.showinfo("Download Selesai", result_msg)
            
            if success > 0:
                # Tawarkan rebuild index
                rebuild = messagebox.askyesno(
                    "Rebuild Index?", 
                    "Ada dokumen baru didownload. Apakah Anda ingin membangun ulang index sekarang?"
                )
                if rebuild:
                    self.rebuild_index_dialog()
            
        except Exception as e:
            messagebox.showerror("Error", f"Gagal mendownload: {str(e)}")
            self.status_var.set("Error Download")
            
    def perform_search(self):
        """Melakukan pencarian dokumen"""
        query = self.query_entry.get().strip()
        
        if not query:
            messagebox.showwarning("Warning", "Masukkan query terlebih dahulu!")
            return
        
        if not self.search_engine:
            messagebox.showerror("Error", "Search engine belum diinisialisasi!")
            return
        
        try:
            # Update status
            self.status_var.set("Mencari...")
            self.root.update()
            
            # Search
            method = self.search_method.get()
            top_k = self.top_k.get()
            
            results = self.search_engine.search(
                query, 
                self.preprocessor, 
                method=method, 
                top_k=top_k
            )
            
            # Store results for PDF opening
            self.current_results = results
            
            # Display results
            self.display_results(query, results, method)
            
            # Update status
            self.status_var.set(f"Ditemukan {len(results)} dokumen")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error saat pencarian: {str(e)}")
            self.status_var.set("Error")
    
    def display_results(self, query, results, method):
        """Menampilkan hasil pencarian"""
        # Clear previous results
        self.results_text.delete(1.0, tk.END)
        
        # Clear previous PDF buttons
        for widget in self.pdf_buttons_frame.winfo_children():
            if isinstance(widget, ttk.Button):
                widget.destroy()
        
        # Header
        header = f"{'='*100}\n"
        header += f"HASIL PENCARIAN\n"
        header += f"{'='*100}\n"
        header += f"Query: {query}\n"
        header += f"Metode: {method}\n"
        header += f"Jumlah hasil: {len(results)}\n"
        header += f"{'='*100}\n\n"
        
        self.results_text.insert(tk.END, header)
        
        if not results:
            self.results_text.insert(tk.END, "Tidak ada dokumen yang ditemukan.\n")
            return
        
        # Re-add label after clearing buttons
        ttk.Label(self.pdf_buttons_frame, text="Buka PDF:", font=('Arial', 9, 'bold')).pack(pady=5)
        
        # Display each result
        for i, doc in enumerate(results, 1):
            result_text = f"[{i}] Dokumen ID: {doc['doc_id']}"
            if method == 'vector':
                result_text += f" | Score: {doc['score']:.4f}"
            result_text += "\n"
            
            result_text += f"Judul: {doc['title']}\n"
            result_text += f"Kategori: {doc['category']} | Penulis: {doc['author']} | Tanggal: {doc['date']}\n"
            # Generate snippet based on query terms
            snippet = self.get_content_snippet(doc['content'], query)
            result_text += f"\nSnippet:\n{snippet}\n"
            
            # Extract keywords
            try:
                keyword_extractor = KeywordExtractor(self.tfidf_calculator)
                keywords = keyword_extractor.extract_by_tfidf(doc['doc_id'], top_k=5)
                keyword_str = ", ".join([k[0] for k in keywords])
                result_text += f"\nKeywords: {keyword_str}\n"
            except:
                pass
            
            # Tentukan path PDF dari metadata dokumen
            pdf_path = doc.get('pdf_path', '')
            if not pdf_path:
                # Fallback: gunakan source_file dari proses merge PDF
                source_file = doc.get('source_file', '')
                if source_file:
                    candidate_path = os.path.join(getattr(self, 'data_dir', os.path.dirname(os.path.abspath(__file__))), source_file)
                    if os.path.exists(candidate_path):
                        pdf_path = candidate_path

            if pdf_path and os.path.exists(pdf_path):
                result_text += f"PDF: {os.path.basename(pdf_path)}\n"
                # Add button to open PDF
                btn = ttk.Button(
                    self.pdf_buttons_frame,
                    text=f"[{i}] {doc['title'][:25]}...",
                    command=lambda p=pdf_path: self.open_pdf(p),
                    width=30
                )
                btn.pack(pady=2, fill=tk.X)
            
            result_text += f"\n{'-'*100}\n\n"
            
            self.results_text.insert(tk.END, result_text)
    
    def get_content_snippet(self, content, query, window=150):
        """
        Membuat snippet (potongan teks) yang relevan dengan query (Keyword In Context)
        """
        if not content:
            return ""
            
        # Preprocess query terms for matching
        if not self.preprocessor:
            return content[:300] + "..."
            
        query_terms = self.preprocessor.preprocess(query)
        lower_content = content.lower()
        
        best_pos = -1
        
        # Cari posisi term pertama yang muncul
        for term in query_terms:
            pos = lower_content.find(term)
            if pos != -1:
                best_pos = pos
                break
        
        if best_pos == -1:
            # Jika tidak ada exact match keywords (misal karena stemming),
            # tampilkan awal dokumen saja
            return content[:300] + "..."
            
        # Potong text di sekitar keyword
        start = max(0, best_pos - window)
        end = min(len(content), best_pos + window)
        
        snippet = content[start:end]
        
        # Rapikan visual (tambahkan ellipsis)
        if start > 0:
            snippet = "..." + snippet[3:]
        if end < len(content):
            snippet = snippet[:-3] + "..."
            
        return snippet.replace('\n', ' ')
    
    def open_pdf(self, pdf_path):
        """Membuka file PDF menggunakan default PDF viewer"""
        try:
            if not os.path.exists(pdf_path):
                messagebox.showerror("Error", f"File PDF tidak ditemukan:\n{pdf_path}")
                return
            
            # Buka PDF dengan default viewer di Windows
            if sys.platform == 'win32':
                os.startfile(pdf_path)
            elif sys.platform == 'darwin':  # macOS
                subprocess.run(['open', pdf_path])
            else:  # Linux
                subprocess.run(['xdg-open', pdf_path])
            
            self.status_var.set(f"Membuka: {os.path.basename(pdf_path)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membuka PDF:\n{str(e)}")
            self.status_var.set("Error membuka PDF")

    def show_index_stats(self):
        """Menampilkan statistik index"""
        if not self.inverted_index:
            messagebox.showerror("Error", "Index belum diinisialisasi!")
            return
        
        stats = self.inverted_index.get_stats()
        
        # Clear results
        self.results_text.delete(1.0, tk.END)
        
        stats_text = f"{'='*100}\n"
        stats_text += f"STATISTIK INVERTED INDEX\n"
        stats_text += f"{'='*100}\n\n"
        stats_text += f"Total Dokumen: {stats['total_documents']}\n"
        stats_text += f"Total Unique Terms: {stats['total_terms']}\n"
        stats_text += f"Rata-rata Panjang Dokumen: {stats['avg_doc_length']:.2f} terms\n\n"
        
        # Top terms by document frequency
        stats_text += f"{'='*100}\n"
        stats_text += f"TOP 20 TERMS (berdasarkan Document Frequency)\n"
        stats_text += f"{'='*100}\n\n"
        
        term_df = [(term, len(postings)) for term, postings in self.inverted_index.index.items()]
        term_df.sort(key=lambda x: x[1], reverse=True)
        
        for i, (term, df) in enumerate(term_df[:20], 1):
            stats_text += f"{i:2d}. {term:20s} - DF: {df:3d}\n"
        
        self.results_text.insert(tk.END, stats_text)
        self.status_var.set("Statistik ditampilkan")
    
    def show_all_documents(self):
        """Menampilkan semua dokumen"""
        if not self.inverted_index:
            messagebox.showerror("Error", "Index belum diinisialisasi!")
            return
        
        # Clear results
        self.results_text.delete(1.0, tk.END)
        
        header = f"{'='*100}\n"
        header += f"DAFTAR SEMUA DOKUMEN\n"
        header += f"{'='*100}\n\n"
        
        self.results_text.insert(tk.END, header)
        
        # Display all documents
        for doc_id, doc in sorted(self.inverted_index.documents.items()):
            doc_text = f"[{doc_id:2d}] {doc['title']}\n"
            doc_text += f"     Kategori: {doc['category']} | Penulis: {doc['author']}\n"
            doc_text += f"     {doc['content'][:150]}...\n\n"
            
            self.results_text.insert(tk.END, doc_text)
        
        self.status_var.set(f"Total {len(self.inverted_index.documents)} dokumen")
    
    def evaluate_system(self):
        """Evaluasi performa sistem"""
        if not self.search_engine:
            messagebox.showerror("Error", "Search engine belum diinisialisasi!")
            return
        
        try:
            # Update status
            self.status_var.set("Mengevaluasi sistem...")
            self.root.update()
            
            # Create test queries
            test_queries = create_test_queries()
            
            # Evaluate
            evaluation, results = evaluate_search_system(
                self.search_engine,
                self.preprocessor,
                test_queries,
                k=10
            )
            
            # Display evaluation results
            self.results_text.delete(1.0, tk.END)
            
            eval_text = f"{'='*100}\n"
            eval_text += f"HASIL EVALUASI SISTEM\n"
            eval_text += f"{'='*100}\n\n"
            eval_text += f"Jumlah Test Queries: {len(test_queries)}\n\n"
            
            eval_text += f"METRIK RATA-RATA:\n"
            eval_text += f"{'-'*100}\n"
            for metric, value in evaluation.items():
                eval_text += f"{metric:30s}: {value:.4f}\n"
            
            eval_text += f"\n{'='*100}\n"
            eval_text += f"DETAIL PER QUERY\n"
            eval_text += f"{'='*100}\n\n"
            
            evaluator = IREvaluator()
            
            for i, result in enumerate(results, 1):
                eval_text += f"Query {i}: {result['query']}\n"
                eval_text += f"{'-'*100}\n"
                
                retrieved_set = set(result['retrieved'])
                relevant = result['relevant']
                
                precision = evaluator.precision(retrieved_set, relevant)
                recall = evaluator.recall(retrieved_set, relevant)
                f1 = evaluator.f1_score(precision, recall)
                ap = evaluator.average_precision(result['retrieved'], relevant)
                
                eval_text += f"  Retrieved: {result['retrieved'][:10]}\n"
                eval_text += f"  Relevant : {sorted(relevant)}\n"
                eval_text += f"  Precision: {precision:.4f}\n"
                eval_text += f"  Recall   : {recall:.4f}\n"
                eval_text += f"  F1-Score : {f1:.4f}\n"
                eval_text += f"  Avg Prec : {ap:.4f}\n\n"
            
            self.results_text.insert(tk.END, eval_text)
            self.status_var.set("Evaluasi selesai")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error saat evaluasi: {str(e)}")
            self.status_var.set("Error")
            print(f"Evaluation error: {e}")

    def rebuild_index_dialog(self):
        """Dialog untuk membangun ulang index dengan parameter kustom"""
        try:
            from tkinter import simpledialog
            
            # Minta input min_df
            min_df = simpledialog.askinteger(
                "Rebuild Index", 
                "Masukkan Document Frequency Threshold (min_df):\n\n" +
                "Term yang muncul di kurang dari N dokumen akan dihapus.\n" +
                "Semakin besar angka, semakin agresif seleksi fiturnya.",
                parent=self.root,
                minvalue=1,
                maxvalue=20,
                initialvalue=2
            )
            
            if min_df is None:
                return  # Cancelled
                
            confirm = messagebox.askyesno(
                "Konfirmasi", 
                f"Index akan dibangun ulang dengan min_df={min_df}.\nProses ini mungkin memakan waktu. Lanjutkan?"
            )
            
            if not confirm:
                return
                
            # Update status
            self.status_var.set("Membangun ulang index...")
            self.root.update()
            
            # Paths
            base_dir = os.path.dirname(os.path.abspath(__file__))
            data_dir = os.path.join(base_dir, 'data')
            docs_path = os.path.join(data_dir, 'documents.json')
            index_path = os.path.join(data_dir, 'inverted_index.pkl')
            
            # Rebuild
            # Pass data_dir to scan all files
            self.inverted_index = build_index_from_documents(data_dir, index_path, min_df=min_df)
            
            # Re-init dependent components
            self.tfidf_calculator = TFIDFCalculator(self.inverted_index)
            self.search_engine = SearchEngine(self.inverted_index, self.tfidf_calculator)
            
            # Show stats
            self.show_index_stats()
            self.status_var.set(f"Index berhasil dibangun ulang (min_df={min_df})")
            
            messagebox.showinfo("Sukses", "Index berhasil diperbarui dengan konfigurasi Seleksi Fitur baru!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membangun index: {str(e)}")
            self.status_var.set("Error")

def main():
    """Main function"""
    print("="*80)
    print("Sistem Pencarian & Ekstraksi Dokumen Pemanasan Global")
    print("="*80)
    print()
    
    # Create GUI
    root = tk.Tk()
    app = IRSystemGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
