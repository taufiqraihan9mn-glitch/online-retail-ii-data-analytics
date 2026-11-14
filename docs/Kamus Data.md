# Kamus Data

## Tabel `fact_sales`

Satu baris mengikuti satu baris sumber yang dipertahankan. `Invoice` dapat berulang karena satu pesanan memuat beberapa baris. Nama kolom teknis utama dipertahankan dari proyek awal untuk memudahkan penelusuran.

| Kolom | Tipe DuckDB | Asal dan arti |
| --- | --- | --- |
| `Invoice` | VARCHAR | Nomor invoice sumber, setelah penanganan spasi. Awalan C dikeluarkan dari fakta positif. |
| `StockCode` | VARCHAR | Kode barang atau entri operasional sebagaimana di sumber. |
| `Description` | VARCHAR, dapat NULL | Deskripsi katalog historis atau catatan entri dalam bahasa asli sumber. |
| `Quantity` | BIGINT | Kuantitas pada baris penjualan, bernilai positif. |
| `InvoiceDate` | TIMESTAMP | Tanggal dan waktu dari lembar Excel, tanpa interpretasi zona waktu baru. |
| `CustomerID` | BIGINT, dapat NULL | ID pelanggan sumber. NULL berarti identitas tidak tercatat di baris tersebut. |
| `Country` | VARCHAR, dapat NULL | Negara atau wilayah asli dari sumber. |
| `CountryLabel` | VARCHAR | Padanan nama negara atau wilayah untuk laporan. Label sumber dicadangkan jika belum ada padanan. |
| `ProductCode` | VARCHAR, dapat NULL | Kode SKU perkiraan berdasarkan pola lima digit diikuti hingga tiga huruf. Spasi dibuang di tepi dan huruf dikapitalisasi. NULL berarti baris berada di luar cakupan grafik produk. |
| `UnitPrice` | DECIMAL(18,3) | Harga asli GBP per unit. Berasal dari `Price` di Excel. |
| `UnitPriceIDR` | DECIMAL(27,5) | Harga per unit hasil kali `UnitPrice` dengan kurs acuan. |
| `RevenueGBP` | DECIMAL(18,3) | Nilai baris penjualan positif dalam GBP, yaitu kuantitas × harga satuan. |
| `RevenueIDR` | DECIMAL(27,5) | Nilai baris hasil kali `RevenueGBP` dengan kurs acuan. |
| `Revenue` | DECIMAL(18,3) | Alias GBP untuk kompatibilitas kueri lama. |

## Tabel `exchange_rate`

| Kolom | Tipe DuckDB | Arti |
| --- | --- | --- |
| `idr_per_gbp` | DECIMAL(9,2) | Rupiah per GBP, satu nilai untuk semua transaksi. |
| `tanggal` | DATE | Tanggal referensi publikasi kurs. |
| `sumber` | VARCHAR | Nama lembaga dan seri kurs. |
| `url` | VARCHAR | Halaman resmi sumber kurs. |

`data_quality_report.json` memuat jumlah baris, nilai kosong, dan temuan kualitas. `kpis.json` memuat hasil pandas pada seluruh periode, `kpi_validation.json` memuat perbandingan terhadap DuckDB, dan `validasi_sql.json` mencatat hasil eksekusi kueri. Nilai desimal dalam JSON disimpan sebagai teks untuk mempertahankan presisi.
