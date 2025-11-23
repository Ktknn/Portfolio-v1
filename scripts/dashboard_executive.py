"""
Bảng điều hành - Phân tích thị trường & ngành
Hệ thống hiển thị hiện đại với giao diện trực quan, chia rõ từng mô-đun.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings

from scripts.data_loader import (
    get_market_indices_metrics,
    get_indices_history,
    get_index_history,
    get_sector_snapshot,
    summarize_sector_performance,
    summarize_market_cap_distribution,
    get_foreign_flow_leaderboard,
    get_liquidity_leaders,
    get_sector_heatmap_matrix,
    get_return_correlation_matrix,
    get_realtime_index_board,
)
from scripts.config import ANALYSIS_START_DATE, ANALYSIS_END_DATE

warnings.filterwarnings('ignore')

PAPER_BG = '#ffffff'
PLOT_BG = '#ffffff'
FONT_COLOR = '#2d3748'
GRID_COLOR = '#e2e8f0'
ZERO_LINE_COLOR = '#cbd5f5'
POSITIVE_COLOR = '#2f855a'
NEGATIVE_COLOR = '#c53030'
REFERENCE_COLOR = '#d69e2e'
TITLE_FONT = dict(size=14, color=FONT_COLOR, family='Arial, sans-serif')
TITLE_PAD = dict(b=12)
REALTIME_INDEX_SYMBOLS = ["VNINDEX", "VN30", "HNXIndex", "HNX30", "UpcomIndex"]
REALTIME_LABELS = {
    "VNINDEX": "VN-Index",
    "VN30": "VN30",
    "HNXINDEX": "HNX-Index",
    "HNX30": "HNX30",
    "UPCOMINDEX": "UPCoM",
    "UPCOM": "UPCoM",
}
REALTIME_SYMBOL_KEYS = sorted({symbol.upper() for symbol in REALTIME_INDEX_SYMBOLS} | {symbol.upper() for symbol in REALTIME_LABELS.keys()})

SNAPSHOT_COLUMNS = [
    'ticker',
    'industry',
    'market_cap',
    'price_growth_1w',
    'price_growth_1m',
    'avg_trading_value_20d',
    'foreign_buysell_20s',
]


@st.cache_data(ttl=1800, show_spinner=False)
def load_overview_data():
    """Fetch lightweight data powering the headline KPI cards and charts."""

    analysis_start = pd.to_datetime(ANALYSIS_START_DATE).strftime("%Y-%m-%d")
    analysis_end = pd.to_datetime(ANALYSIS_END_DATE).strftime("%Y-%m-%d")
    months_span = max(1, int((pd.to_datetime(analysis_end) - pd.to_datetime(analysis_start)).days / 30))

    return {
        'indices_metrics': get_market_indices_metrics(),
        'index_history': get_indices_history(start_date=analysis_start, end_date=analysis_end, months=months_span),
        'vnindex_history': get_index_history('VNINDEX', start_date=analysis_start, end_date=analysis_end, months=months_span),
    }


@st.cache_data(ttl=1800, show_spinner=False)
def load_sector_snapshot_cached():
    """Cache-reuse the sector snapshot with only essential columns."""

    return get_sector_snapshot(columns=SNAPSHOT_COLUMNS)


@st.cache_data(ttl=1800, show_spinner=False)
def load_detail_data():
    """Load heavier, sector-dependent datasets for secondary visuals."""

    sector_snapshot = load_sector_snapshot_cached()
    return {
        'sector_snapshot': sector_snapshot,
        'sector_perf': summarize_sector_performance(sector_snapshot, top_n=8),
        'market_cap': summarize_market_cap_distribution(sector_snapshot, top_n=8),
        'foreign_flow': get_foreign_flow_leaderboard(sector_snapshot, top_n=6),
        'liquidity': get_liquidity_leaders(sector_snapshot, top_n=40),
        'sector_heatmap': get_sector_heatmap_matrix(sector_snapshot, top_n=6),
        'correlation': get_return_correlation_matrix(),
    }

# ==================== TÙY CHỈNH CSS ====================
DASHBOARD_STYLE = """
<style>
    /* Nền trang và phông chữ tổng thể */
    html, body, [data-testid="stAppViewContainer"], .main, .block-container {
        background-color: #f5f7fb !important;
        color: #1a202c;
        font-family: "Inter", "Be VietNam Pro", "Segoe UI", sans-serif;
    }

    /* Tiêu đề chính và mô tả */
    .dashboard-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1a202c;
        margin-bottom: 0.5rem;
        letter-spacing: 1px;
        text-transform: uppercase;
    }

    .dashboard-subtitle {
        font-size: 0.95rem;
        color: #4a5568;
        margin-bottom: 2rem;
        letter-spacing: 0.5px;
    }

    /* Thẻ KPI */
    .kpi-card {
        background: linear-gradient(135deg, #ffffff 0%, #edf2f7 100%);
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 8px 16px rgba(15, 23, 42, 0.08);
        border: 1px solid #e2e8f0;
        transition: transform 0.2s, box-shadow 0.2s;
    }

    .kpi-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 20px rgba(15, 23, 42, 0.12);
    }

    .kpi-title {
        font-size: 0.85rem;
        color: #718096;
        font-weight: 600;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .kpi-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1a202c;
        margin-bottom: 0.3rem;
    }

    .kpi-change {
        font-size: 0.9rem;
        font-weight: 600;
    }

    .kpi-change.positive {
        color: #2f855a;
    }

    .kpi-change.negative {
        color: #c53030;
    }

    .kpi-change.neutral {
        color: #d69e2e;
    }

    /* Hộp chứa biểu đồ */
    .chart-container {
        background: #ffffff;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 6px 14px rgba(15, 23, 42, 0.08);
        border: 1px solid #e2e8f0;
    }

    .chart-title {
        font-size: 1rem;
        color: #2d3748;
        font-weight: 600;
        margin-bottom: 1rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }

    /* Thanh hiệu suất ngành */
    .sector-bar {
        background: #edf2f7;
        border-radius: 8px;
        padding: 0.8rem;
        margin-bottom: 0.5rem;
    }

    /* Thanh cuộn */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: #e2e8f0;
    }

    ::-webkit-scrollbar-thumb {
        background: #cbd5f5;
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #a0aec0;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background-color: #ffffff;
        border-radius: 8px;
        padding: 0.5rem;
        border: 1px solid #e2e8f0;
    }

    .stTabs [data-baseweb="tab"] {
        color: #4a5568;
        font-weight: 600;
        font-size: 0.95rem;
        padding: 0.25rem 0.5rem;
    }

    .stTabs [aria-selected="true"] {
        color: #1a202c;
        border-bottom: 3px solid #3182ce;
    }

    .stTabs [data-baseweb="tab-content"] {
        background-color: #ffffff;
        border-radius: 0 0 12px 12px;
        border: 1px solid #e2e8f0;
        margin-top: -0.5rem;
        padding-top: 1.5rem;
    }
</style>
"""


# ==================== MÔ-ĐUN 1: KPI CHỈ SỐ THỊ TRƯỜNG ====================
def generate_market_indices_kpi(metrics):
    """Hiển thị các chỉ số chính dạng thẻ KPI dựa trên dữ liệu thực."""

    if not metrics:
        st.info("Không có dữ liệu chỉ số để hiển thị.")
        return

    cols = st.columns(len(metrics))

    for col, metric in zip(cols, metrics):
        value = metric.get('value')
        change_pct = metric.get('pct_change')
        note = metric.get('note', '')
        timestamp = metric.get('timestamp')

        value_display = f"{value:,.2f}" if value is not None else "—"
        if change_pct is None:
            trend_class = ""
            trend_value = "Chưa có dữ liệu"
        else:
            if change_pct > 0:
                trend_class = "positive"
            elif change_pct < 0:
                trend_class = "negative"
            else:
                trend_class = "neutral"
            trend_value = f"{change_pct:+.2f}%"

        time_suffix = f" · {timestamp.strftime('%d/%m %H:%M')}" if timestamp is not None else ""

        col.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-title">{metric.get('label')}</div>
                <div class="kpi-value">{value_display}</div>
                <div class="kpi-change {trend_class}">{trend_value} · {note}{time_suffix}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _build_realtime_metrics():
    board = get_realtime_index_board(REALTIME_INDEX_SYMBOLS)
    if board is None or board.empty:
        return []

    history_cache = {}

    def _safe_float(value):
        try:
            if pd.isna(value):
                return None
            return float(value)
        except Exception:
            return None

    def _get_sorted_history(symbol_key):
        if symbol_key not in history_cache:
            history = get_index_history(symbol_key, months=1)
            history_cache[symbol_key] = history.sort_values('time') if not history.empty else pd.DataFrame()
        return history_cache[symbol_key]

    metrics = []
    for _, row in board.iterrows():
        symbol_key = str(row['symbol']).upper()
        price = _safe_float(row.get('gia_khop'))
        reference = _safe_float(row.get('gia_tham_chieu'))
        change = _safe_float(row.get('thay_doi'))
        pct_change = _safe_float(row.get('ty_le_thay_doi'))
        note_ts = row.get('last_updated')
        note_text = None

        if reference in (None, 0) and price is not None and change is not None:
            reference = price - change

        if price in (None, 0) and reference not in (None, 0):
            price = reference
            change = 0.0
            pct_change = 0.0
            note_text = 'Chưa có khớp · Hiển thị tham chiếu'
        elif price in (None, 0):
            history = _get_sorted_history(symbol_key)
            if history.empty:
                continue
            last_row = history.iloc[-1]
            prev_row = history.iloc[-2] if len(history) > 1 else last_row
            price = float(last_row['close'])
            reference = float(prev_row['close']) if pd.notna(prev_row['close']) else price
            change = price - reference
            pct_change = (change / reference * 100) if reference not in (0, None) else 0.0
            note_text = 'Dữ liệu cuối phiên'
            note_ts = pd.to_datetime(last_row['time']).to_pydatetime()
        else:
            base_reference = reference if reference not in (None, 0) else None
            if base_reference is None and change is not None:
                base_reference = price - change
            if change is None and base_reference is not None:
                change = price - base_reference
            if pct_change is None and base_reference not in (None, 0):
                pct_change = (change / base_reference * 100) if change is not None else 0.0

        if change is None:
            change = 0.0
        if pct_change is None:
            pct_change = 0.0
        if note_text is None:
            note_text = f"Thay đổi {change:+.2f} điểm"

        metrics.append({
            'symbol': symbol_key,
            'label': REALTIME_LABELS.get(symbol_key, symbol_key),
            'value': price,
            'change': change,
            'pct_change': pct_change,
            'note': note_text,
            'timestamp': note_ts
        })

    available_symbols = {metric['symbol'] for metric in metrics}
    for symbol_key in REALTIME_SYMBOL_KEYS:
        if symbol_key in available_symbols:
            continue
        history = _get_sorted_history(symbol_key)
        if history.empty:
            continue
        last_row = history.iloc[-1]
        prev_row = history.iloc[-2] if len(history) > 1 else last_row
        last_close = float(last_row['close']) if pd.notna(last_row['close']) else None
        prev_close = float(prev_row['close']) if pd.notna(prev_row['close']) else None
        if last_close is None:
            continue
        change = last_close - (prev_close if prev_close is not None else last_close)
        pct_change = (change / prev_close * 100) if prev_close not in (0, None) else 0.0
        metrics.append({
            'symbol': symbol_key,
            'label': REALTIME_LABELS.get(symbol_key, symbol_key),
            'value': last_close,
            'change': change,
            'pct_change': pct_change,
            'note': 'Dữ liệu cuối phiên',
            'timestamp': pd.to_datetime(last_row['time']).to_pydatetime()
        })
    return metrics


def render_realtime_market_overview():
    metrics = _build_realtime_metrics()
    if not metrics:
        st.info("Không thể tải dữ liệu realtime cho các chỉ số.")
        return

    generate_market_indices_kpi(metrics)

    latest_ts = max((metric.get('timestamp') for metric in metrics if metric.get('timestamp')), default=None)
    if latest_ts:
        st.caption(f"Cập nhật: {latest_ts.strftime('%d/%m/%Y %H:%M:%S')}")


# ==================== MÔ-ĐUN 2: SO SÁNH CHỈ SỐ CHÍNH ====================
def generate_index_comparison_chart(index_history: pd.DataFrame):
    """Biểu đồ so sánh VN-Index, HNX và UPCoM dựa trên dữ liệu lịch sử."""

    if index_history is None or index_history.empty:
        fig = go.Figure()
        fig.update_layout(paper_bgcolor=PAPER_BG, plot_bgcolor=PLOT_BG)
        fig.add_annotation(text='Không có dữ liệu chỉ số', xref='paper', yref='paper', x=0.5, y=0.5)
        return fig

    pivot_df = index_history.pivot(index='time', columns='symbol', values='close').dropna(how='all')
    pivot_df = pivot_df.fillna(method='ffill')
    pivot_df = pivot_df.dropna(how='all')

    def normalize_series(series: pd.Series) -> pd.Series:
        first_valid_idx = series.first_valid_index()
        if first_valid_idx is None:
            return series
        base_value = series.loc[first_valid_idx]
        if base_value in (0, None):
            return series
        return (series / base_value - 1) * 100

    pct_change_df = pivot_df.apply(normalize_series)

    fig = go.Figure()

    palette = {
        'VN-Index': '#1D4ED8',
        'HNX-Index': '#F97316',
        'UPCoM': '#7C3AED'
    }

    for column in pct_change_df.columns:
        fig.add_trace(
            go.Scatter(
                x=pct_change_df.index,
                y=pct_change_df[column],
                mode='lines',
                name=column,
                line=dict(color=palette.get(column, '#2d3748'), width=2.6),
                hovertemplate='%{y:+.2f}%<extra></extra>'
            )
        )

    fig.update_layout(
        title=dict(
            text='SO SÁNH CÁC CHỈ SỐ CHÍNH (TỶ LỆ % SO ĐẦU KỲ)',
            font=TITLE_FONT,
            x=0,
            pad=TITLE_PAD
        ),
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(color=FONT_COLOR, size=11),
        hovermode='x unified',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.28,
            xanchor="center",
            x=0.5,
            font=dict(size=12, color=FONT_COLOR),
            bgcolor='rgba(255, 255, 255, 0.95)',
            bordercolor='#e2e8f0',
            borderwidth=1,
            itemclick='toggleothers',
            itemsizing='constant'
        ),
        xaxis=dict(
            gridcolor=GRID_COLOR,
            showgrid=True,
            zeroline=False
        ),
        yaxis=dict(
            gridcolor=GRID_COLOR,
            showgrid=True,
            zeroline=True,
            zerolinecolor=ZERO_LINE_COLOR,
            title='Thay đổi so với đầu kỳ (%)'
        ),
        height=350,
        margin=dict(l=40, r=40, t=50, b=40)
    )


    if len(pct_change_df) > 30:
        anchor_idx = pct_change_df.index[int(len(pct_change_df) * 0.7)]
        anchor_symbol = 'HNX-Index' if 'HNX-Index' in pct_change_df.columns else pct_change_df.columns[0]
        anchor_value = pct_change_df[anchor_symbol].loc[anchor_idx]
        fig.add_annotation(
            x=anchor_idx,
            y=anchor_value,
            text="Xu hướng ngắn hạn",
            showarrow=True,
            arrowhead=2,
            arrowcolor=REFERENCE_COLOR,
            arrowwidth=1.2,
            ax=0,
            ay=-70,
            font=dict(size=10, color='#1a202c'),
            bgcolor='rgba(255, 255, 255, 0.7)',
            bordercolor=REFERENCE_COLOR,
            borderwidth=1
        )

    return fig


# ==================== MÔ-ĐUN 3: DIỄN BIẾN VN-INDEX ====================
def generate_vn_index_trend(vnindex_history: pd.DataFrame):
    """Mô-đun hiển thị xu hướng VN-Index theo dữ liệu thực."""

    if vnindex_history is None or vnindex_history.empty:
        fig = go.Figure()
        fig.update_layout(paper_bgcolor=PAPER_BG, plot_bgcolor=PLOT_BG)
        fig.add_annotation(text='Không có dữ liệu VN-Index', xref='paper', yref='paper', x=0.5, y=0.5)
        return fig

    df = vnindex_history.sort_values('time')

    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['time'],
        y=df['close'],
        mode='lines',
        name='VN-INDEX TR',
        line=dict(color='rgba(37, 99, 235, 1)', width=3),
        fill='tozeroy',
        fillcolor='rgba(191, 219, 254, 0.45)',
        hovertemplate='%{y:.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text='DIỄN BIẾN VN-INDEX',
            font=TITLE_FONT,
            x=0,
            pad=TITLE_PAD
        ),
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(color=FONT_COLOR, size=11),
        showlegend=False,
        xaxis=dict(
            gridcolor=GRID_COLOR,
            showgrid=True,
            zeroline=False
        ),
        yaxis=dict(
            gridcolor=GRID_COLOR,
            showgrid=True,
            zeroline=False,
            range=[df['close'].min()*0.98, df['close'].max()*1.02]
        ),
        height=350,
        margin=dict(l=40, r=40, t=50, b=40)
    )
    
    return fig


# ==================== MÔ-ĐUN 4: HIỆU SUẤT NGÀNH ====================
def generate_sector_performance(sector_perf: pd.DataFrame):
    """Biểu đồ hiệu suất ngành dựa trên dữ liệu vnstock."""

    if sector_perf is None or sector_perf.empty:
        fig = go.Figure()
        fig.update_layout(paper_bgcolor=PAPER_BG, plot_bgcolor=PLOT_BG)
        fig.add_annotation(text='Chưa có dữ liệu ngành', xref='paper', yref='paper', x=0.5, y=0.5)
        return fig

    top_sectors = sector_perf.sort_values('avg_growth_1m', ascending=True)
    colors = [POSITIVE_COLOR if value >= 0 else NEGATIVE_COLOR for value in top_sectors['avg_growth_1m']]

    fig = go.Figure(
        go.Bar(
            y=top_sectors['industry'],
            x=top_sectors['avg_growth_1m'],
            orientation='h',
            marker=dict(
                color=colors,
                line=dict(color='rgba(255, 255, 255, 0.2)', width=1)
            ),
            text=[f"{val:+.1f}%" for val in top_sectors['avg_growth_1m']],
            textposition='outside',
            hovertemplate='%{y}: %{x:+.1f}% (1M) | %{customdata:.1f}% (1W)<extra></extra>',
            customdata=top_sectors['avg_growth_1w']
        )
    )

    fig.update_layout(
        title=dict(
            text='HIỆU SUẤT NGÀNH (CHÊNH LỆCH SO VỚI TRUNG BÌNH)',
            font=TITLE_FONT,
            x=0,
            pad=TITLE_PAD
        ),
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(color=FONT_COLOR, size=11),
        showlegend=False,
        xaxis=dict(
            gridcolor=GRID_COLOR,
            showgrid=True,
            zeroline=True,
            zerolinecolor=ZERO_LINE_COLOR,
            title='Tăng trưởng 1 tháng (%)'
        ),
        yaxis=dict(showgrid=False),
        height=350,
        margin=dict(l=120, r=80, t=50, b=40)
    )

    return fig


# ==================== MÔ-ĐUN 5: VỐN HÓA THEO NGÀNH ====================
def generate_market_cap_treemap(market_cap_df: pd.DataFrame):
    """Treemap tỷ trọng vốn hóa theo ngành từ dữ liệu thực."""

    if market_cap_df is None or market_cap_df.empty:
        return go.Figure()

    top_sectors = market_cap_df
    palette = ['#48bb78', '#f6ad55', '#63b3ed', '#fc8181', '#dd6b20', '#9f7aea', '#38b2ac', '#ed8936']
    colors = [palette[i % len(palette)] for i in range(len(top_sectors))]

    fig = go.Figure(
        go.Treemap(
            labels=top_sectors['industry'],
            parents=[''] * len(top_sectors),
            values=top_sectors['market_cap'],
            marker=dict(colors=colors, line=dict(color='#f5f7fb', width=2)),
            texttemplate='<b>%{label}</b><br>%{value:.0f} tỷ',
            textfont=dict(size=13, color='#1a202c', family='Inter, "Be VietNam Pro", "Segoe UI", sans-serif'),
            hovertemplate='<b>%{label}</b><br>Vốn hóa: %{value:,.0f} tỷ<extra></extra>'
        )
    )

    fig.update_layout(
        title=dict(
            text='TỶ TRỌNG DOANH NGHIỆP THEO NGÀNH',
            font=TITLE_FONT,
            x=0,
            pad=TITLE_PAD
        ),
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(color=FONT_COLOR, size=11),
        height=350,
        margin=dict(l=10, r=10, t=50, b=10)
    )

    return fig


# ==================== MÔ-ĐUN 6: DÒNG TIỀN KHỐI NGOẠI ====================
def generate_net_foreign_buying(foreign_flow_df: pd.DataFrame):
    """Hiển thị Top mua/bán ròng khối ngoại dạng 2 cột đối xứng."""

    if foreign_flow_df is None or foreign_flow_df.empty:
        fig = go.Figure()
        fig.update_layout(paper_bgcolor=PAPER_BG, plot_bgcolor=PLOT_BG)
        fig.add_annotation(text='Không có dữ liệu giao dịch khối ngoại', xref='paper', yref='paper', x=0.5, y=0.5)
        return fig

    df = foreign_flow_df.copy()
    buys = df[df['foreign_buysell_20s'] > 0].nlargest(5, 'foreign_buysell_20s')
    sells = df[df['foreign_buysell_20s'] < 0].nsmallest(5, 'foreign_buysell_20s')

    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=("Top Mua", "Top Bán"),
        horizontal_spacing=0.12
    )

    if not buys.empty:
        buy_custom = np.column_stack((buys['industry'], buys['foreign_buysell_20s'])).tolist()
        fig.add_trace(
            go.Bar(
                x=buys['foreign_buysell_20s'],
                y=buys['ticker'],
                orientation='h',
                marker_color=POSITIVE_COLOR,
                text=[f"{val:,.0f}" for val in buys['foreign_buysell_20s']],
                textposition='outside',
                hovertemplate='%{y} · %{customdata[0]}<br>Mua ròng: %{customdata[1]:,.0f} tỷ<extra></extra>',
                customdata=buy_custom,
                name='Top Mua'
            ),
            row=1,
            col=1
        )

    if not sells.empty:
        sell_values = np.abs(sells['foreign_buysell_20s'])
        sell_custom = np.column_stack((sells['industry'], sell_values)).tolist()
        fig.add_trace(
            go.Bar(
                x=sell_values,
                y=sells['ticker'],
                orientation='h',
                marker_color=NEGATIVE_COLOR,
                text=[f"{val:,.0f}" for val in sell_values],
                textposition='outside',
                hovertemplate='%{y} · %{customdata[0]}<br>Bán ròng: %{customdata[1]:,.0f} tỷ<extra></extra>',
                customdata=sell_custom,
                name='Top Bán'
            ),
            row=1,
            col=2
        )

    fig.update_layout(
        title=dict(
            text='GIÁ TRỊ MUA/BÁN RÒNG KHỐI NGOẠI (20 PHIÊN)',
            font=TITLE_FONT,
            x=0,
            pad=TITLE_PAD
        ),
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PAPER_BG,
        font=dict(color=FONT_COLOR, size=11),
        showlegend=False,
        height=350,
        margin=dict(l=40, r=40, t=70, b=40)
    )

    fig.update_xaxes(
        row=1,
        col=1,
        showgrid=False,
        zeroline=False,
        title_text='Giá trị mua ròng (tỷ VND)'
    )
    fig.update_yaxes(
        row=1,
        col=1,
        autorange='reversed',
        tickfont=dict(size=13, color=FONT_COLOR)
    )

    fig.update_xaxes(
        row=1,
        col=2,
        showgrid=False,
        zeroline=False,
        title_text='Giá trị bán ròng (tỷ VND)'
    )
    fig.update_yaxes(
        row=1,
        col=2,
        autorange='reversed',
        tickfont=dict(size=13, color=FONT_COLOR)
    )

    return fig


# ==================== MÔ-ĐUN 7: TƯƠNG QUAN LẠM PHÁT ====================
def generate_inflation_correlation(liquidity_df: pd.DataFrame):
    """Biểu đồ scatter thể hiện mối tương quan giữa tăng trưởng giá và thanh khoản."""

    if liquidity_df is None or liquidity_df.empty:
        fig = go.Figure()
        fig.update_layout(paper_bgcolor=PAPER_BG, plot_bgcolor=PLOT_BG)
        fig.add_annotation(text='Không có dữ liệu thanh khoản', xref='paper', yref='paper', x=0.5, y=0.5)
        return fig

    df = liquidity_df.copy()
    size_base = df['market_cap'].replace({0: np.nan}).max()
    if pd.isna(size_base) or size_base == 0:
        size_base = 1
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['avg_trading_value_20d'],
        y=df['price_growth_1m'],
        mode='markers',
        marker=dict(
            size=np.clip(df['market_cap'] / size_base * 30, 8, 30),
            color=[POSITIVE_COLOR if val >= 0 else NEGATIVE_COLOR for val in df['price_growth_1m']],
            line=dict(color='#ffffff', width=0.5)
        ),
        text=df['ticker'],
        hovertemplate='%{text} · %{customdata}<br>Tăng trưởng: %{y:.2f}%<br>Thanh khoản: %{x:,.1f} tỷ<extra></extra>',
        customdata=df['industry']
    ))

    fig.update_layout(
        title=dict(
            text='TĂNG TRƯỞNG VS THANH KHOẢN',
            font=TITLE_FONT,
            x=0,
            pad=TITLE_PAD
        ),
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(color=FONT_COLOR, size=11),
        xaxis=dict(
            gridcolor=GRID_COLOR,
            showgrid=True,
            zeroline=False,
            title='Thanh khoản TB 20 phiên (tỷ VND)'
        ),
        yaxis=dict(
            gridcolor=GRID_COLOR,
            showgrid=True,
            zeroline=False,
            title='Tăng trưởng 1 tháng (%)'
        ),
        height=350,
        margin=dict(l=40, r=40, t=50, b=40)
    )
    
    return fig


# ==================== MÔ-ĐUN 8: MA TRẬN TƯƠNG QUAN ====================
def generate_correlation_matrix(correlation_df: pd.DataFrame):
    """Hiển thị ma trận tương quan lợi suất thực tế."""

    if correlation_df is None or correlation_df.empty:
        fig = go.Figure()
        fig.update_layout(paper_bgcolor=PAPER_BG, plot_bgcolor=PLOT_BG)
        fig.add_annotation(text='Không đủ dữ liệu để tính tương quan', xref='paper', yref='paper', x=0.5, y=0.5)
        return fig

    fig = go.Figure(data=go.Heatmap(
        z=correlation_df.values,
        x=correlation_df.columns,
        y=correlation_df.index,
        colorscale=[
            [0, '#ebf4ff'],
            [0.5, '#90cdf4'],
            [1, '#2b6cb0']
        ],
        text=np.round(correlation_df.values, 2),
        texttemplate='%{text:.1f}',
        textfont=dict(size=13, color='#1a202c'),
        hovertemplate='%{x} so với %{y}<br>Hệ số: %{z:.2f}<extra></extra>',
        colorbar=dict(
            thickness=15,
            len=0.7,
            bgcolor=PAPER_BG,
            tickfont=dict(color=FONT_COLOR),
            title=dict(text='Hệ số', side='right', font=dict(color=FONT_COLOR))
        )
    ))
    
    fig.update_layout(
        title=dict(
            text='MA TRẬN TƯƠNG QUAN',
            font=TITLE_FONT,
            x=0,
            pad=TITLE_PAD
        ),
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(color=FONT_COLOR, size=11),
        xaxis=dict(
            side='bottom',
            showgrid=False
        ),
        yaxis=dict(
            showgrid=False,
            autorange='reversed'
        ),
        height=350,
        margin=dict(l=120, r=40, t=50, b=80)
    )
    
    return fig


# ==================== MÔ-ĐUN 9: BẢN ĐỒ NHIỆT LẠM PHÁT ====================
def generate_inflation_heatmap(heatmap_df: pd.DataFrame):
    """Bản đồ nhiệt thể hiện các chỉ số ngành (tăng trưởng & thanh khoản)."""

    if heatmap_df is None or heatmap_df.empty:
        fig = go.Figure()
        fig.update_layout(paper_bgcolor=PAPER_BG, plot_bgcolor=PLOT_BG)
        fig.add_annotation(text='Không có dữ liệu heatmap', xref='paper', yref='paper', x=0.5, y=0.5)
        return fig

    pivot = heatmap_df.pivot(index='industry', columns='metric', values='value')
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        colorscale=[
            [0, '#fefcbf'],
            [0.5, '#f6ad55'],
            [1, '#c05621']
        ],
        text=np.round(pivot.values, 2),
        texttemplate='%{text:.1f}',
        textfont=dict(size=14, color='#1a202c', weight='bold'),
        hovertemplate='%{y} - %{x}<br>Giá trị: %{z:.1f}<extra></extra>',
        showscale=False
    ))
    
    fig.update_layout(
        title=dict(
            text='HEATMAP HIỆU SUẤT NGÀNH',
            font=TITLE_FONT,
            x=0,
            pad=TITLE_PAD
        ),
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(color=FONT_COLOR, size=11),
        xaxis=dict(
            side='top',
            showgrid=False
        ),
        yaxis=dict(
            showgrid=False
        ),
        height=250,
        margin=dict(l=60, r=40, t=70, b=40)
    )
    
    return fig


# ==================== KHU VỰC HIỂN THỊ CHÍNH ====================
def render_bang_dieu_hanh():
    """Hiển thị bảng điều hành chính cho tab Tổng quan Thị trường & Ngành."""
    st.markdown(DASHBOARD_STYLE, unsafe_allow_html=True)

    st.markdown('<div class="dashboard-header">PHÂN TÍCH THỊ TRƯỜNG & NGÀNH</div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-subtitle">Dữ liệu tổng hợp theo tháng & cập nhật theo thời gian thực</div>', unsafe_allow_html=True)

    with st.spinner("Đang tải dữ liệu tổng quan..."):
        overview_data = load_overview_data()

    with st.spinner("Đang tải dữ liệu thị trường..."):
        render_realtime_market_overview()

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.plotly_chart(
            generate_index_comparison_chart(overview_data.get('index_history')), use_container_width=True
        )
        market_cap_placeholder = st.empty()

    with col2:
        st.plotly_chart(
            generate_vn_index_trend(overview_data.get('vnindex_history')), use_container_width=True
        )
        foreign_flow_placeholder = st.empty()

    with col3:
        sector_perf_placeholder = st.empty()
        liquidity_placeholder = st.empty()

    st.markdown("<br>", unsafe_allow_html=True)

    col4, col5 = st.columns(2)
    correlation_placeholder = col4.empty()
    heatmap_placeholder = col5.empty()

    detail_data = None
    detail_spinner_placeholder = st.empty()
    with detail_spinner_placeholder.container():
        with st.spinner("Đang tải dữ liệu ngành & dòng tiền..."):
            detail_data = load_detail_data()
    detail_spinner_placeholder.empty()

    if detail_data:
        market_cap_placeholder.plotly_chart(
            generate_market_cap_treemap(detail_data.get('market_cap')), use_container_width=True
        )
        foreign_flow_placeholder.plotly_chart(
            generate_net_foreign_buying(detail_data.get('foreign_flow')), use_container_width=True
        )
        sector_perf_placeholder.plotly_chart(
            generate_sector_performance(detail_data.get('sector_perf')), use_container_width=True
        )
        liquidity_placeholder.plotly_chart(
            generate_inflation_correlation(detail_data.get('liquidity')), use_container_width=True
        )
        correlation_placeholder.plotly_chart(
            generate_correlation_matrix(detail_data.get('correlation')), use_container_width=True
        )
        heatmap_placeholder.plotly_chart(
            generate_inflation_heatmap(detail_data.get('sector_heatmap')), use_container_width=True
        )
    else:
        market_cap_placeholder.info("Không thể tải dữ liệu ngành.")
        foreign_flow_placeholder.info("Không thể tải dữ liệu ngành.")
        sector_perf_placeholder.info("Không thể tải dữ liệu ngành.")
        liquidity_placeholder.info("Không thể tải dữ liệu ngành.")
        correlation_placeholder.info("Không thể tải dữ liệu ngành.")
        heatmap_placeholder.info("Không thể tải dữ liệu ngành.")


def main():
    """Giữ hàm main để có thể chạy file độc lập."""
    render_bang_dieu_hanh()


if __name__ == "__main__":
    st.set_page_config(
        page_title="Bảng điều hành tài chính",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    main()
