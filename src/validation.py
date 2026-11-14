"""Rekonsiliasi angka pandas, DuckDB, dan rumus transaksi di seluruh tabel."""
import json
from decimal import Decimal, localcontext

import duckdb

from src.reference import OUT, write_json

SUMMARY_QUERY = """
    SELECT COALESCE(SUM(RevenueGBP), 0) AS total_gbp,
           COALESCE(SUM(RevenueIDR), 0) AS total_idr,
           COUNT(DISTINCT Invoice) AS transaksi, COUNT(DISTINCT CustomerID) AS pelanggan,
           COALESCE(SUM(Quantity), 0) AS unit, COUNT(*) AS baris,
           COUNT(CustomerID) AS baris_dengan_id
    FROM {table}
"""


def fetch_kpis(db, table='fact_sales'):
    result = db.execute(SUMMARY_QUERY.format(table=table))
    metrics = dict(zip([field[0] for field in result.description], result.fetchone(), strict=True))
    orders = metrics['transaksi']
    with localcontext() as ctx:
        ctx.prec = 38
        for currency in ('gbp', 'idr'):
            metrics[f'aov_{currency}'] = metrics[f'total_{currency}'] / orders if orders else None
    return metrics


def validate(out=OUT, *, save=True):
    python = json.loads((out / 'kpis.json').read_text(encoding='utf-8'))
    with duckdb.connect(str(out / 'retail.duckdb'), read_only=True) as db:
        sql = fetch_kpis(db)
        sql['pelanggan_ulang'] = db.execute("""
            SELECT COUNT(*) FROM (
                SELECT CustomerID FROM fact_sales WHERE CustomerID IS NOT NULL
                GROUP BY CustomerID HAVING COUNT(DISTINCT Invoice) > 1
            )
        """).fetchone()[0]
        discrepancies, rate = db.execute("""
            SELECT COUNT(*) FILTER (WHERE
                RevenueGBP <> Quantity * UnitPrice OR Revenue <> RevenueGBP
                OR UnitPriceIDR <> UnitPrice * idr_per_gbp
                OR RevenueIDR <> RevenueGBP * idr_per_gbp
                OR RevenueIDR <> UnitPriceIDR * Quantity
            ), MAX(idr_per_gbp)
            FROM fact_sales CROSS JOIN exchange_rate
        """).fetchone()

    checks = {
        key: {'python': python[key], 'duckdb': str(value) if isinstance(value, Decimal) else value,
              'lulus': Decimal(python[key]) == value if isinstance(value, Decimal) else python[key] == value}
        for key, value in sql.items()
    }
    result = {
        'pemeriksaan_kpi': checks,
        'baris_menyimpang_konversi': discrepancies,
        'kurs_cocok': rate == Decimal(python['kurs']['idr_per_gbp']),
    }
    result['semua_lulus'] = (
        all(check['lulus'] for check in checks.values()) and discrepancies == 0 and result['kurs_cocok']
    )
    if save:
        write_json(out / 'kpi_validation.json', result)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result['semua_lulus']:
        raise AssertionError('Hasil pandas dan DuckDB berbeda atau ada baris yang menyimpang dari rumus kurs.')
    return result


if __name__ == '__main__':
    validate()
