# Catatan Perubahan

## Lokalisasi dari proyek Manus

- Melanjutkan folder, dataset, tabel `fact_sales`, definisi penjualan positif, 12 topik SQL, delapan tema visual, serta notebook eksplorasi.
- Membaca ulang dua lembar sumber UCI dan memperinci audit nilai kosong, aturan eksklusi, tanggal, invoice, dan wilayah.
- Mengganti format penyimpanan antara dari CSV besar ke Parquet bertipe, dengan alias `Revenue` yang tetap dalam GBP.
- Menambahkan nilai asli GBP berpresisi tetap, nilai IDR, konfigurasi kurs, metadata kurs pada Parquet, dan tabel kurs di DuckDB.
- Mengalihkan pengambilan agregat dashboard ke DuckDB, menerapkan parameter tanggal dan wilayah, serta membangun ulang tampilan dan grafik Plotly dalam bahasa Indonesia.
- Mengganti peringkat deskripsi dengan volume per kode SKU, memakai rentang IDR pada distribusi nilai invoice, dan memisahkan periode penuh serta parsial dalam interpretasi.
- Memperluas rekonsiliasi Python dan SQL, pengujian filter, dan pemeriksaan kondisi tanpa hasil.
- Menampilkan bulan tanpa transaksi sebagai nol dalam tren yang difilter.
- Menambahkan panduan Windows, panduan belajar dan wawancara, ringkasan eksekutif, serta tangkapan layar terbaru.

File di `data/processed/` disertakan agar ZIP langsung dapat dijalankan. Parquet dan DuckDB dibuat ulang dari sumber yang sama. Arsip mentah berasal dari UCI dan dapat diunduh saat membangun ulang. Penggunaan proyek tetap lokal. Publikasi atau deployment memerlukan keputusan pengguna.
