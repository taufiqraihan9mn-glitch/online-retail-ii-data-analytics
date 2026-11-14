# Panduan Instalasi Windows 11

## 1. Siapkan Python

Pasang **Python 3.12 64-bit**. Buka PowerShell, lalu periksa versi.

```powershell
py -3.12 --version
```

Perintah panduan menggunakan executable dalam lingkungan virtual secara langsung sehingga Anda dapat menjalankannya di PowerShell tanpa skrip aktivasi. [Unduh Python untuk Windows](https://www.python.org/downloads/windows/)

## 2. Jalankan paket yang sudah berisi basis data

Ekstrak ZIP. Buka folder sampai Anda melihat `README.md`, `requirements.txt`, dan subfolder `dashboard`. Klik kanan area kosong dan pilih **Buka di Terminal**. Jalankan perintah berikut.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run dashboard/app.py
```

Buka [http://localhost:8501](http://localhost:8501) jika browser belum terbuka. Untuk berhenti, tekan **Ctrl+C** pada terminal Streamlit.

## 3. Bangun ulang dari data resmi

Tutup Streamlit dan alat yang sedang membuka DuckDB sebelum mengganti basis data. Gunakan perintah berikut dari folder yang berisi README.

```powershell
.\.venv\Scripts\python.exe -m src.pipeline --unduh
.\.venv\Scripts\python.exe -m src.build_database
.\.venv\Scripts\python.exe -m src.validation
.\.venv\Scripts\python.exe -m src.validate_sql_queries
.\.venv\Scripts\python.exe -m pytest -q
```

Jika unduhan otomatis diblokir jaringan, buat folder `data\raw` jika belum ada, lalu unduh ZIP resmi secara manual dan simpan sebagai `data\raw\online_retail_ii.zip`. Pertahankan ZIP dan nama berkas tersebut. Pembacaan Excel berisi lebih dari satu juta baris sehingga tahap pertama biasanya memakan waktu paling lama. [Unduh sumber UCI](https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip)

## 4. Atasi kendala umum

| Kendala | Tindakan |
| --- | --- |
| `py` tidak dikenal | Buka PowerShell baru setelah instalasi. Jika `python --version` menunjukkan 3.12, gunakan `python -m venv .venv`. |
| `No module named src` atau `dashboard/app.py` hilang | Gunakan perintah `Get-ChildItem` dan pastikan terminal berada di folder yang berisi `README.md`. |
| Port 8501 sedang digunakan | Tambahkan `--server.port 8502` pada perintah Streamlit, lalu buka [http://localhost:8502](http://localhost:8502). |
| Berkas DuckDB terkunci | Hentikan Streamlit serta tutup koneksi DuckDB dari aplikasi lain, lalu bangun ulang. |
| Dashboard menyatakan basis data belum ada | Periksa `data\processed\retail.duckdb` atau jalankan langkah pembangunan ulang. |

Panduan memakai sintaks PowerShell Windows 11. Pengujian yang dicatat dilakukan pada lingkungan Linux dengan Python 3.12.

## 5. Buka notebook latihan di VS Code

Untuk latihan interaktif, pasang ekstensi **Python** dan **Jupyter** di VS Code. Dari terminal pada folder proyek, pasang kernel Python pada lingkungan virtual.

```powershell
.\.venv\Scripts\python.exe -m pip install ipykernel
```

Buka folder proyek di VS Code, buka `notebooks/exploratory_analysis.ipynb`, lalu pilih `.venv\Scripts\python.exe` melalui **Select Kernel**. Jalankan sel dari atas. Dashboard dapat digunakan tanpa memasang kernel ini.
