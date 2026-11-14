# Laporan Pengujian

Pengujian dijalankan pada **14 November 2026** di Linux x86-64 dengan Python **3.12.14**, pandas **2.2.3**, DuckDB **1.5.6**, Streamlit **1.67.0**, Plotly **6.9.0**, dan pytest **8.4.2**. Tangkapan desktop dan ponsel diambil dengan Chromium **153.0.8010.0**.

| Cakupan | Bukti hasil |
| --- | --- |
| Sintaks Python | `python -m compileall -q src dashboard tests` selesai tanpa galat. |
| Pipeline dari awal | Direktori awal hanya berisi kode, konfigurasi, dan tes. `python -m src.pipeline --unduh` mengunduh ulang data UCI, membaca dua lembar, dan membuat 1.007.913 baris penjualan dari 1.067.371 baris sumber. |
| Pembangunan DuckDB | `python -m src.build_database` membuat skema dan mengisi basis data dari Parquet. |
| Reproduksibilitas | Empat JSON bukti pada hasil pembangunan ulang sama byte demi byte dengan yang dikemas. |
| Rekonsiliasi data lama | Perbandingan `EXCEPT ALL` terhadap CSV Manus dan tabel baru menghasilkan 0 baris berbeda di kedua arah untuk sembilan kolom asli. |
| Rekonsiliasi KPI | `python -m src.validation` mempertemukan 10 dari 10 metrik pandas dan DuckDB, termasuk total dan AOV dalam GBP dan IDR. |
| Konversi per baris | 0 dari 1.007.913 baris menyimpang pada pemeriksaan nilai GBP, harga IDR, nilai IDR, atau hubungan nilai baris dan harga satuan. Contoh dengan GBP 83,400 menghasilkan IDR 2.010.065,10000. |
| Kueri SQL | `python -m src.validate_sql_queries` mengeksekusi 12 dari 12 kueri. Uji agregat tambahan memeriksa total per negara, distribusi invoice, dan hasil JOIN. |
| Suite pengujian | `python -m pytest -q` menghasilkan 13 lulus dan 0 gagal. |
| Filter dashboard | Tanggal awal dan akhir yang sama untuk Britania Raya pada 1 Desember 2009 menghasilkan 109 invoice. Prancis pada November 2011 menghasilkan 64 invoice dan Rp763.930.061,56. |
| Hasil kosong dan data pelanggan | Uji memilih Arab Saudi pada 1 Desember 2009, memasukkan satu tanggal pada filter rentang, dan membuka Bermuda yang memiliki transaksi dengan 0 ID pelanggan. |
| Bulan kosong dalam tren | Pada filter Bermuda dari Februari hingga April 2010, dashboard menampilkan 0, 1, dan 0 invoice. Maret mencatat Rp30.202.553,71. Februari dan April bernilai nol. |
| Browser | Delapan figur dirender. Pemeriksaan pada desktop 1.440 px dan ponsel 390 px menampilkan KPI lengkap. Tampilan ponsel menggunakan satu kolom tanpa gulir horizontal pada halaman. |
| Notebook | Sel kode dijalankan berurutan dari folder proyek dengan fakta Parquet dan DuckDB yang dikemas. |

Laporan dalam format mesin tersedia di `data/processed/kpi_validation.json`, `validasi_sql.json`, `kpis.json`, dan `data_quality_report.json`. Langkah PowerShell disediakan untuk penggunaan Windows 11. Pengujian sistem operasi tersebut perlu dilakukan pada perangkat Windows pengguna.
