# Hasil Audit

## Rekonsiliasi jumlah baris

| Tahap atau kejadian | Jumlah baris |
| --- | ---: |
| Lembar `Year 2009-2010` | 525.461 |
| Lembar `Year 2010-2011` | 541.910 |
| Total sumber | 1.067.371 |
| Dihapus karena duplikat persis setelah parsing | 34.335 |
| Dihapus karena invoice pembatalan setelah deduplikasi | 19.104 |
| Dihapus karena kolom wajib tidak valid | 0 |
| Dihapus karena kuantitas nonpositif setelah tahap sebelumnya | 3.393 |
| Dihapus karena harga nonpositif setelah tahap sebelumnya | 2.626 |
| Total dikecualikan | 59.458 |
| Total fakta penjualan positif | 1.007.913 |

Pada data sumber, **19.494** baris berawalan C, **22.950** berkuantitas nonpositif, dan **6.207** berharga nonpositif. Satu baris sumber dapat masuk ke beberapa hitungan ini. Tabel tahap mencatat penyebab pertama per baris, sehingga jumlahnya bisa direkonsiliasi.

## Nilai kosong dan konsistensi

| Pemeriksaan | Temuan |
| --- | --- |
| ID pelanggan kosong | 243.007 baris sumber. Sebanyak 228.488 masih termasuk dalam total penjualan positif. |
| Deskripsi kosong | 4.382 baris sumber dan 0 baris pada fakta penjualan positif. |
| Kolom sumber lain yang kosong | 0 pada nomor invoice, kode barang, kuantitas, tanggal, harga, dan negara. |
| Tanggal tidak valid | 0 baris sumber. |
| Cakupan fakta | 1 Desember 2009 pukul 07.45 sampai 9 Desember 2011 pukul 12.50, waktu dari sumber. |
| Invoice dengan lebih dari satu cap waktu | 82 invoice dalam hari yang sama. Nol invoice lintas hari. |
| Invoice lintas negara atau dengan beberapa ID | 0 invoice lintas negara dan 0 invoice dengan lebih dari satu ID nonkosong. |
| Negara dan wilayah | 43 label pada fakta. Label “Tidak disebutkan” terdapat pada 748 baris dan berasal dari `Unspecified` pada sumber. |
| ID pelanggan lintas negara | 13 ID muncul pada lebih dari satu label wilayah. Agregat pelanggan per negara tidak aditif. |
| Kode di luar pola SKU | 4.699 baris positif senilai Rp20.090.246.334,25. Baris ini tercakup pada KPI keseluruhan. |
| Presisi GBP | 18 baris memerlukan tiga desimal pada nilai baris. |
| Pemeriksaan rumus moneter | 0 dari 1.007.913 baris menyimpang dari persamaan GBP dan IDR. |

## Temuan dari proyek awal

- Label “net revenue” menggambarkan baris penjualan positif. Label dan laporan sekarang memakai istilah **penjualan positif**.
- Tiga dari entri besar pada peringkat nilai berbasis deskripsi adalah `Manual`, `DOTCOM POSTAGE`, dan `POSTAGE`. Peringkat terlaris sekarang memakai total unit per kode berpola SKU.
- Perbandingan bulan pertama dan terakhir dikeluarkan dari KPI. Bulan Desember 2011 hanya mencakup tanggal 1–9.
- Laporan awal memeriksa tiga KPI utama. Audit ini menghitung ulang sepuluh metrik, memeriksa persamaan untuk semua baris, dan menjalankan 12 kueri analisis.
- Pembanding CSV Manus direkonsiliasi sebagai kumpulan baris dengan kolom asli, termasuk GBP pada tiga desimal dan spasi kode sumber. Nominal, jumlah baris, dan definisi penjualan positif Manus dipertahankan.

Bukti yang dapat diperiksa ada di `data/processed/data_quality_report.json`, `kpi_validation.json`, dan `validasi_sql.json`.
