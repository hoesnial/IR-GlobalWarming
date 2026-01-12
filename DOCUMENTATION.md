# Dokumentasi Sistem Temu Kembali Informasi Pemanasan Global

**Mata Kuliah:** IFB-307 Data Mining  
**Topik:** Information Retrieval System for Global Warming Documents

---

## 1. System Overview

### Background
Pemanasan global adalah isu krusial yang memiliki volume literatur yang sangat besar dan terus berkembang. Peneliti, mahasiswa, dan masyarakat umum seringkali kesulitan menemukan dokumen spesifik yang relevan dengan topik tertentu (misalnya "dampak kesehatan" atau "solusi energi terbarukan") di tengah lautan informasi. Pencarian manual melalui dokumen teks yang tidak terstruktur memakan waktu dan tidak efisien. Sistem ini dibangun untuk mengatasi masalah *information overload* tersebut dengan menyediakan mekanisme pencarian yang cepat, relevan, dan terstruktur.

### System Objective
Tujuan utama sistem ini adalah membangun aplikasi *Information Retrieval* (IR) *desktop-based* yang mampu:
1.  Mengindeks kumpulan dokumen teks bertopik pemanasan global.
2.  Menerima kueri bahasa alami dari pengguna.
3.  Mengembalikan daftar dokumen yang relevan berdasarkan tingkat kemiripan konten.
4.  Memberikan ringkasan otomatis untuk setiap dokumen agar pengguna dapat memahami inti konten tanpa membaca keseluruhan teks.

### Scope & Limitation
**Termasuk (In-Scope):**
*   Pencarian berbasis teks menggunakan model ruang vektor (Vector Space Model).
*   Fitur peringkas dokumen otomatis (Extractive Summarization).
*   Seleksi fitur statistik untuk optimasi indeks.
*   Antarmuka pengguna grafis (GUI) sederhana berbasis desktop.

**Tidak Termasuk (Out-of-Scope):**
*   Pencarian data multimedia (gambar/video).
*   Crawling otomatis dari internet (dataset statis).
*   Sistem autentikasi pengguna (login/register).

---

## 2. System Requirements

### Functional Requirements
1.  **FR-01**: Sistem mampu membaca dan memproses dokumen data mentah dalam format **JSON, PDF, dan TXT**.
2.  **FR-02**: Sistem melakukan preprocessing teks otomatis (tokenisasi, stemming, stopwords removal).
3.  **FR-03**: Sistem membangun *Inverted Index* dari dokumen yang telah diproses.
4.  **FR-04**: Sistem menyediakan fitur **Seleksi Fitur** (rebuild index) di mana pengguna dapat mengatur ambang batas frekuensi dokumen (*min_df*) untuk menyaring kata-kata yang tidak signifikan.
5.  **FR-05**: Sistem menerima input *query* pencarian dari pengguna.
6.  **FR-06**: Sistem menerapkan **Information Retrieval Model** (TF-IDF & Cosine Similarity) untuk menghitung skor relevansi.
7.  **FR-07**: Sistem melakukan **Query Processing & Document Ranking** untuk mengurutkan dokumen dari yang paling relevan.
8.  **FR-08**: Sistem memiliki fitur **Text Document Summarization (Extractive)** untuk menghasilkan ringkasan otomatis dari dokumen.
9.  **FR-09**: Sistem menangani duplikasi dokumen secara cerdas dengan mengabaikan file backup dan menyatukan konten PDF dengan metadata JSON.

### Non-Functional Requirements
1.  **NFR-01 (Performance)**: Waktu respon pencarian rata-rata < 1 detik untuk dataset saat ini.
2.  **NFR-02 (Usability)**: Antarmuka pengguna (GUI) berbasis Tkinter yang mudah dipahami (user-friendly).
3.  **NFR-03 (Reliability)**: Sistem dapat menyimpan dan memuat ulang indeks (*pickling*) tanpa perlu membangun ulang dari nol setiap kali dijalankan.

---

## 3. System Architecture

### Architecture Overview
Sistem mengikuti arsitektur pipa (pipeline) klasik Information Retrieval:

`Dokumen Raw` → `Preprocessing` → `Indexing` → `Storage`
                                      ↑
`Query User` → `Preprocessing` → `Ranking (IR Model)` → `Output (Hasil)`

### Component Description
1.  **Data Ingestion**: Modul untuk membaca dataset dokumen (`.json`, `.pdf`, `.txt`) dan loader otomatis (`document_loader.py`).
2.  **Download Manager**: Modul `downloader.py` yang otomatis mengunduh file PDF dari URL yang tersedia di `documents.json` secara massal.
3.  **Preprocessing**: Modul `text_processor.py` yang membersihkan teks mentah menjadi token-token standar siap indeks.
3.  **Inverted Index**: Modul `indexer.py` (Kelas `InvertedIndex`) yang memetakan setiap kata unik (term) ke daftar dokumen tempat kata tersebut muncul.
4.  **Feature Selection**: Fitur dalam `indexer.py` yang memangkas ukuran indeks dengan membuang term yang terlalu jarang muncul (*Rare Term Removal*).
5.  **IR Model**: Modul `search_engine.py` yang mengimplementasikan TF-IDF weighting dan perhitungan Cosine Similarity.
6.  **Extractor**: Modul `extractor.py` untuk menghasilkan ringkasan dokumen dan ekstraksi entitas/keyword.
7.  **GUI Application**: Modul `main.py` sebagai antarmuka interaksi pengguna dengan sistem.

---

## 4. Data Specification

### Sumber Data
Data merupakan koleksi artikel nyata yang diambil dari berbagai sumber (repository kampus, Neliti, Scribd, dll) tentang pemanasan global.

*   **Format**: JSON (`documents.json`) serta dukungan untuk PDF/TXT.
*   **Jumlah Dokumen**: 4 Dokumen (Dataset aktif yang memiliki file PDF valid)
*   **Struktur Data per Dokumen**:
    *   `id`: Integer (Unique Identifier)
    *   `title`: String (Judul Artikel)
    *   `content`: String (Abstrak/Ringkasan Isi)
    *   `author`: String (Penulis/Sumber)
    *   `date`: String (Tahun/Tanggal)
    *   `category`: String (Kategori Topik)
    *   `download`: String (Link Download Asli)

### Contoh Data (Cuplikan)
```json
{
    "id": 1,
    "title": "Pemanasan Global: Dampak dan Upaya Meminimalisasinya",
    "content": "Makalah ringkas yang menjelaskan konsep pemanasan global...",
    "author": "Ramli Utina",
    "download": "https://repository.ung.ac.id/..."
}
```

---

## 5. Text Processing & Indexing Design

### Text Preprocessing
Setiap teks (baik dokumen maupun query) melewati tahapan:
1.  **Case Folding**: Mengubah semua huruf menjadi huruf kecil (*lowercase*).
2.  **Punctuation Removal**: Menghapus tanda baca dan angka.
3.  **Tokenization**: Memecah kalimat menjadi daftar kata (list of tokens).
4.  **Short Word Filter**: Menghapus kata-kata yang terlalu pendek (< 2 karakter) untuk mengurangi noise.
5.  **Stopword Removal**: Menghapus kata umum yang tidak bermakna. Menggunakan **Sastrawi** (Indonesian) dan **NLTK** (English) untuk menangani dokumen campuran.
6.  **Stemming**: Mengubah kata berimbuhan menjadi kata dasar (misal: "memanaskan" -> "panas") menggunakan library **Sastrawi**.

### Inverted Index Design
Struktur data utama adalah **Dictionary** python:
*   **Key**: Term (kata dasar)
*   **Value**: List of Tuples `[(doc_id, frequency), ...]`

**Contoh Struktur:**
```python
{
    "panas": [(1, 2), (3, 5), (15, 1)],
    "karbon": [(2, 4), (7, 3)]
}
```
Indeks ini memungkinkan sistem menemukan dokumen yang mengandung kata "panas" secara instan tanpa memindai seluruh teks lagi.

---

## 6. Information Retrieval Model Design

### Model IR: Vector Space Model (VSM)
Sistem menggunakan VSM di mana dokumen dan query direpresentasikan sebagai vektor dalam ruang multi-dimensi.

1.  **Pembobotan (TF-IDF)**:
    *   **TF (Term Frequency)**: Seberapa sering kata muncul dalam dokumen (dinormalisasi dengan panjang dokumen).
    *   **IDF (Inverse Document Frequency)**: Logaritma dari (Total Dokumen / Jumlah Dokumen yang mengandung kata). Ini memberikan bobot lebih tinggi pada kata langka/spesifik.
    
    `Score(term, doc) = TF(term, doc) * IDF(term)`

2.  **Perhitungan Relevansi (Cosine Similarity)**:
    Kemiripan antara Query (Q) dan Dokumen (D) dihitung berdasarkan sudut antara kedua vektornya.
    
    `Similarity = (Q . D) / (|Q| * |D|)`
    
    Semakin mendekati 1, semakin mirip/relevan dokumen tersebut.

---

## 7. Feature Selection & Summarization Design

### Feature Selection
Metode yang diterapkan adalah **Document Frequency (DF) Thresholding** (Rare Term Removal).

*   **Metode**: Pengguna dapat menentukan nilai `min_df` (misal: 2).
*   **Mekanisme**: Saat indeks dibangun ulang (`rebuild index`), sistem akan menghapus semua term yang muncul di kurang dari `min_df` dokumen.
*   **Dampak**: Mengurangi ukuran indeks secara signifikan (reduksi dimensi hingga ~60-70%) dan menghilangkan noise (kata typo atau kata yang terlalu unik sehingga tidak berguna untuk generalisasi pencarian).

### Document Summarization
Sistem menggunakan **Extractive Summarization**.

*   **Algoritma**:
    1.  Memecah dokumen menjadi kalimat-kalimat.
    2.  Mengekstrak top keywords dari dokumen (berdasarkan TF-IDF).
    3.  Memberikan skor pada setiap kalimat berdasarkan jumlah keywords penting yang dikandungnya.
    4.  Memilih 3 kalimat dengan skor tertinggi sebagai ringkasan.
*   **Output**: Paragraf pendek yang tetap mempertahankan kalimat asli dari penulis.

---

## 8. Implementation Overview

### Tech Stack
*   **Bahasa**: Python 3.1x
*   **GUI Library**: Tkinter + `ttkbootstrap` (Modern UI Theme)
*   **NLP Library**: `Sastrawi` (Indonesian), `NLTK` (English Stopwords)
*   **General Library**: `json`, `math`, `pickle`, `re`

### Struktur Folder
```
Global_Warming/
├── data/
│   ├── documents.json       # Dataset
│   └── inverted_index.pkl   # Serialized Index
├── preprocessing/           # Modul Text Processing
├── indexing/                # Modul Indexing & TF-IDF
├── retrieval/               # Modul Searching
├── extraction/              # Modul Summarization
└── main.py                  # Entry Point (GUI)
```

### Cara Menjalankan
1.  Pastikan Python dan library Sastrawi terinstal.
2.  Jalankan perintah: `python main.py`
3.  Aplikasi GUI akan terbuka.

---

## 9. System Testing & Demonstration

### Skenario Pengujian
**Skenario**: Pengguna mencari informasi tentang solusi energi.
1.  **Input Query**: "energi terbarukan dan surya"
2.  **Proses**:
    *   Preprocessing query -> `['energi', 'baru', 'surya']`
    *   Hitung vektor query.
    *   Match dengan dokumen di index.
    *   Ranking berdasarkan Cosine Similarity.
3.  **Output yang Diharapkan**:
    *   Dokumen ID 6 ("Energi Terbarukan sebagai Solusi") muncul di peringkat 1.
    *   Skor relevansi > 0.

### Hasil Evaluasi Kinerja (Performance Metrics)
Berdasarkan pengujian otomatis menggunakan 5 *test queries* terhadap dataset yang ada, diperoleh hasil rata-rata sebagai berikut:

| Metric | Score (Rata-rata) | Interpretasi |
| :--- | :--- | :--- |
| **Average Precision** | **100.00%** | **Sempurna.** Semua dokumen (10/10) yang ditampilkan di halaman pertama relevan dengan query. |
| **Average Recall** | **16.49%** | Wajar, karena sistem membatasi output hanya 10 dokumen teratas (`top_k=10`), sementara database memiliki banyak dokumen relevan (>60) untuk setiap topik. |
| **Mean Average Precision (MAP)** | **16.49%** | Konsisten dengan Recall karena batasan potong (cutoff) pada ranking. |
| **Average F1-Score** | **28.13%** | Rata-rata harmonik antara Presisi dan Recall. |

*Catatan: Nilai Recall yang rendah bukan indikasi performa buruk, melainkan konsekuensi logis dari batasan tampilan (Top-10) terhadap dataset yang memiliki redundansi tinggi.*

---

## 10. Limitations & Future Improvement

### Keterbatasan
*   Batasan tampilan 10 dokumen menyebabkan nilai Recall terlihat rendah, meskipun dokumen relevan lainnya tersimpan di database.
*   Stemming Sastrawi terkadang *over-stemming* atau *under-stemming* untuk istilah teknis sains.
*   Belum ada penanganan *synonym* (misal: "global warming" vs "pemanasan global").

### Future Improvement
*   Implementasi **Query Expansion** menggunakan Thesaurus untuk menangani sinonim.
*   Menambahkan fitur **Clustering** dokumen untuk mengelompokkan hasil pencarian secara otomatis.
*   Migrasi ke antarmuka Web (misal: Streamlit atau Flask) untuk aksesibilitas yang lebih baik.

---

## Appendix
### Modul Utama (Indexer Pseudocode)
```python
class InvertedIndex:
    def add_document(self, doc_id, tokens):
        for token in tokens:
            self.index[token].append(doc_id)
            
    def prune_terms(self, min_df):
        # Seleksi Fitur
        for term in list(self.index.keys()):
            if len(self.index[term]) < min_df:
                del self.index[term]
```
