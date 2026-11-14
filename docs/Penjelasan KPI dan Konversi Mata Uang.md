# Penjelasan KPI dan Konversi Mata Uang

| KPI | Definisi dalam filter | Nilai keseluruhan |
| --- | --- | ---: |
| Penjualan positif | Jumlah dari nilai semua baris yang lolos pembersihan. | Rp493.508.591.187,47 |
| Transaksi | `COUNT(DISTINCT Invoice)` pada baris yang lolos filter. | 40.077 |
| Rata-rata nilai transaksi (AOV) | Penjualan positif ÷ jumlah invoice unik. Jika tidak ada invoice, KPI kosong. | Rp12.314.010,31 |
| Pelanggan teridentifikasi | `COUNT(DISTINCT CustomerID)`, dengan NULL dilewati. | 5.878 |
| Tingkat pembelian ulang | Pelanggan teridentifikasi dengan lebih dari satu invoice ÷ semua pelanggan teridentifikasi dalam filter. | 72,39% |
| Cakupan identitas | Baris yang memiliki ID pelanggan ÷ seluruh baris penjualan positif. | 77,33% |

Satu nomor invoice bisa mencakup banyak produk. Rata-rata nilai per baris akan memakai pembagi yang berbeda dari AOV. Metrik penjualan positif tidak mengurangkan retur atau pembatalan dan tidak mengukur laba.

## Kurs dan presisi

Kurs Acuan Non-USD/IDR Bank Indonesia pada **13 November 2026** menunjukkan **Rp24.101,50 untuk 1 GBP**. Satu kurs membuat perbandingan lintas periode memakai skala yang sama. Kurs ini bertanggal di luar periode transaksi 2009–2011, sehingga nilai Rupiah merupakan konversi analitis untuk membaca hasil dan tidak merepresentasikan pendapatan historis aktual dalam IDR. Halaman Bank Indonesia memuat kurs terkini saat dibuka. Gunakan pencarian harian dengan tanggal referensi untuk mengecek angka tersebut. [Bank Indonesia](https://www.bi.go.id/id/statistik/informasi-kurs/kurs-acuan-non-usd-idr/Default.aspx)

1. **GBP per baris** = jumlah unit × harga asli GBP per unit.
2. **Rupiah per baris** = nilai GBP per baris × 24.101,50.
3. **Total** = jumlahkan nilai baris tanpa pembulatan per item.
4. **Tampilan** = bulatkan nilai agregat ke dua desimal, setengah dibulatkan menjauhi nol, format Indonesia.

Contoh transaksi nyata `489434`, SKU `85048`. Sebanyak 12 unit × GBP 6,95 menghasilkan GBP 83,400. Setelah dikali kurs, nilai tampil **Rp2.010.065,10**. Total presisi penuh dari seluruh baris adalah **GBP 20.476.260,448** dan **Rp493.508.591.187,47200**. Tabel menyimpan harga dan nilai GBP dengan tiga desimal dan nilai IDR dengan lima desimal. Tooltip memformat desimal hasil agregasi. Posisi titik dan batang menggunakan angka pecahan biner yang diperlukan Plotly.

Untuk mengubah kurs pada salinan proyek, edit nilai, tanggal, dan sumber di `config/kurs.json`, lalu bangun ulang Parquet dan DuckDB. Ringkasan serta pengujian regresi berbasis angka historis paket memakai kurs referensi aslinya.
