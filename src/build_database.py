"""Bangun basis data DuckDB dari fakta Parquet dan metadata kursnya."""
import json
import tempfile
from decimal import Decimal
from pathlib import Path

import duckdb
import pyarrow.parquet as pq

from src.reference import OUT, ROOT


def build(out=OUT):
    fact = out / 'fact_sales.parquet'
    db_path = out / 'retail.duckdb'
    if not fact.exists():
        raise FileNotFoundError('Buat Parquet terlebih dahulu dengan python -m src.pipeline.')
    kurs = json.loads(pq.read_schema(fact).metadata[b'kurs'])
    with tempfile.TemporaryDirectory(dir=out) as folder:
        staged_db = Path(folder) / db_path.name
        with duckdb.connect(str(staged_db), config={'threads': 4}) as db:
            db.execute((ROOT / 'sql/schema.sql').read_text(encoding='utf-8'))
            db.execute('INSERT INTO fact_sales BY NAME SELECT * FROM read_parquet(?)', [str(fact)])
            db.execute('INSERT INTO exchange_rate VALUES (?, ?, ?, ?)', [
                Decimal(kurs['idr_per_gbp']), kurs['tanggal'], kurs['sumber'], kurs['url'],
            ])
            db.execute('CHECKPOINT')
        staged_db.replace(db_path)
    print(f'Basis data siap: {db_path}')
    return db_path


if __name__ == '__main__':
    build()
