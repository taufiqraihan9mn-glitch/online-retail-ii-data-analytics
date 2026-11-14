# Ringkasan Eksekutif

**Analisis Penjualan dan Pelanggan — Online Retail II** mencakup transaksi yang tercatat dari 1 Desember 2009 sampai 9 Desember 2011. Setelah penerapan aturan pembersihan, terdapat **1.007.913 baris penjualan positif** dari **1.067.371 baris sumber UCI**.

| Metrik | Hasil |
| --- | ---: |
| Penjualan positif | Rp493.508.591.187,47 |
| Jumlah invoice unik | 40.077 |
| Rata-rata nilai invoice | Rp12.314.010,31 |
| Unit dalam baris positif | 11.205.148 |
| Pelanggan teridentifikasi | 5.878 |
| Pelanggan teridentifikasi yang membeli ulang | 4.255 atau 72,39% |

## Temuan

- **Britania Raya adalah wilayah dengan nilai tertinggi.** Nilainya Rp419.611.841.713,88 atau 85,03% dari total. Irlandia berada di urutan kedua dengan Rp15.877.280.321,97. Perusahaan pada dataset berbasis di Britania Raya. Analisis lanjutan bisa memeriksa komposisi pesanan domestik dan ekspor dengan rentang tanggal yang sama.
- **November adalah puncak pada kedua tahun yang mencakup November.** November 2011 mencapai Rp36.245.445.198,17 dari 2.769 invoice, sekitar 2,70% lebih tinggi dari November 2010. Untuk menilai apakah pola itu berulang, diperlukan data tambahan. Desember 2011 terpotong pada tanggal 9.
- **SKU 84077 memiliki volume unit tertinggi pada grafik produk.** Tercatat 106.139 unit dengan nilai Rp589.175.869,42. Ukuran volume ini dapat digunakan untuk menelusuri kebutuhan persediaan bersama katalog dan data stok. Peringkat tersebut memakai pendekatan pola SKU dan mengecualikan kode ongkir serta entri manual.
- **Data pelanggan punya keterbatasan cakupan.** Sebanyak 228.488 baris penjualan positif tidak memiliki ID pelanggan. Tingkat pembelian ulang sebesar 72,39% berasal dari pelanggan yang teridentifikasi di dataset. Evaluasi retensi dapat memakai kelompok pelanggan baru dengan awal pengamatan sebanding.

Seluruh nominal IDR memakai kurs analitis Bank Indonesia sebesar Rp24.101,50 per GBP tertanggal 13 November 2026. Penjualan positif mencakup nilai kotor baris yang lolos aturan, termasuk beberapa entri non-SKU, dan tidak merekonsiliasi pengembalian, biaya, atau laba. [Kurs Bank Indonesia](https://www.bi.go.id/id/statistik/informasi-kurs/kurs-acuan-non-usd-idr/Default.aspx) · [Dataset UCI](https://doi.org/10.24432/C5CG6D)
