from datetime import date
import json
from pathlib import Path

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]


def open_dashboard():
    dashboard = AppTest.from_file(str(ROOT / 'dashboard/app.py'), default_timeout=45).run()
    assert not dashboard.exception
    return dashboard


def test_filter_hari_akhir_termasuk_dan_negara_diterapkan():
    app = open_dashboard()
    assert app.metric[1].value == '40.077'
    first = date(2009, 12, 1)
    app.date_input[0].set_value((first, first)).run()
    app.multiselect[0].set_value(['Britania Raya']).run()
    assert not app.exception
    assert app.metric[1].value == '109'
    assert app.metric[0].value == 'Rp1.148.891.029,29'


def test_filter_kosong_menampilkan_pesan_tanpa_kpi():
    app = open_dashboard()
    first = date(2009, 12, 1)
    app.date_input[0].set_value((first, first)).run()
    app.multiselect[0].set_value(['Arab Saudi']).run()
    assert not app.exception
    assert 'Tidak ada penjualan positif' in app.warning[0].value
    assert len(app.metric) == len(app.get('plotly_chart')) == 0


def test_filter_menunggu_tanggal_akhir():
    app = open_dashboard()
    app.date_input[0].set_value((date(2009, 12, 1),)).run()
    assert not app.exception
    assert app.info[0].value == 'Pilih tanggal awal dan akhir untuk menampilkan hasil.'


def test_contoh_prancis_november_2011_sesuai_dengan_panduan():
    app = open_dashboard()
    app.date_input[0].set_value((date(2011, 11, 1), date(2011, 11, 30))).run()
    app.multiselect[0].set_value(['Prancis']).run()
    assert not app.exception
    assert app.metric[0].value == 'Rp763.930.061,56'
    assert app.metric[1].value == '64'


def test_penjualan_tanpa_id_tetap_ditampilkan():
    app = open_dashboard()
    app.multiselect[0].set_value(['Bermuda']).run()
    assert not app.exception
    assert app.metric[0].value.startswith('Rp')
    assert app.metric[3].value == '0'
    assert any('Tidak ada ID pelanggan' in message.value for message in app.info)
    assert len(app.get('plotly_chart')) == 6


def test_tren_bulanan_menampilkan_bulan_kosong_dalam_filter():
    app = open_dashboard()
    app.date_input[0].set_value((date(2010, 2, 1), date(2010, 4, 30))).run()
    app.multiselect[0].set_value(['Bermuda']).run()
    assert not app.exception
    charts = app.get('plotly_chart')
    sales, orders = (json.loads(chart.proto.spec)['data'][0] for chart in charts[:2])
    assert [month[:7] for month in sales['x']] == ['2010-02', '2010-03', '2010-04']
    assert sales['y'] == [0, 30202553.71, 0]
    assert orders['y'] == [0, 1, 0]
