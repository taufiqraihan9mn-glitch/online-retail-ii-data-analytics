# Metodologi Analisis

## Pertanyaan analisis

Bagaimana nilai penjualan positif berubah dari waktu ke waktu, seberapa terkonsentrasi menurut wilayah, SKU apa yang memiliki volume terbesar, dan berapa banyak pelanggan teridentifikasi yang membeli lebih dari satu kali?

## Alur data

1. **Ekstraksi.** `src/pipeline.py` membaca semua lembar buku kerja `online_retail_II.xlsx` di dalam ZIP resmi UCI. Nama kolom diperiksa pada setiap lembar sebelum penggabungan.
2. **Pembersihan.** Tanggal, kuantitas, harga, dan ID diparsing. Duplikat persis setelah parsing empat kolom tersebut dihapus lintas lembar. Aturan berikutnya diterapkan berurutan. Abaikan invoice berawalan C, baris wajib yang tidak valid, kuantitas nonpositif, dan harga nonpositif. ID yang hilang tetap dipertahankan untuk agregat penjualan. Duplikat identik mungkin merepresentasikan baris pemesanan yang sah karena dataset tidak memiliki nomor baris invoice. Perlakuan ini meneruskan asumsi Manus.
3. **Transformasi.** Hitung nilai baris dari kuantitas dan harga sumber. Python mengalikan dalam seperseribu GBP sebagai bilangan bulat. Turunkan nilai IDR dengan kurs tetap dalam tipe desimal. Negara asli disalin, sedangkan label dashboard memakai padanan bahasa Indonesia. Seri atau wilayah nonnegara dari sumber, misalnya Komunitas Eropa, tetap merupakan kategori terpisah.
4. **Penyimpanan.** Tulis fakta Parquet, laporan audit, serta KPI pandas. Buat DuckDB dari Parquet sesuai skema SQL. Kurs yang tertanam pada Parquet ikut masuk ke tabel `exchange_rate`. Kueri rekonsiliasi memeriksa setiap rumus moneter pada semua baris.
5. **Penyajian.** Streamlit membuka DuckDB dalam mode baca, menerapkan filter, dan membangun tabel sementara pada koneksi tersebut. Basis data mengagregasi hasil. pandas mengemasnya untuk Plotly. Filter tanggal memakai batas awal inklusif dan awal hari berikutnya sebagai batas akhir eksklusif.

## Delapan visualisasi

| Grafik | Cara membaca dan batasan |
| --- | --- |
| Penjualan bulanan | Membaca pergerakan nilai positif dalam IDR. Bulan tanpa penjualan dalam filter ditampilkan sebagai nol. Ujung rentang bisa memuat bulan parsial. |
| Transaksi bulanan | Menghitung nomor invoice unik per bulan, dengan tanggal dari baris sumber. Bulan tanpa invoice dalam filter ditampilkan sebagai nol. |
| Kontribusi wilayah | Menampilkan maksimal 10 wilayah. Penyebut mencakup seluruh wilayah dalam filter sehingga batang yang ditampilkan dapat berjumlah kurang dari 100%. |
| Produk terlaris | Menjumlahkan kuantitas per `ProductCode`, yakni kode sumber setelah trim dan kapitalisasi yang memenuhi pola lima digit dengan 0–3 huruf. Pola membantu mengeluarkan kode ongkir dan manual serta dapat mengeluarkan barang berkode khusus. Grafik menampilkan kode agar dapat dicocokkan dengan katalog historis sumber. |
| Penjualan menurut hari | Menjumlahkan nilai per hari dalam sepekan. Jumlah kemunculan setiap hari dapat berbeda pada rentang pendek. |
| Sebaran nilai transaksi | Satu invoice masuk ke satu dari empat rentang Rupiah. Angka dihitung dari baris yang lolos filter dan tidak dipotong pada persentil tertentu. |
| Frekuensi dan nilai pelanggan | Setiap titik adalah satu ID pelanggan pada sumbu log. Jarak yang sama pada sumbu log menunjukkan rasio yang sama. |
| Segmen jumlah transaksi | Mengelompokkan pelanggan menjadi satu, dua sampai lima, dan enam transaksi atau lebih dalam filter. |

## Interpretasi bisnis

Total KPI mencakup semua baris positif yang memenuhi kriteria, termasuk sebagian biaya atau penyesuaian berkode khusus. Hasil berfokus pada pola historis dan memerlukan katalog produk, detail retur, biaya, serta cakupan konsisten untuk analisis margin atau kebijakan operasional. Kode pelanggan yang sama dapat terlihat di beberapa wilayah sehingga penjumlahan pelanggan per wilayah dapat melebihi jumlah keseluruhan.
