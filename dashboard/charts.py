"""Delapan figur Plotly dengan label dan tooltip berformat Indonesia."""
from math import ceil, floor, log10

import plotly.graph_objects as go

from src.reference import DAYS, MONTHS, number, rupiah

INK = '#142839'
TEAL = '#00796D'
BLUE = '#4567B6'
GRID = '#E1E9EE'
BANDS = ['< Rp1 juta', 'Rp1–<5 juta', 'Rp5–<20 juta', '≥ Rp20 juta']
SEGMENTS = ['1 transaksi', '2–5 transaksi', '6 transaksi atau lebih']


def compact(value, currency=False):
    for unit, label in ((10**12, 'T'), (10**9, 'M'), (10**6, 'jt'), (10**3, 'rb')):
        if abs(value) >= unit:
            prefix = 'Rp' if currency else ''
            quotient = value / unit
            return f'{prefix}{number(quotient, 0 if quotient == int(quotient) else 1)} {label}'
    return f'{"Rp" if currency else ""}{number(value)}'


def money_axis(values, logarithmic=False, horizontal=False):
    values = [float(value) for value in values if value is not None]
    if logarithmic:
        ticks = [10.0**i for i in range(floor(log10(min(values))), ceil(log10(max(values))) + 1)]
        return {'type': 'log', 'tickvals': ticks, 'ticktext': [compact(x, True) for x in ticks]}
    maximum = max(values, default=0)
    if maximum <= 0:
        return {'rangemode': 'tozero'}
    raw_step = maximum / 4
    scale = 10.0**floor(log10(raw_step))
    step = min(x * scale for x in (1, 2, 2.5, 5, 10) if x * scale >= raw_step)
    if step >= 100:
        ticks = [step * index for index in range(ceil(maximum * 1.05 / step) + 1)]
        return {'tickvals': ticks, 'ticktext': [compact(x, True) for x in ticks],
                'range': [0, maximum * (1.09 if horizontal else 1.15)]}
    return {'tickprefix': 'Rp', 'tickformat': ',.2f', 'rangemode': 'tozero'}


def style(figure, x_title, y_title, height=320):
    figure.update_layout(
        height=height, margin=dict(l=18, r=18, t=18, b=48),
        paper_bgcolor='white', plot_bgcolor='white', separators=',.',
        showlegend=False, font=dict(family='Inter, system-ui, sans-serif', color=INK, size=13),
        hoverlabel=dict(bgcolor=INK, font_color='white', align='left'),
        xaxis_title=x_title, yaxis_title=y_title,
    )
    figure.update_xaxes(automargin=True, gridcolor=GRID, zeroline=False)
    figure.update_yaxes(automargin=True, gridcolor=GRID, zeroline=False)
    return figure


def render_figures(data):
    month = data['monthly']
    periods = month['bulan'].tolist()
    monthly_idr = month['nilai'].tolist()
    monthly_orders = month['transaksi'].tolist()
    tick_spacing = max(1, ceil(len(periods) / 8))
    ticks = periods[::tick_spacing]
    month_ticks = {
        'tickvals': ticks, 'ticktext': [f'{MONTHS[x.month-1]} {str(x.year)[-2:]}' for x in ticks],
        'showgrid': False,
    }
    monthly_sales_fig = style(go.Figure(go.Scatter(
        x=periods, y=[float(value) for value in monthly_idr], mode='lines+markers',
        line=dict(color=TEAL, width=3), marker=dict(size=6),
        customdata=[[f'{MONTHS[x.month-1]} {x.year}', rupiah(y)] for x, y in zip(periods, monthly_idr)],
        hovertemplate='<b>%{customdata[0]}</b><br>Penjualan positif: %{customdata[1]}<extra></extra>',
    )), 'Bulan', 'Penjualan positif')
    monthly_sales_fig.update_xaxes(**month_ticks)
    monthly_sales_fig.update_yaxes(**money_axis(monthly_idr))
    monthly_orders_fig = style(go.Figure(go.Scatter(
        x=periods, y=monthly_orders, mode='lines+markers',
        line=dict(color=BLUE, width=3), marker=dict(size=6),
        customdata=[[f'{MONTHS[x.month-1]} {x.year}', number(y)] for x, y in zip(periods, monthly_orders)],
        hovertemplate='<b>%{customdata[0]}</b><br>Transaksi: %{customdata[1]}<extra></extra>',
    )), 'Bulan', 'Jumlah transaksi')
    monthly_orders_fig.update_xaxes(**month_ticks)
    monthly_orders_fig.update_yaxes(tickformat=',d', rangemode='tozero')

    countries = data['countries'].iloc[::-1]
    country_fig = style(go.Figure(go.Bar(
        x=countries['kontribusi'].tolist(), y=countries['negara'].tolist(), orientation='h',
        marker_color=[TEAL if idx == len(countries) - 1 else '#6AAFA6' for idx in range(len(countries))],
        customdata=[[f'{number(share, 2)}%', rupiah(value)]
                    for share, value in zip(countries.kontribusi, countries.nilai)],
        hovertemplate='<b>%{y}</b><br>Kontribusi: %{customdata[0]}<br>Penjualan positif: %{customdata[1]}<extra></extra>',
    )), 'Persentase penjualan terfilter', '', 365)
    country_fig.update_xaxes(ticksuffix='%', rangemode='tozero')

    products = data['products'].iloc[::-1]
    product_fig = style(go.Figure(go.Bar(
        x=products['unit'].tolist(), y=products['kode'].tolist(), orientation='h',
        marker_color=BLUE, customdata=[[number(unit), rupiah(value)]
                                       for unit, value in zip(products.unit, products.nilai)],
        hovertemplate='<b>Kode SKU %{y}</b><br>Unit: %{customdata[0]}<br>Penjualan positif: %{customdata[1]}<extra></extra>',
    )), 'Unit terjual', 'Kode SKU', 365)
    product_fig.update_xaxes(tickformat=',d', rangemode='tozero')
    product_fig.update_yaxes(type='category')

    weekday_values = data['weekdays'].set_index('hari')['nilai'].reindex(range(1, 8), fill_value=0).tolist()
    weekday_fig = style(go.Figure(go.Bar(
        x=DAYS, y=[float(value) for value in weekday_values], marker_color=TEAL,
        customdata=[rupiah(x) for x in weekday_values],
        hovertemplate='<b>%{x}</b><br>Penjualan positif: %{customdata}<extra></extra>',
    )), 'Hari transaksi', 'Penjualan positif')
    weekday_fig.update_yaxes(**money_axis(weekday_values))

    band_counts = data['order_bands'].set_index('kelompok')['jumlah'].reindex(range(1, 5), fill_value=0)
    band_fig = style(go.Figure(go.Bar(
        x=BANDS, y=band_counts.tolist(), marker_color=BLUE,
        customdata=[number(x) for x in band_counts],
        hovertemplate='<b>%{x}</b><br>Transaksi: %{customdata}<extra></extra>',
    )), 'Rentang nilai transaksi', 'Jumlah transaksi')
    band_fig.update_yaxes(tickformat=',d')

    customers = data['customers']
    c_orders = customers.transaksi.tolist()
    c_value = customers.nilai.tolist()
    customer_fig = style(go.Figure(go.Scatter(
        x=c_orders, y=[float(value) for value in c_value], mode='markers',
        marker=dict(color=TEAL, size=6, opacity=0.43),
        customdata=[[number(amount), rupiah(value)] for amount, value in zip(c_orders, c_value)],
        hovertemplate='Transaksi: %{customdata[0]}<br>Penjualan positif: %{customdata[1]}<extra></extra>',
    )), 'Transaksi per pelanggan (log)', 'Penjualan per pelanggan (log)')
    customer_fig.update_xaxes(type='log', tickvals=[1, 3, 10, 30, 100, 300],
                              ticktext=['1', '3', '10', '30', '100', '300'])
    if c_value:
        customer_fig.update_yaxes(**money_axis(c_value, logarithmic=True))
    segments = [sum(x == 1 for x in c_orders), sum(2 <= x <= 5 for x in c_orders), sum(x >= 6 for x in c_orders)]
    customer_segments_fig = style(go.Figure(go.Bar(
        x=SEGMENTS, y=segments, marker_color=BLUE,
        customdata=[number(x) for x in segments],
        hovertemplate='<b>%{x}</b><br>Pelanggan: %{customdata}<extra></extra>',
    )), 'Frekuensi pembelian pada periode terpilih', 'Pelanggan teridentifikasi')
    customer_segments_fig.update_yaxes(tickformat=',d')

    return {
        'tren_penjualan': monthly_sales_fig, 'tren_transaksi': monthly_orders_fig, 'kontribusi': country_fig,
        'produk': product_fig, 'hari': weekday_fig, 'rentang': band_fig,
        'frekuensi_nilai': customer_fig, 'segmen': customer_segments_fig,
    }
