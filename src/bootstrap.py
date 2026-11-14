"""Persiapan database untuk deployment Streamlit."""
from pathlib import Path
from threading import Lock

import duckdb

from src.reference import RAW, OUT
from src.pipeline import download_source, run
from src.build_database import build

_BOOTSTRAP_LOCK = Lock()


def database_ready(path: Path) -> bool:
    if not path.is_file():
        return False
    try:
        with duckdb.connect(str(path), read_only=True) as db:
            sales = db.execute(
                "SELECT COUNT(*) FROM fact_sales"
            ).fetchone()
            rate = db.execute(
                "SELECT COUNT(*) FROM exchange_rate"
            ).fetchone()
        return sales[0] > 0 and rate[0] == 1
    except (OSError, duckdb.Error):
        return False


def ensure_database() -> Path:
    db_path = OUT / "retail.duckdb"

    if database_ready(db_path):
        return db_path

    with _BOOTSTRAP_LOCK:
        if database_ready(db_path):
            return db_path

        OUT.mkdir(parents=True, exist_ok=True)
        fact_path = OUT / "fact_sales.parquet"

        if not fact_path.exists():
            if not RAW.exists():
                download_source(RAW)
            run()

        build()

        if not database_ready(db_path):
            raise RuntimeError(
                "Database gagal melewati pemeriksaan."
            )

        return db_path
