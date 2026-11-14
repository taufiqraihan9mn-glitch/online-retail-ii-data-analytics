"""Jalankan seluruh contoh SQL dan simpan jumlah baris hasil setiap kueri."""
import re

import duckdb

from src.reference import OUT, ROOT, write_json


def validate_queries(out=OUT, *, save=True):
    source = (ROOT / 'sql/business_queries.sql').read_text(encoding='utf-8')
    names = re.findall(r'^-- (Q\d+ .+)$', source, re.MULTILINE)
    with duckdb.connect(str(out / 'retail.duckdb'), read_only=True) as db:
        statements = db.extract_statements(source)
        results = []
        for name, statement in zip(names, statements, strict=True):
            rows = db.execute(statement).fetchall()
            if not rows:
                raise AssertionError(f'Hasil kosong pada data lengkap: {name}')
            results.append({'kueri': name, 'baris_hasil': len(rows)})
            if save:
                print(f'LULUS · {name} ({len(rows)} baris)')
    if save:
        write_json(out / 'validasi_sql.json', results)
    return results


if __name__ == '__main__':
    validate_queries()
