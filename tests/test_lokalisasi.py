from decimal import Decimal
from pathlib import Path

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

from src import pipeline

ROOT = Path(__file__).resolve().parents[1]


def test_duckdb_menyimpan_gbp_dan_idr_tanpa_pembulatan_per_baris():
    import duckdb

    query = """
        SELECT RevenueGBP, RevenueIDR FROM fact_sales
        WHERE Invoice = '489434' AND StockCode = '85048'
    """
    with duckdb.connect(str(ROOT / 'data/processed/retail.duckdb'), read_only=True) as db:
        assert db.execute(query).fetchone() == (Decimal('83.400'), Decimal('2010065.10000'))


def test_dashboard_menampilkan_nilai_dan_delapan_grafik():
    app = AppTest.from_file(str(ROOT / 'dashboard/app.py'), default_timeout=60).run()
    assert not app.exception
    assert app.metric[0].value.startswith('Rp')
    assert len(app.get('plotly_chart')) == 8


def test_pembersihan_mempertahankan_pelanggan_tidak_dikenal_dan_audit_eksklusi():
    raw = pd.DataFrame([
        ['1', '12345', 'A', 2, '2011-01-01', 0.001, None, 'France'],
        ['1', '12345', 'A', 2, '2011-01-01', 0.001, None, 'France'],
        ['C1', '12345', 'A', -2, '2011-01-02', 0.001, None, 'France'],
        ['2', '12345', 'A', 1, '2011-01-02', 0, 10001, 'France'],
    ], columns=pipeline.EXPECTED)
    clean = getattr(pipeline, 'clean_source', None)
    assert clean is not None, 'Pipeline belum menyediakan audit pembersihan yang bisa diuji'
    sales, audit = clean(raw)
    assert len(sales) == 1
    assert pd.isna(sales.CustomerID.iloc[0])
    assert audit['eksklusi_bertahap'] == {
        'duplikat': 1, 'pembatalan': 1, 'data_wajib_tidak_valid': 0, 'kuantitas_nonpositif': 0,
        'harga_nonpositif': 1,
    }
