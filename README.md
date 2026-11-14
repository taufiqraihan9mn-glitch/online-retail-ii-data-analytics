## Menjalankan dashboard dari GitHub

Proyek menggunakan Python 3.12 dan dataset Online Retail II dari UCI Machine Learning Repository.

File database DuckDB dan Parquet tidak disimpan di GitHub. Pengguna harus membangun ulang data dari sumber resmi sebelum menjalankan dashboard.

### Instalasi Windows

Buka PowerShell di folder proyek, lalu jalankan:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Pastikan perintah `python --version` menunjukkan Python 3.12.

### Unduh dan proses dataset

```powershell
.\.venv\Scripts\python.exe -m src.pipeline --unduh
```

### Bangun database DuckDB

```powershell
.\.venv\Scripts\python.exe -m src.build_database
```

### Jalankan validasi

```powershell
.\.venv\Scripts\python.exe -m src.validation
.\.venv\Scripts\python.exe -m src.validate_sql_queries
.\.venv\Scripts\python.exe -m pytest tests -q
```

Pada pengujian lokal tanggal 14 November 2026, seluruh 12 kueri SQL dan 13 pengujian otomatis berhasil.

### Jalankan dashboard

```powershell
.\.venv\Scripts\python.exe -m streamlit run dashboard/app.py
```

Buka http://localhost:8501 melalui browser.

### Catatan

- Pengunduhan dataset membutuhkan koneksi internet.
- Proses awal dapat membutuhkan beberapa menit.
- File database dan Parquet dibuat secara lokal.
- Nilai Rupiah merupakan konversi analitis menggunakan kurs tetap yang terdokumentasi, bukan pendapatan historis aktual dalam Rupiah.
- Jika instalasi Windows gagal karena panjang path, pindahkan proyek ke direktori yang lebih pendek atau gunakan virtual environment pada lokasi pendek seperti `F:\venvs\retail2`.
