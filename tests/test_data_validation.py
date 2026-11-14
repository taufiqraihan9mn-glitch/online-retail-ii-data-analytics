import json
from decimal import Decimal
from pathlib import Path

import duckdb
import pytest

from src.validation import validate
from src.validate_sql_queries import validate_queries

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/processed'


def test_fakta_positif_dan_konsistensi_grain():
    with duckdb.connect(str(DATA / 'retail.duckdb'), read_only=True) as db:
        assert db.execute("""
            SELECT COUNT(*) FROM fact_sales WHERE Invoice IS NULL OR InvoiceDate IS NULL
                OR Quantity <= 0 OR UnitPrice <= 0 OR UPPER(Invoice) LIKE 'C%'
        """).fetchone() == (0,)
        assert db.execute("""
            SELECT COUNT(*) FROM (
                SELECT Invoice FROM fact_sales GROUP BY Invoice
                HAVING COUNT(DISTINCT InvoiceDate::DATE) > 1 OR COUNT(DISTINCT CountryLabel) > 1
                    OR COUNT(DISTINCT CustomerID) > 1
            )
        """).fetchone() == (0,)


def test_eksklusi_bertahap_tepat():
    audit = json.loads((DATA / 'data_quality_report.json').read_text(encoding='utf-8'))
    assert sum(audit['lembar_sumber'].values()) == 1067371
    assert sum(audit['eksklusi_bertahap'].values()) == 59458
    assert audit['baris_sumber'] == audit['baris_penjualan'] + audit['baris_dikecualikan']
    assert audit['baris_penjualan_tanpa_id'] == 228488


def test_rekonsiliasi_benar_benar_dihitung_ulang():
    result = validate(save=False)
    assert result['semua_lulus']
    assert result['baris_menyimpang_konversi'] == 0
    assert len(result['pemeriksaan_kpi']) == 10
    assert Decimal(result['pemeriksaan_kpi']['total_gbp']['duckdb']) == Decimal('20476260.448')


def test_semua_query_dan_satukan_total_kelompok():
    assert len(validate_queries(save=False)) == 12
    statements = (ROOT / 'sql/business_queries.sql').read_text(encoding='utf-8')
    with duckdb.connect(str(DATA / 'retail.duckdb'), read_only=True) as db:
        queries = db.extract_statements(statements)
        summary = db.execute(queries[0]).fetchone()
        assert summary[:3] == (Decimal('493508591187.47200'), Decimal('20476260.448'), 40077)
        assert summary[3] == pytest.approx(12314010.30984036)
        assert sum(row[1] for row in db.execute(queries[8]).fetchall()) == 40077
        country_shares = db.execute(queries[2]).fetchall()
        assert sum(row[3] for row in country_shares) == pytest.approx(100)
        assert sum(row[1] for row in country_shares) == summary[0]
        joined = db.execute(queries[11]).fetchall()
        assert len(joined) == len(country_shares) == 43
        assert sum(row[1] for row in joined) == summary[0]
