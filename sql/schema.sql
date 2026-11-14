-- Satu baris per baris penjualan positif yang dipertahankan.
CREATE TABLE fact_sales (
    Invoice VARCHAR NOT NULL,
    StockCode VARCHAR NOT NULL,
    Description VARCHAR,
    Quantity BIGINT NOT NULL CHECK (Quantity > 0),
    InvoiceDate TIMESTAMP NOT NULL,
    CustomerID BIGINT,
    Country VARCHAR,
    CountryLabel VARCHAR NOT NULL,
    ProductCode VARCHAR,
    UnitPrice DECIMAL(18,3) NOT NULL CHECK (UnitPrice > 0),
    UnitPriceIDR DECIMAL(27,5) NOT NULL,
    RevenueGBP DECIMAL(18,3) NOT NULL,
    RevenueIDR DECIMAL(27,5) NOT NULL,
    Revenue DECIMAL(18,3) NOT NULL
);
CREATE TABLE exchange_rate (
    idr_per_gbp DECIMAL(9,2) NOT NULL,
    tanggal DATE NOT NULL,
    sumber VARCHAR NOT NULL,
    url VARCHAR NOT NULL
);
