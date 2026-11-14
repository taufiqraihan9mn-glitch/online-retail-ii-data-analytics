# Data Online Retail II

Sumber: Chen, D. (2012). *Online Retail II* [Dataset]. UCI Machine Learning Repository. DOI 10.24432/C5CG6D, CC BY 4.0. Dataset berisi transaksi historis ritel daring yang berbasis di Britania Raya. Data olahan pada proyek ini menghapus duplikat dan baris di luar definisi penjualan positif serta menambahkan label negara dan konversi IDR.

- [Katalog sumber dan lisensi](https://archive.ics.uci.edu/dataset/502/online+retail+ii)
- [Unduh ZIP resmi UCI](https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip)

Simpan unduhan sebagai `data/raw/online_retail_ii.zip` tanpa mengekstrak berkas Excel dari dalamnya, atau jalankan `python -m src.pipeline --unduh`. Arsip mentah berukuran sekitar 43,5 MiB. SHA-256 unduhan yang diuji adalah `572e36277c2390fbfde10664750731e0a86f55e33470d91919085f0408e67bfb`. Laporan audit mencatat hash untuk setiap proses.

`data/processed/fact_sales.parquet` memuat fakta penjualan dan metadata kurs. `retail.duckdb` menyediakan tabel analisis yang bisa dibuka secara lokal. Paket unduhan menyertakan keduanya. `.gitignore` mengecualikan arsip mentah, Parquet, dan DuckDB dari kontrol versi. Sebelum mengunggah kode, hapus berkas pribadi tambahan yang mungkin Anda simpan di folder proyek. Dataset memakai pengenal pelanggan dari sumber publik.
