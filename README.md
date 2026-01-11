# Sistem Pencarian & Ekstraksi Dokumen Pemanasan Global
## Information Retrieval System

### Deskripsi
Sistem Information Retrieval (IR) untuk pencarian dan ekstraksi dokumen tentang pemanasan global. Sistem ini menggunakan teknik data mining dan IR untuk memproses, mengindeks, dan mencari dokumen dengan efisien.

### Fitur Utama
1. **Preprocessing Teks**
   - Tokenisasi
   - Case Folding
   - Stopword Removal
   - Stemming (Bahasa Indonesia)

2. **Indexing**
   - Inverted Index
   - TF-IDF Calculation
   - Document Vector Representation

3. **Retrieval/Search**
   - Vector Space Model (Cosine Similarity)
   - Boolean Search (AND/OR)
   - Ranked Retrieval

4. **Extraction**
   - Keyword Extraction
   - Text Summarization
   - Entity Recognition
   - Statistical Information Extraction

5. **Evaluation**
   - Precision, Recall, F1-Score
   - Average Precision (AP)
   - Mean Average Precision (MAP)
   - Precision@K, Recall@K

### Struktur Folder
```
Global_Warming/
├── data/                      # Data dokumen dan index
│   ├── documents.json         # Koleksi dokumen
│   ├── stopwords_id.txt      # Stopwords bahasa Indonesia
│   └── inverted_index.pkl    # Index (generated)
├── preprocessing/             # Modul preprocessing
│   └── text_processor.py
├── indexing/                  # Modul indexing
│   └── indexer.py
├── retrieval/                 # Modul retrieval
│   └── search_engine.py
├── extraction/                # Modul extraction
│   └── extractor.py
├── evaluation/                # Modul evaluation
│   └── evaluator.py
├── main.py                    # Program utama dengan GUI
└── README.md                  # Dokumentasi
```

### Requirements
```
Python 3.7+
tkinter (biasanya sudah terinstall)
Sastrawi (untuk stemming bahasa Indonesia)
```

### Instalasi

1. Clone atau download repository

2. Install dependencies:
```bash
pip install Sastrawi
```

### Cara Menggunakan

#### 1. Menjalankan Program Utama (GUI)
```bash
python main.py
```

Program akan:
- Membuat atau memuat inverted index
- Membuka GUI untuk pencarian

#### 2. Testing Modul Individual

**Preprocessing:**
```bash
cd preprocessing
python text_processor.py
```

**Indexing:**
```bash
cd indexing
python indexer.py
```

**Retrieval:**
```bash
cd retrieval
python search_engine.py
```

**Extraction:**
```bash
cd extraction
python extractor.py
```

**Evaluation:**
```bash
cd evaluation
python evaluator.py
```

### Penggunaan GUI

1. **Pencarian Dokumen:**
   - Masukkan query di field "Query"
   - Pilih metode pencarian (Vector Space/Boolean AND/Boolean OR)
   - Tentukan jumlah hasil yang diinginkan
   - Klik "Cari" atau tekan Enter

2. **Melihat Statistik Index:**
   - Klik tombol "Statistik Index"
   - Melihat informasi tentang jumlah dokumen, terms, dll

3. **Evaluasi Sistem:**
   - Klik tombol "Evaluasi Sistem"
   - Sistem akan menjalankan test queries dan menampilkan metrics

4. **Lihat Semua Dokumen:**
   - Klik tombol "Lihat Semua Dokumen"
   - Menampilkan daftar lengkap dokumen dalam koleksi

### Contoh Query
- "pemanasan global efek rumah kaca"
- "energi terbarukan solusi"
- "dampak perubahan iklim"
- "emisi karbon transportasi"
- "pencairan es kutub"

### Metode Pencarian

**1. Vector Space Model**
- Menggunakan TF-IDF dan Cosine Similarity
- Ranking berdasarkan similarity score
- Recommended untuk most queries

**2. Boolean AND**
- Mengembalikan dokumen yang mengandung SEMUA query terms
- Cocok untuk pencarian spesifik

**3. Boolean OR**
- Mengembalikan dokumen yang mengandung SALAH SATU query terms
- Cocok untuk pencarian broad/luas

### Evaluasi Metrics

- **Precision**: Proporsi dokumen retrieved yang relevan
- **Recall**: Proporsi dokumen relevan yang ter-retrieve
- **F1-Score**: Harmonic mean dari Precision dan Recall
- **Average Precision (AP)**: Rata-rata precision pada setiap posisi dokumen relevan
- **MAP**: Mean Average Precision untuk multiple queries

### Dataset
Dataset berisi 15 dokumen tentang pemanasan global dengan topik:
- Konsep dasar pemanasan global
- Penyebab pemanasan global
- Dampak pada iklim dan ekosistem
- Solusi (energi terbarukan, transportasi, dll)
- Kebijakan internasional
- Adaptasi dan mitigasi

### Algoritma & Teknik

**Preprocessing:**
- Tokenization menggunakan whitespace splitting
- Sastrawi Stemmer untuk bahasa Indonesia
- Stopword removal dengan daftar stopwords Indonesia

**Indexing:**
- Inverted Index: term → [(doc_id, frequency), ...]
- TF-IDF: tf(t,d) × idf(t) = (freq/doc_length) × log(N/df)

**Retrieval:**
- Cosine Similarity: sim(q,d) = (q·d) / (||q|| × ||d||)
- Boolean operators untuk filtering

**Extraction:**
- Frequency-based keyword extraction
- TF-IDF-based keyword extraction
- Extractive summarization

### Troubleshooting

**Error: ModuleNotFoundError: No module named 'Sastrawi'**
```bash
pip install Sastrawi
```

**Error: File documents.json tidak ditemukan**
- Pastikan menjalankan dari root directory (Global_Warming/)
- Pastikan file data/documents.json ada

**GUI tidak muncul:**
- Pastikan tkinter terinstall (biasanya default dengan Python)
- Di Linux: `sudo apt-get install python3-tk`

### Pengembangan Lebih Lanjut

Fitur yang bisa ditambahkan:
1. Query expansion dengan synonym
2. Relevance feedback
3. Clustering dokumen
4. Visualisasi (word cloud, similarity graph)
5. Export hasil pencarian
6. Web-based interface
7. More sophisticated NER
8. Machine learning untuk ranking

### Kontributor
- Sistem dikembangkan untuk Tugas Data Mining
- Topik: Penerapan IR dalam Sistem Pencarian & Ekstraksi Dokumen

### Lisensi
Educational Purpose

---
© 2025 - Information Retrieval System for Global Warming Documents
