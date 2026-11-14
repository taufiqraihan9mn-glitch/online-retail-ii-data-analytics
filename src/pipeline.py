"""Membaca Online Retail II, mengaudit baris, dan membuat fakta penjualan."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tempfile
import urllib.request
import zipfile
from decimal import Decimal, localcontext
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq

from src.reference import COUNTRIES, OUT, RAW, SOURCE_URL, THOUSANDTH, load_rate, number, write_json

EXPECTED = ['Invoice', 'StockCode', 'Description', 'Quantity', 'InvoiceDate', 'Price', 'Customer ID', 'Country']
COLUMNS = ['Invoice', 'StockCode', 'Description', 'Quantity', 'InvoiceDate', 'CustomerID',
           'Country', 'CountryLabel', 'ProductCode']


def download_source(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=path.parent) as temp:
        target = Path(temp) / path.name
        with urllib.request.urlopen(SOURCE_URL, timeout=120) as response, target.open('wb') as out:
            shutil.copyfileobj(response, out)
        with zipfile.ZipFile(target) as archive:
            if archive.testzip() is not None:
                raise ValueError('Arsip UCI gagal pemeriksaan integritas.')
        target.replace(path)


def load_source(path: Path = RAW) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f'Arsip UCI belum tersedia di {path}. Jalankan ulang dengan --unduh.')
    frames = []
    with zipfile.ZipFile(path) as archive:
        names = [name for name in archive.namelist() if name.lower().endswith('.xlsx')]
        if len(names) != 1:
            raise ValueError('Arsip UCI harus berisi satu buku kerja .xlsx.')
        with archive.open(names[0]) as source, pd.ExcelFile(source, engine='openpyxl') as workbook:
            for sheet in workbook.sheet_names:
                frame = workbook.parse(sheet)
                frame.columns = frame.columns.str.strip()
                missing = set(EXPECTED) - set(frame.columns)
                if missing:
                    raise ValueError(f'Kolom wajib hilang dari lembar {sheet}: {sorted(missing)}')
                frames.append(frame[EXPECTED])
        df = pd.concat(frames, ignore_index=True)
        df.attrs['lembar'] = dict(zip(workbook.sheet_names, map(len, frames), strict=True))
    return df


def clean_source(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Pertahankan konvensi deduplikasi Manus, lalu audit eksklusi secara berurutan."""
    data = raw[EXPECTED].copy()
    invalid_id = pd.to_numeric(data['Customer ID'], errors='coerce')
    data['Customer ID'] = invalid_id.where(invalid_id.mod(1).eq(0))
    data['InvoiceDate'] = pd.to_datetime(data['InvoiceDate'], errors='coerce')
    for field in ['Quantity', 'Price']:
        data[field] = pd.to_numeric(data[field], errors='coerce')
    duplicated = data.duplicated()
    invoice = data.Invoice.astype('string').str.strip()
    stock = data.StockCode.astype('string').str.strip()
    cancelled = invoice.str.upper().str.startswith('C', na=False)
    invalid = (
        invoice.fillna('').eq('') | stock.fillna('').eq('') | data.InvoiceDate.isna()
        | ~data.Quantity.mod(1).eq(0) | ~data.Price.abs().lt(float('inf'))
    )
    nonpositive_quantity = data.Quantity.le(0)
    nonpositive_price = data.Price.le(0)
    rules = {
        'duplikat': duplicated,
        'pembatalan': cancelled,
        'data_wajib_tidak_valid': invalid,
        'kuantitas_nonpositif': nonpositive_quantity,
        'harga_nonpositif': nonpositive_price,
    }
    included = pd.Series(True, index=data.index)
    exclusions = {}
    for rule, mask in rules.items():
        exclusions[rule] = int((included & mask).sum())
        included &= ~mask

    sales = data.loc[included].rename(columns={'Customer ID': 'CustomerID'}).copy()
    sales['Invoice'] = invoice[included]
    sales['StockCode'] = sales.StockCode.astype('string')
    sales['CustomerID'] = sales.CustomerID.astype('Int64')
    sales['Quantity'] = sales.Quantity.astype('int64')
    sales['Country'] = sales.Country.astype('string')
    sales['CountryLabel'] = sales.Country.map(COUNTRIES).fillna(sales.Country).fillna('Negara tidak tersedia')
    code = sales.StockCode.str.strip().str.upper()
    sales['ProductCode'] = code.where(code.str.fullmatch(r'[0-9]{5}[A-Z]{0,3}'))
    scaled = sales.Price * 1000
    if not scaled.sub(scaled.round()).abs().le(1e-6).all():
        raise ValueError('Ditemukan harga dengan lebih dari tiga desimal GBP. Periksa satuan sebelum melanjutkan.')
    sales['UnitPriceMilliGBP'] = scaled.round().astype('int64')
    sales['RevenueMilliGBP'] = sales.Quantity * sales.UnitPriceMilliGBP

    invoices = sales.groupby('Invoice')
    quality = {
        'lembar_sumber': raw.attrs.get('lembar', {}),
        'baris_sumber': len(raw),
        'kolom_sumber': len(EXPECTED),
        'kosong_sumber_per_kolom': {key: int(value) for key, value in raw[EXPECTED].isna().sum().items()},
        'tanggal_tidak_valid_sumber': int(data.InvoiceDate.isna().sum()),
        'temuan_sumber_dapat_tumpang_tindih': {key: int(mask.sum()) for key, mask in rules.items()},
        'eksklusi_bertahap': exclusions,
        'baris_dikecualikan': sum(exclusions.values()),
        'baris_penjualan': len(sales),
        'baris_penjualan_tanpa_id': int(sales.CustomerID.isna().sum()),
        'baris_penjualan_tanpa_deskripsi': int(sales.Description.isna().sum()),
        'baris_penjualan_tanpa_negara': int(sales.Country.isna().sum()),
        'label_negara_unik': int(sales.CountryLabel.nunique()),
        'tanggal_min': sales.InvoiceDate.min().isoformat(),
        'tanggal_maks': sales.InvoiceDate.max().isoformat(),
        'invoice_lintas_tanggal': int(invoices.InvoiceDate.nunique().gt(1).sum()),
        'invoice_lintas_hari': int(sales.assign(day=sales.InvoiceDate.dt.normalize()).groupby('Invoice').day.nunique().gt(1).sum()),
        'invoice_lintas_negara': int(invoices.CountryLabel.nunique().gt(1).sum()),
        'invoice_beberapa_id': int(invoices.CustomerID.nunique().gt(1).sum()),
        'baris_di_luar_pola_sku': int(sales.ProductCode.isna().sum()),
        'kode_di_luar_pola_sku': sorted(sales.loc[sales.ProductCode.isna(), 'StockCode'].unique()),
    }
    return sales, quality


def python_kpis(sales: pd.DataFrame, rate: Decimal) -> dict:
    orders = sales.Invoice.nunique()
    customers = sales.dropna(subset=['CustomerID']).groupby('CustomerID').Invoice.nunique()
    with localcontext() as ctx:
        ctx.prec = 38
        gbp = Decimal(int(sales.RevenueMilliGBP.sum())) * THOUSANDTH
        idr = gbp * rate
        return {
            'total_gbp': str(gbp), 'total_idr': str(idr),
            'aov_gbp': str(gbp / orders) if orders else None,
            'aov_idr': str(idr / orders) if orders else None,
            'transaksi': int(orders), 'pelanggan': int(len(customers)), 'unit': int(sales.Quantity.sum()),
            'baris': len(sales), 'baris_dengan_id': int(sales.CustomerID.notna().sum()),
            'pelanggan_ulang': int(customers.gt(1).sum()),
        }


def save_fact(sales: pd.DataFrame, path: Path, rate: Decimal, metadata: dict) -> None:
    table = pa.Table.from_pandas(sales[COLUMNS], preserve_index=False)
    for name, integer_column in [('UnitPrice', 'UnitPriceMilliGBP'), ('RevenueGBP', 'RevenueMilliGBP')]:
        scale = pa.scalar(THOUSANDTH, type=pa.decimal128(3, 3))
        integer = pa.array(sales[integer_column], type=pa.int64()).cast(pa.decimal128(19, 0))
        gbp = pc.multiply(integer, scale).cast(pa.decimal128(18, 3))
        table = table.append_column(name, gbp)
        idr = pc.multiply(gbp, pa.scalar(rate, type=pa.decimal128(9, 2)))
        idr_name = 'UnitPriceIDR' if name == 'UnitPrice' else 'RevenueIDR'
        table = table.append_column(idr_name, idr.cast(pa.decimal128(27, 5)))
    # Alias kompatibilitas yang tetap bermata uang GBP.
    table = table.append_column('Revenue', table.column('RevenueGBP'))
    attrs = dict(table.schema.metadata or {})
    attrs[b'kurs'] = json.dumps(metadata, ensure_ascii=False).encode('utf-8')
    pq.write_table(table.replace_schema_metadata(attrs), path, compression='zstd')


def run(source=RAW, out=OUT) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    rate, metadata = load_rate()
    sales, quality = clean_source(load_source(source))
    with source.open('rb') as archive:
        quality['sha256_arsip_uci'] = hashlib.file_digest(archive, 'sha256').hexdigest()
    kpis = python_kpis(sales, rate)
    with tempfile.TemporaryDirectory(dir=out) as temp:
        stage = Path(temp)
        save_fact(sales, stage / 'fact_sales.parquet', rate, metadata)
        write_json(stage / 'data_quality_report.json', quality)
        write_json(stage / 'kpis.json', {'kurs': metadata, **kpis})
        for path in stage.iterdir():
            path.replace(out / path.name)
    print(f"Audit menyelesaikan {number(quality['baris_sumber'])} baris sumber dan {number(len(sales))} baris penjualan.")
    return {'quality': quality, 'kpis': kpis}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--unduh', action='store_true', help='Unduh arsip resmi jika belum tersedia.')
    parser.add_argument('--sumber', type=Path, default=RAW, help='Lokasi ZIP unduhan UCI.')
    arguments = parser.parse_args()
    if arguments.unduh and not arguments.sumber.exists():
        download_source(arguments.sumber)
    run(arguments.sumber)
