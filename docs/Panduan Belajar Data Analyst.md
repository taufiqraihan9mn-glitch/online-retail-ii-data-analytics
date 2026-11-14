# Panduan Belajar Data Analyst

Mulai dari dashboard selama 15 menit. Buka periode penuh, ubah negara ke Prancis, pilih November 2011, lalu bandingkan total dan jumlah invoice dengan ringkasan awal. Coba bulan yang tidak berisi transaksi pada wilayah kecil untuk melihat cara aplikasi menangani hasil kosong.

## 1. Telusuri satu baris

Di `src/pipeline.py`, fungsi `load_source` membaca dua lembar Excel dan menggabungkannya dengan `pd.concat`. Fungsi `clean_source` memakai serangkaian masker boolean, yaitu deret nilai benar/salah yang menunjukkan baris mana yang memenuhi suatu kondisi. Lihat urutannya pada `reports/Hasil Audit.md`.

Gunakan contoh sebenarnya dari invoice `489434`, SKU `85048`. Kalikan 12 unit × GBP 6,95 untuk memperoleh GBP 83,40. Setelah konversi analitis, nilainya Rp2.010.065,10. Temukan contoh ini di DuckDB, lalu coba cari satu invoice lain yang berisi banyak baris.

## 2. Baca tabel dengan pandas

DataFrame adalah tabel dalam memori. Gunakan Parquet yang tersedia di paket supaya latihan pertama berlangsung cepat, tanpa membaca ulang buku kerja Excel. Pada terminal Python dari folder proyek, coba contoh berikut.

```python
import pandas as pd

sales = pd.read_parquet(
    "data/processed/fact_sales.parquet",
    columns=["Invoice", "CountryLabel", "RevenueIDR", "CustomerID"],
)
subset = sales.loc[sales["CountryLabel"].eq("Prancis")]
print(subset.head())
print(subset["Invoice"].nunique())
print(subset["RevenueIDR"].sum())
print(subset["CustomerID"].isna().mean())
```

`loc` memilih baris, `nunique` menghitung nilai unik, dan `isna().mean()` menghitung proporsi nilai kosong. Untuk latihan berikutnya, hitung penjualan per negara dengan `groupby` dan bandingkan urutan hasil dengan SQL Q03. Gunakan `notebooks/exploratory_analysis.ipynb` untuk eksplorasi per sel. [Cara menyiapkan notebook di Windows 11](Panduan%20Instalasi%20Windows%2011.md#5-buka-notebook-latihan-di-vs-code)

## 3. Tulis SQL untuk pertanyaan yang sama

Mulai dari `FROM` untuk memilih sumber, lalu `WHERE` untuk memilih baris, kemudian `SELECT` untuk menentukan kolom atau agregat. Contoh berikut merupakan definisi invoice dan penjualan pada filter November 2011 di Prancis.

```sql
SELECT COUNT(DISTINCT Invoice) AS transaksi,
       SUM(RevenueIDR) AS penjualan_idr
FROM fact_sales
WHERE CountryLabel = 'Prancis'
  AND InvoiceDate >= DATE '2011-11-01'
  AND InvoiceDate < DATE '2011-12-01';
```

Hasilnya **64 invoice** dan **Rp763.930.061,56** pada tampilan. Untuk menjalankan SQL melalui Python, buka koneksi seperti contoh berikut.

```python
import duckdb

with duckdb.connect("data/processed/retail.duckdb", read_only=True) as db:
    print(db.sql("SELECT COUNT(DISTINCT Invoice) FROM fact_sales").fetchone())
```

Lanjutkan ke Q02 dan Q12 di `sql/business_queries.sql`. CTE adalah hasil sementara yang diberi nama dengan `WITH`. `LAG` mengambil nilai baris sebelumnya menurut urutan tertentu. `JOIN` menghubungkan dua hasil. Pada Q12, kedua sisi diringkas per negara sebelum digabungkan. Coba periksa kembali jumlah baris dan total penjualan setelah JOIN untuk memastikan nilai tidak tergandakan.

## 4. Pahami aplikasi dan grafik

Streamlit menyediakan filter, KPI, dan tab. Setelah Anda mengubah filter, skrip dievaluasi kembali. `aggregate` menjalankan kueri dengan parameter dan menyimpan hasil agregat berdasarkan periode serta negara yang sama. Plotly menerima nilai hasil agregasi dan merender grafik interaktif.

Dalam tren bulanan, perhatikan November 2010 dan November 2011. Pada kontribusi wilayah, perhatikan bahwa 10 batang terbesar masih memakai total seluruh wilayah sebagai penyebut. Untuk sebaran transaksi, satu invoice hanya masuk satu rentang. Pada grafik pelanggan bersumbu log, jarak antartitik mencerminkan rasio skala, dan titik bertumpuk dapat menutupi kepadatan.

## 5. Siapkan cerita wawancara

Dalam 90 detik, jelaskan pertanyaan bisnis, cara membersihkan data, hasil utama, lalu batasan. Tunjukkan satu filter dan satu kueri yang angkanya cocok. Sebagai contoh, Anda dapat menjelaskan bahwa Britania Raya menyumbang 85,03% penjualan positif dan hampir seperempat baris positif tidak memiliki ID pelanggan. Ceritakan kontribusi Anda berdasarkan bagian yang sudah Anda jalankan dan dapat jelaskan sendiri. Proyek ini dikembangkan dari paket awal Manus dengan bantuan ChatGPT.

## Pertanyaan dan contoh jawaban

| Pertanyaan | Contoh jawaban |
| --- | --- |
| 1. Apa tujuan proyek ini? | Mengukur pola penjualan positif, kontribusi negara, volume produk, dan pembelian ulang dari periode Online Retail II. |
| 2. Apa yang dimaksud grain tabel? | Satu baris adalah satu baris penjualan sumber yang dipertahankan. Invoice dapat muncul beberapa kali jika ada beberapa produk atau baris pesanan. |
| 3. Bagaimana merekonsiliasi jumlah baris? | Dari 1.067.371 baris sumber, 59.458 dikeluarkan. Saya menjumlahkan eksklusi setelah filter sebelumnya, sehingga satu baris dihitung sekali. |
| 4. Bagaimana menangani duplikat? | Aturan proyek mempertahankan satu dari baris yang identik setelah parsing. Karena tidak ada ID baris asli, ada kemungkinan beberapa duplikat merupakan pesanan yang sah. |
| 5. Apa yang dilakukan pada ID pelanggan kosong? | Saya mempertahankan barisnya untuk total penjualan. Analisis pelanggan memakai ID yang tersedia. Ada 228.488 baris positif tanpa ID. |
| 6. Bagaimana menghitung revenue proyek dan AOV? | Nilai penjualan positif adalah jumlah dari kuantitas × harga baris yang lolos filter. AOV adalah total tersebut dibagi 40.077 invoice unik pada periode penuh. |
| 7. Bagaimana memastikan IDR dihitung dengan benar? | Saya memakai kurs tetap Rp24.101,50 per GBP dari Bank Indonesia, menyimpan desimal penuh, dan memeriksa ulang semua baris dengan SQL. |
| 8. Mengapa kursnya sama di semua tahun? | Tujuannya menyajikan analisis dalam Rupiah dengan satu skala perbandingan. Tanggal kurs 13 November 2026 berbeda dari periode transaksi, sehingga IDR adalah konversi analitis. |
| 9. Apa keputusan utama tentang kode produk? | Saya memakai pola SKU dan mengurutkan jumlah unit. Kode ongkir dan manual dikecualikan dari grafik produk, dengan kemungkinan sejumlah kode barang khusus ikut terlewat. |
| 10. Bagaimana menghindari penggandaan baris ketika JOIN? | Pada Q12 saya membuat dua ringkasan yang masing-masing memiliki satu baris per negara, lalu menggunakan LEFT JOIN dan membandingkan total sesudahnya. |
| 11. Apa interpretasi pola bulanan? | November 2011 adalah puncak hasil. Desember 2011 hanya tersedia sampai tanggal 9, jadi saya memeriksa durasi sebelum membandingkannya dengan bulan lengkap. |
| 12. Bagaimana menunjukkan hasil dapat direproduksi? | Saya menjalankan ulang tahap sumber UCI, Parquet, DuckDB, rekonsiliasi, pengujian SQL, dan tes dashboard. Filter November 2011 untuk Prancis menghasilkan 64 invoice di SQL dan dashboard. |

Latihan presentasi. Tampilkan empat KPI, jelaskan mengapa penjualan positif berbeda dari penghitungan laba, ganti filter ke Prancis, lalu tunjukkan hasil kueri November 2011. Akhiri dengan langkah yang akan Anda ambil bila diberi data retur dan katalog SKU.
