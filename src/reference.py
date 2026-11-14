"""Referensi kurs, nama negara, dan satuan tampilan."""
import json
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data/raw/online_retail_ii.zip'
OUT = ROOT / 'data/processed'
SOURCE_URL = 'https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip'
RATE_PATH = ROOT / 'config/kurs.json'
THOUSANDTH = Decimal('0.001')
CENT = Decimal('0.01')

COUNTRIES = dict([
    ('Australia', 'Australia'), ('Austria', 'Austria'), ('Bahrain', 'Bahrain'),
    ('Belgium', 'Belgia'), ('Bermuda', 'Bermuda'), ('Brazil', 'Brasil'),
    ('Canada', 'Kanada'), ('Channel Islands', 'Kepulauan Channel'),
    ('Cyprus', 'Siprus'), ('Czech Republic', 'Ceko'), ('Denmark', 'Denmark'),
    ('EIRE', 'Irlandia'), ('European Community', 'Komunitas Eropa'),
    ('Finland', 'Finlandia'), ('France', 'Prancis'), ('Germany', 'Jerman'),
    ('Greece', 'Yunani'), ('Hong Kong', 'Hong Kong'), ('Iceland', 'Islandia'),
    ('Israel', 'Israel'), ('Italy', 'Italia'), ('Japan', 'Jepang'), ('Korea', 'Korea'),
    ('Lebanon', 'Lebanon'), ('Lithuania', 'Lituania'), ('Malta', 'Malta'),
    ('Netherlands', 'Belanda'), ('Nigeria', 'Nigeria'), ('Norway', 'Norwegia'),
    ('Poland', 'Polandia'), ('Portugal', 'Portugal'), ('RSA', 'Afrika Selatan'),
    ('Saudi Arabia', 'Arab Saudi'), ('Singapore', 'Singapura'), ('Spain', 'Spanyol'),
    ('Sweden', 'Swedia'), ('Switzerland', 'Swiss'), ('Thailand', 'Thailand'),
    ('USA', 'Amerika Serikat'), ('United Arab Emirates', 'Uni Emirat Arab'),
    ('United Kingdom', 'Britania Raya'), ('Unspecified', 'Tidak disebutkan'),
    ('West Indies', 'Hindia Barat'),
])

DAYS = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']
MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']
MONTH_NAMES = [
    'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus',
    'September', 'Oktober', 'November', 'Desember',
]


def load_rate(path=RATE_PATH):
    metadata = json.loads(path.read_text(encoding='utf-8'))
    rate = Decimal(metadata['idr_per_gbp'])
    if not rate.is_finite() or not 0 < rate < 10**7 or rate != rate.quantize(CENT):
        raise ValueError('Kurs harus positif, di bawah 10 juta, dengan paling banyak dua desimal.')
    date.fromisoformat(metadata['tanggal'])
    return rate.quantize(CENT), metadata


def number(value, decimals=0):
    if value is None:
        return '—'
    rounded = Decimal(str(value)).quantize(Decimal(1).scaleb(-decimals), rounding=ROUND_HALF_UP)
    return f'{rounded:,.{decimals}f}'.translate(str.maketrans(',.', '.,'))


def rupiah(value):
    return f'Rp{number(value, 2)}' if value is not None else '—'


def tanggal(value):
    return f'{value.day} {MONTH_NAMES[value.month - 1]} {value.year}'


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
