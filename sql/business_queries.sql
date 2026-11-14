-- Sumber query ialah fakta penjualan positif. Nilai IDR memakai satu kurs acuan.
-- Q01 Ringkasan KPI dan rata-rata nilai invoice
SELECT SUM(RevenueIDR) AS penjualan_idr, SUM(RevenueGBP) AS penjualan_gbp,
       COUNT(DISTINCT Invoice) AS transaksi,
       SUM(RevenueIDR) / NULLIF(COUNT(DISTINCT Invoice), 0) AS rata_rata_idr,
       SUM(Quantity) AS unit, COUNT(DISTINCT CustomerID) AS pelanggan_teridentifikasi
FROM fact_sales;

-- Q02 Tren bulanan dan perubahan terhadap bulan sebelumnya
WITH bulanan AS (
    SELECT DATE_TRUNC('month', InvoiceDate) AS bulan, SUM(RevenueIDR) AS penjualan_idr
    FROM fact_sales GROUP BY bulan
), tren AS (
    SELECT *, LAG(penjualan_idr) OVER (ORDER BY bulan) AS idr_bulan_sebelumnya
    FROM bulanan
)
SELECT *, 100.0 * (penjualan_idr / NULLIF(idr_bulan_sebelumnya, 0) - 1) AS perubahan_persen
FROM tren ORDER BY bulan;

-- Q03 Kontribusi negara terhadap penjualan positif
SELECT CountryLabel AS negara, SUM(RevenueIDR) AS penjualan_idr,
       COUNT(DISTINCT Invoice) AS transaksi,
       100.0 * SUM(RevenueIDR) / NULLIF(SUM(SUM(RevenueIDR)) OVER (), 0) AS kontribusi_persen
FROM fact_sales GROUP BY negara ORDER BY penjualan_idr DESC, negara;

-- Q04 Produk terlaris berdasarkan unit dan kode barang terstandardisasi
SELECT ProductCode AS kode, SUM(RevenueIDR) AS penjualan_idr, SUM(Quantity) AS unit,
       COUNT(DISTINCT Invoice) AS transaksi
FROM fact_sales WHERE ProductCode IS NOT NULL GROUP BY kode
ORDER BY unit DESC, kode LIMIT 20;

-- Q05 Nilai dan frekuensi pembelian pelanggan teridentifikasi
SELECT CustomerID, COUNT(DISTINCT Invoice) AS transaksi,
       SUM(RevenueIDR) AS penjualan_idr, AVG(RevenueIDR) AS rata_rata_nilai_baris_idr
FROM fact_sales WHERE CustomerID IS NOT NULL
GROUP BY CustomerID ORDER BY penjualan_idr DESC, CustomerID LIMIT 25;

-- Q06 Segmen pembelian ulang
WITH pelanggan AS (
    SELECT CustomerID, COUNT(DISTINCT Invoice) AS transaksi, SUM(RevenueIDR) AS penjualan_idr
    FROM fact_sales WHERE CustomerID IS NOT NULL GROUP BY CustomerID
)
SELECT CASE WHEN transaksi = 1 THEN '1 transaksi' WHEN transaksi BETWEEN 2 AND 5 THEN '2–5 transaksi'
            ELSE '6 transaksi atau lebih' END AS segmen,
       COUNT(*) AS pelanggan, SUM(penjualan_idr) AS penjualan_idr,
       AVG(penjualan_idr) AS rata_rata_per_pelanggan_idr
FROM pelanggan GROUP BY segmen ORDER BY MIN(transaksi);

-- Q07 Penjualan per hari dalam sepekan
SELECT ISODOW(InvoiceDate) AS urutan,
       ['Senin','Selasa','Rabu','Kamis','Jumat','Sabtu','Minggu'][ISODOW(InvoiceDate)] AS hari,
       SUM(RevenueIDR) AS penjualan_idr, COUNT(DISTINCT Invoice) AS transaksi
FROM fact_sales GROUP BY urutan, hari ORDER BY urutan;

-- Q08 Tiga bulan terbesar per negara
WITH bulanan AS (
    SELECT CountryLabel AS negara, DATE_TRUNC('month',InvoiceDate) AS bulan,
           SUM(RevenueIDR) AS penjualan_idr
    FROM fact_sales GROUP BY negara, bulan
), peringkat AS (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY negara ORDER BY penjualan_idr DESC, bulan) AS urutan
    FROM bulanan
)
SELECT negara, bulan, penjualan_idr FROM peringkat WHERE urutan <= 3 ORDER BY negara, urutan;

-- Q09 Distribusi nilai per invoice dengan ambang dalam Rupiah
WITH invoice AS (
    SELECT Invoice, SUM(RevenueIDR) AS nilai_idr FROM fact_sales GROUP BY Invoice
), kelompok AS (
    SELECT *, CASE WHEN nilai_idr < 1000000 THEN 1 WHEN nilai_idr < 5000000 THEN 2
                   WHEN nilai_idr < 20000000 THEN 3 ELSE 4 END AS urutan
    FROM invoice
)
SELECT ['< Rp1 juta','Rp1–<5 juta','Rp5–<20 juta','≥ Rp20 juta'][urutan] AS rentang,
       COUNT(*) AS transaksi, SUM(nilai_idr) AS penjualan_idr
FROM kelompok GROUP BY urutan ORDER BY urutan;

-- Q10 Aktivitas penjualan tahunan menurut negara
SELECT YEAR(InvoiceDate) AS tahun, CountryLabel AS negara,
       COUNT(DISTINCT Invoice) AS transaksi, SUM(Quantity) AS unit,
       SUM(RevenueIDR) AS penjualan_idr
FROM fact_sales GROUP BY tahun, negara ORDER BY tahun, penjualan_idr DESC, negara;

-- Q11 Variasi deskripsi sumber per kode SKU
SELECT ProductCode AS kode, COUNT(DISTINCT Description) AS variasi_deskripsi,
       SUM(Quantity) AS unit, SUM(RevenueIDR) AS penjualan_idr
FROM fact_sales WHERE ProductCode IS NOT NULL GROUP BY kode
ORDER BY penjualan_idr DESC, kode LIMIT 20;

-- Q12 Hubungkan ringkasan penjualan dan pelanggan per negara
WITH penjualan AS (
    SELECT CountryLabel AS negara, SUM(RevenueIDR) AS penjualan_idr,
           COUNT(DISTINCT Invoice) AS transaksi
    FROM fact_sales GROUP BY negara
), pelanggan AS (
    SELECT CountryLabel AS negara, COUNT(DISTINCT CustomerID) AS pelanggan_teridentifikasi
    FROM fact_sales WHERE CustomerID IS NOT NULL GROUP BY negara
)
SELECT p.*, COALESCE(c.pelanggan_teridentifikasi, 0) AS pelanggan_teridentifikasi
FROM penjualan p LEFT JOIN pelanggan c USING (negara)
ORDER BY p.penjualan_idr DESC, negara;
