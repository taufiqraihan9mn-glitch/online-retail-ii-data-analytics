"""Dashboard Streamlit untuk fakta penjualan Online Retail II."""
from datetime import timedelta
from pathlib import Path
import sys

import duckdb
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.bootstrap import ensure_database
from dashboard.charts import render_figures
from src.reference import OUT, number, rupiah, tanggal
from src.validation import fetch_kpis

DB_PATH = OUT / 'retail.duckdb'
QUERIES = {
    'monthly': """
        SELECT DATE_TRUNC('month', InvoiceDate) AS bulan, SUM(RevenueIDR) AS nilai,
               COUNT(DISTINCT Invoice) AS transaksi
        FROM pilihan GROUP BY bulan ORDER BY bulan
    """,
    'countries': """
        SELECT CountryLabel AS negara, SUM(RevenueIDR) AS nilai,
               100.0 * SUM(RevenueIDR) / SUM(SUM(RevenueIDR)) OVER () AS kontribusi
        FROM pilihan GROUP BY negara ORDER BY nilai DESC, negara LIMIT 10
    """,
    'products': """
        SELECT ProductCode AS kode, SUM(Quantity) AS unit, SUM(RevenueIDR) AS nilai
        FROM pilihan WHERE ProductCode IS NOT NULL
        GROUP BY kode ORDER BY unit DESC, kode LIMIT 10
    """,
    'weekdays': """
        SELECT ISODOW(InvoiceDate) AS hari, SUM(RevenueIDR) AS nilai FROM pilihan GROUP BY hari
    """,
    'order_bands': """
        WITH invoice AS (SELECT Invoice, SUM(RevenueIDR) AS nilai FROM pilihan GROUP BY Invoice)
        SELECT CASE WHEN nilai < 1000000 THEN 1 WHEN nilai < 5000000 THEN 2
                    WHEN nilai < 20000000 THEN 3 ELSE 4 END AS kelompok, COUNT(*) AS jumlah
        FROM invoice GROUP BY kelompok
    """,
    'customers': """
        SELECT COUNT(DISTINCT Invoice) AS transaksi, SUM(RevenueIDR) AS nilai
        FROM pilihan WHERE CustomerID IS NOT NULL GROUP BY CustomerID ORDER BY CustomerID
    """,
}


@st.cache_data
def context(db_path, modified):
    with duckdb.connect(str(db_path), read_only=True, config={'threads': 4}) as db:
        start, end = db.execute('SELECT MIN(InvoiceDate)::DATE, MAX(InvoiceDate)::DATE FROM fact_sales').fetchone()
        countries = db.execute('SELECT DISTINCT CountryLabel FROM fact_sales ORDER BY 1').fetchall()
        rate = db.execute('SELECT idr_per_gbp, tanggal, sumber, url FROM exchange_rate').fetchone()
    return start, end, [row[0] for row in countries], rate


@st.cache_data(max_entries=12, show_spinner=False)
def aggregate(db_path, modified, start, end, countries):
    query = ('SELECT Invoice, InvoiceDate, Quantity, CustomerID, CountryLabel, ProductCode, RevenueGBP, RevenueIDR '
             'FROM fact_sales WHERE InvoiceDate >= ? AND InvoiceDate < ?')
    params = [start, end + timedelta(days=1)]
    if countries:
        query += ' AND CountryLabel IN (SELECT UNNEST(?))'
        params.append(list(countries))
    with duckdb.connect(str(db_path), read_only=True, config={'threads': 4}) as db:
        db.execute(f'CREATE TEMP TABLE pilihan AS {query}', params)
        kpis = fetch_kpis(db, 'pilihan')
        result = {}
        if kpis['baris']:
            for name, sql in QUERIES.items():
                data = db.execute(sql)
                result[name] = pd.DataFrame(data.fetchall(), columns=[column[0] for column in data.description])
            months = pd.period_range(start, end, freq='M').to_timestamp()
            monthly = result['monthly'].set_index('bulan')
            result['monthly'] = monthly.reindex(months, fill_value=0).rename_axis('bulan').reset_index()
    return kpis, result


def show_chart(heading, note, figure, key):
    st.subheader(heading)
    st.caption(note)
    st.plotly_chart(figure, key=key, width='stretch', theme=None,
                    config={'displayModeBar': False, 'showTips': False})


def main():
    st.set_page_config(page_title='Analisis Penjualan dan Pelanggan | Online Retail II',
                       layout='wide', initial_sidebar_state='auto')
    st.markdown("""
    <style>
    .block-container {max-width: 1536px; padding-top: 2.5rem; padding-bottom: 2.2rem;}
    [data-testid="stMetric"] {background: white; border: 1px solid #D9E6EB; border-radius: 12px; padding: .85rem 1rem; height: 100%;}
    [data-testid="stMetricValue"] {font-size: clamp(1.02rem, 1.51vw, 1.58rem); font-weight: 710;}
    [data-testid="stMetricValue"] > div {overflow: visible; white-space: normal; overflow-wrap: anywhere;}
    [data-testid="stMetricLabel"] {font-weight: 560;}
    [data-testid="stPlotlyChart"] {background: white; border: 1px solid #D9E6EB; border-radius: 10px;}
    [data-testid="stTab"] {font-weight: 640;}
    @media (max-width: 640px) {
      .block-container {padding: 1.4rem .78rem;}
      h1 {font-size: 1.75rem !important;}
      [data-testid="stMetricValue"] {font-size: 1.24rem;}
    }
    </style>
    """, unsafe_allow_html=True)
    st.title('Analisis Penjualan dan Pelanggan')
    st.caption('Online Retail II · UCI Machine Learning Repository · 2009–2011')
    try:
        with st.spinner('Menyiapkan database penjualan. Proses pertama mungkin memerlukan beberapa menit...'):
            ensure_database()
    except Exception as exc:
        st.error('Database belum berhasil disiapkan. Silakan coba kembali beberapa saat lagi.')
        st.exception(exc)
        return

    try:
        modified = DB_PATH.stat().st_mtime_ns
        first, last, countries, kurs = context(DB_PATH, modified)
    except (OSError, duckdb.Error):
        st.error('Basis data tidak dapat dibaca. Tutup proses yang membuka berkas lalu jalankan `python -m src.build_database`.')
        return
    if not first or not kurs:
        st.warning('Basis data belum berisi penjualan atau kurs acuan.')
        return

    with st.sidebar:
        st.header('Filter laporan')
        dates = st.date_input('Periode transaksi', (first, last), min_value=first, max_value=last,
                              format='DD/MM/YYYY', key='periode')
        selected = st.multiselect('Negara atau wilayah', countries, key='negara',
                                  placeholder='Semua negara dan wilayah')
        st.caption('Tanggal awal dan akhir termasuk dalam hasil. Kosongkan negara untuk menampilkan semua wilayah.')
    rate, rate_date, source, url = kurs
    if len(dates) != 2:
        st.info('Pilih tanggal awal dan akhir untuk menampilkan hasil.')
        return
    start, end = dates
    try:
        kpis, data = aggregate(DB_PATH, modified, start, end, tuple(sorted(selected)))
    except (OSError, duckdb.Error):
        st.error('Agregasi gagal. Muat ulang halaman setelah basis data tersedia.')
        return
    st.markdown(f'**{tanggal(start)} – {tanggal(end)}** · '
                f'{number(len(selected)) + " wilayah dipilih" if selected else "Semua negara dan wilayah"}')
    if not kpis['baris']:
        st.warning('Tidak ada penjualan positif pada kombinasi tanggal dan wilayah ini.')
        return
    a, b, c, d = st.columns([1.24, 0.8, 1.12, 1])
    a.metric('Total penjualan positif', rupiah(kpis['total_idr']))
    b.metric('Jumlah transaksi', number(kpis['transaksi']))
    c.metric('Rata-rata nilai transaksi', rupiah(kpis['aov_idr']))
    d.metric('Pelanggan teridentifikasi', number(kpis['pelanggan']))
    st.caption(f"{number(kpis['baris'])} baris · {number(kpis['unit'])} unit · "
               f"{rupiah(rate)} per GBP. Nilai Rupiah adalah konversi analitis.")
    figures = render_figures(data)
    overview, products, customers = st.tabs(['Ringkasan penjualan', 'Produk dan transaksi', 'Pelanggan'])
    with overview:
        left, right = st.columns(2)
        with left:
            show_chart('Penjualan positif per bulan', 'Bulan tanpa penjualan bernilai nol. Ujung rentang dapat mencakup sebagian hari.',
                       figures['tren_penjualan'], 'tren_penjualan')
        with right:
            show_chart('Jumlah transaksi per bulan', 'Satu nomor invoice dihitung sekali pada setiap bulan.',
                       figures['tren_transaksi'], 'tren_transaksi')
        show_chart('Kontribusi 10 negara dan wilayah terbesar', 'Pembagi persentase mencakup semua wilayah dalam filter.',
                   figures['kontribusi'], 'kontribusi')
    with products:
        left, right = st.columns(2)
        with left:
            if data['products'].empty:
                st.info('Tidak ada kode berpola SKU pada hasil filter ini.')
            else:
                show_chart('Produk terlaris menurut unit', 'Peringkat memakai kode berpola SKU. Ongkir dan entri manual dikecualikan.',
                           figures['produk'], 'produk')
        with right:
            show_chart('Penjualan menurut hari', 'Total sepanjang periode terpilih untuk setiap hari dalam sepekan.',
                       figures['hari'], 'hari')
        show_chart('Sebaran nilai transaksi', 'Setiap invoice masuk ke satu kelompok berdasarkan nilai baris dalam filter.',
                   figures['rentang'], 'rentang')
    with customers:
        freq = data['customers']['transaksi']
        if freq.empty:
            st.info('Tidak ada ID pelanggan pada hasil filter ini.')
        else:
            st.caption(f"{number(freq.gt(1).mean() * 100, 2)}% pelanggan teridentifikasi memiliki lebih dari satu "
                       f"transaksi dalam filter. ID tercatat pada {number(kpis['baris_dengan_id'] / kpis['baris'] * 100, 2)}% baris.")
            left, right = st.columns(2)
            with left:
                show_chart('Frekuensi dan nilai pembelian', 'Setiap titik mewakili satu pelanggan teridentifikasi.',
                           figures['frekuensi_nilai'], 'frekuensi_nilai')
            with right:
                show_chart('Pelanggan menurut jumlah transaksi', 'Pelanggan dikelompokkan menurut jumlah invoice unik.',
                           figures['segmen'], 'segmen')
    with st.expander('Kurs, sumber data, dan definisi KPI'):
        st.markdown(f'**Kurs acuan tetap {rupiah(rate)} per GBP** · {tanggal(rate_date)}. '
                    f'[Lihat {source}]({url}).')
        st.write('DuckDB menyimpan nilai asli GBP dan nilai IDR hasil konversi dengan kurs tanggal acuan. '
                 'Penjualan positif hanya mencakup baris yang lolos aturan pembersihan. '
                 'Perhitungan laba atau pendapatan akuntansi memerlukan penyesuaian seperti retur, pembatalan, dan biaya usaha.')
        st.write('Transaksi dihitung dari nomor invoice unik. Rata-rata nilai transaksi membagi total penjualan '
                 'positif dengan invoice unik. Analisis pelanggan memakai ID yang tersedia.')
        st.markdown('[Sumber dataset Online Retail II, Daqing Chen](https://doi.org/10.24432/C5CG6D)')


if __name__ == '__main__':
    main()
