"""Pengujian bootstrap tanpa mengubah database asli."""
from pathlib import Path

import pytest

from src import bootstrap


def test_database_valid_tidak_dibangun_ulang(monkeypatch, tmp_path):
    db_path = tmp_path / "retail.duckdb"
    db_path.touch()

    monkeypatch.setattr(bootstrap, "OUT", tmp_path)
    monkeypatch.setattr(
        bootstrap, "database_ready",
        lambda path: path == db_path
    )

    def forbidden(*args, **kwargs):
        raise AssertionError("Pipeline tidak boleh dijalankan")

    monkeypatch.setattr(bootstrap, "download_source", forbidden)
    monkeypatch.setattr(bootstrap, "run", forbidden)
    monkeypatch.setattr(bootstrap, "build", forbidden)

    assert bootstrap.ensure_database() == db_path
    assert bootstrap.ensure_database() == db_path


def test_database_kosong_memicu_pipeline(monkeypatch, tmp_path):
    out = tmp_path / "processed"
    raw = tmp_path / "raw" / "source.zip"
    db_path = out / "retail.duckdb"
    fact_path = out / "fact_sales.parquet"
    calls = []

    monkeypatch.setattr(bootstrap, "OUT", out)
    monkeypatch.setattr(bootstrap, "RAW", raw)
    monkeypatch.setattr(
        bootstrap, "database_ready",
        lambda path: path.is_file()
    )

    def fake_download(path):
        calls.append("download")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()

    def fake_run():
        calls.append("pipeline")
        fact_path.touch()

    def fake_build():
        calls.append("build")
        db_path.touch()

    monkeypatch.setattr(bootstrap, "download_source", fake_download)
    monkeypatch.setattr(bootstrap, "run", fake_run)
    monkeypatch.setattr(bootstrap, "build", fake_build)

    assert bootstrap.ensure_database() == db_path
    assert calls == ["download", "pipeline", "build"]

    assert bootstrap.ensure_database() == db_path
    assert calls == ["download", "pipeline", "build"]


def test_kegagalan_unduhan_tidak_membuat_database(monkeypatch, tmp_path):
    out = tmp_path / "processed"
    raw = tmp_path / "raw" / "source.zip"

    monkeypatch.setattr(bootstrap, "OUT", out)
    monkeypatch.setattr(bootstrap, "RAW", raw)
    monkeypatch.setattr(
        bootstrap, "database_ready",
        lambda path: path.is_file()
    )

    def failed_download(path):
        raise ConnectionError("Simulasi jaringan terputus")

    monkeypatch.setattr(bootstrap, "download_source", failed_download)

    with pytest.raises(ConnectionError):
        bootstrap.ensure_database()

    assert not (out / "retail.duckdb").exists()
