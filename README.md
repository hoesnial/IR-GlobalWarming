# Sistem Pencarian & Ekstraksi Dokumen Pemanasan Global

Aplikasi Information Retrieval System (IR) untuk dokumen bertopik Pemanasan Global.

## Fitur Utama
*   **Multi-Format Support**: Membaca JSON, PDF, dan TXT.
*   **Smart Downloader**: Mendownload dokumen otomatis dari internet.
*   **Search Engine**: Menggunakan Vectors Space Model (TF-IDF & Cosine Similarity).
*   **Feature Selection**: Optimasi index dengan menghapus *rare terms*.
*   **Smart Snippet**: Menampilkan konteks kata kunci di hasil pencarian.

## Dokumentasi
Dokumentasi lengkap mengenai sistem, arsitektur, dan testing dapat dilihat di:
[DOCUMENTATION.md](DOCUMENTATION.md)

## Cara Menjalankan
```bash
pip install -r requirements.txt
python main.py
```
