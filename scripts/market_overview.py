"""
Module market_overview.py
Chứa các hàm liên quan đến tổng quan thị trường và phân tích ngành.
"""

import warnings
warnings.filterwarnings('ignore', message='pkg_resources is deprecated')

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from scripts.config import ANALYSIS_START_DATE, ANALYSIS_END_DATE, DEFAULT_MARKET, DEFAULT_INVESTMENT_AMOUNT
from scripts.session_manager import save_market_overview_state, get_market_overview_state


def show_market_heatmap(df, data_loader_module, preselected_sector=None, preselected_exchange=None):
    """
    Hiển thị Biểu đồ nhiệt (heatmap) của thị trường.
    
    Args:
        df (pd.DataFrame): DataFrame chứa thông tin công ty
        data_loader_module: Module data_loader để lấy dữ liệu giá
        preselected_sector (str): Ngành được chọn trước (từ drill-down)
        preselected_exchange (str): Sàn được chọn trước (từ drill-down)
    """
    st.subheader("Biểu đồ Nhiệt Thị trường")
    
    # Hiển thị thông báo nếu đang drill-down từ ngành
    if preselected_sector:
        st.info(f"Đang hiển thị chi tiết ngành: **{preselected_sector}**")
    
    # Chọn sàn và ngành
    col1, col2 = st.columns(2)
    with col1:
        exchanges = df['exchange'].unique()
        # Ưu tiên sàn được chọn trước, nếu không thì dùng mặc định
        if preselected_exchange and preselected_exchange in exchanges:
            default_index = list(exchanges).index(preselected_exchange)
        else:
            default_index = list(exchanges).index(DEFAULT_MARKET) if DEFAULT_MARKET in exchanges else 0
        exchange = st.selectbox(
            "Chọn sàn giao dịch",
            exchanges,
            index=default_index,
            key="heatmap_exchange"
        )
    
    filtered_df = df[df['exchange'] == exchange]
    
    with col2:
        sectors_list = ["Tất cả"] + list(filtered_df['icb_name'].unique())
        # Ưu tiên ngành được chọn trước
        if preselected_sector and preselected_sector in sectors_list:
            default_sector_index = sectors_list.index(preselected_sector)
        else:
            default_sector_index = 0
        sector = st.selectbox(
            "Chọn ngành",
            sectors_list,
            index=default_sector_index,
            key="heatmap_sector"
        )
    
    # Lọc theo ngành
    if sector != "Tất cả":
        filtered_df = filtered_df[filtered_df['icb_name'] == sector]
    
    # Giới hạn số lượng mã cổ phiếu
    max_stocks = st.slider("Số lượng mã cổ phiếu hiển thị", 10, 50, 20, key="heatmap_stocks")
    stocks = filtered_df['symbol'].tolist()[:max_stocks]
    
    if st.button("Tạo Biểu đồ Nhiệt", key="create_heatmap") or preselected_sector:
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=7)

        st.info(f"Đang tải dữ liệu cho {len(stocks)} mã cổ phiếu...")
        data, skipped = data_loader_module.fetch_stock_data2(stocks, start_date, end_date)

        if data.empty:
            st.error("Không có dữ liệu để hiển thị.")
            return

        # Tính toán % thay đổi
        pct_change = ((data.iloc[-1] - data.iloc[0]) / data.iloc[0] * 100).sort_values(ascending=False)

        # Lấy thông tin chi tiết cho tooltip và tính vốn hóa
        st.info("Đang lấy thông tin vốn hóa thị trường...")
        tooltip_data = {}
        market_caps = {}
        
        # Lấy dữ liệu fundamental để có vốn hóa
        fundamental_data = data_loader_module.fetch_fundamental_data_batch(list(pct_change.index))
        
        for symbol in pct_change.index:
            company_info = filtered_df[filtered_df['symbol'] == symbol]
            if company_info.empty:
                continue
            
            # Lấy giá đóng cửa mới nhất (chỉ để tính vốn hóa)
            closing_price = data[symbol].iloc[-1] if symbol in data.columns else None
            
            # Lấy thông tin từ fundamental data
            market_cap = None
            
            if fundamental_data is not None and not fundamental_data.empty:
                fund_info = fundamental_data[fundamental_data['symbol'] == symbol]
                if not fund_info.empty:
                    # Tính vốn hóa thị trường = EPS * P/E * số lượng cổ phiếu
                    # Hoặc có thể ước tính từ giá * khối lượng trung bình
                    eps = fund_info.iloc[0].get('eps', None)
                    pe = fund_info.iloc[0].get('pe', None)
                    
                    if eps and pe and pd.notna(eps) and pd.notna(pe) and closing_price:
                        # Ước tính số cổ phiếu từ EPS
                        # Market cap ước tính = Giá hiện tại / EPS * Lợi nhuận
                        profit = fund_info.iloc[0].get('profit', None)
                        if profit and pd.notna(profit):
                            market_cap = abs(float(profit)) * float(pe) if float(pe) > 0 else None
            
            # Nếu không có market cap, ước tính từ giá trị giao dịch
            if not market_cap or market_cap <= 0:
                # Ước tính giá trị giao dịch = giá TB * volume ước tính
                avg_price = data[symbol].mean() if symbol in data.columns else closing_price
                # Sử dụng giá trung bình làm proxy cho kích thước
                market_cap = float(avg_price) * 1000000 if avg_price else 1000000
            
            # Lưu market cap
            market_caps[symbol] = market_cap
            
            # Tạo tooltip text
            company_name = company_info.iloc[0]['organ_name']
            tooltip_data[symbol] = {
                'company_name': company_name,
                'market_cap': market_cap,
                'change_pct': pct_change[symbol]
            }
        
        # Tạo custom hover text
        hover_texts = []
        treemap_values = []
        
        for symbol in pct_change.index:
            if symbol in tooltip_data:
                info = tooltip_data[symbol]
                market_cap_display = f"{info['market_cap']/1000:,.0f} tỷ" if info['market_cap'] and info['market_cap'] > 1000 else f"{info['market_cap']:,.0f} triệu"
                
                hover_text = (
                    f"<b>{symbol}</b><br>"
                    f"{info['company_name'][:50]}<br>"
                    f"──────────────────<br>"
                    f"Thay đổi: <b>{info['change_pct']:.2f}%</b><br>"
                    f"Vốn hóa (ước tính): {market_cap_display} VND"
                )
                treemap_values.append(market_caps.get(symbol, 1000000))
            else:
                hover_text = f"<b>{symbol}</b><br>Thay đổi: {pct_change[symbol]:.2f}%"
                treemap_values.append(1000000)
            hover_texts.append(hover_text)
        
        # Vẽ biểu đồ treemap với kích thước theo vốn hóa và dải màu gradient mượt mà
        # Tạo colorscale tùy chỉnh với nhiều điểm chuyển tiếp để có gradient mượt mà hơn
        custom_colorscale = [
            [0.0, '#8B0000'],    # Đỏ đậm - giảm mạnh nhất
            [0.15, '#DC143C'],   # Đỏ tươi - giảm mạnh
            [0.25, '#FF6347'],   # Đỏ cam - giảm vừa
            [0.35, '#FFA07A'],   # Đỏ nhạt - giảm nhẹ
            [0.45, '#F5DEB3'],   # Be nhạt - gần 0
            [0.48, '#E8E8E8'],   # Xám rất nhạt - rất gần 0
            [0.50, '#D3D3D3'],   # Xám nhạt - 0%
            [0.52, '#E8E8E8'],   # Xám rất nhạt - rất gần 0
            [0.55, '#E0F2E9'],   # Xanh rất nhạt - gần 0
            [0.65, '#B2DFDB'],   # Xanh nhạt - tăng nhẹ
            [0.75, '#66BB6A'],   # Xanh lá - tăng vừa
            [0.85, '#43A047'],   # Xanh đậm - tăng mạnh
            [1.0, '#2E7D32']     # Xanh đậm nhất - tăng mạnh nhất
        ]
        
        fig = go.Figure(go.Treemap(
            labels=pct_change.index,
            parents=[""] * len(pct_change),
            values=treemap_values,  # Sử dụng vốn hóa thay vì % thay đổi
            text=[f"{x:.2f}%" for x in pct_change.values],
            textposition="middle center",
            hovertext=hover_texts,
            hovertemplate='%{hovertext}<extra></extra>',
            marker=dict(
                colors=pct_change.values,
                colorscale=custom_colorscale,
                cmid=0,  # Điểm giữa tại 0%
                cmin=max(pct_change.min(), -10),  # Giới hạn min để màu không quá cực đoan
                cmax=min(pct_change.max(), 10),   # Giới hạn max để màu không quá cực đoan
                colorbar=dict(
                    title=dict(
                        text="% Thay đổi",
                        side="right"
                    ),
                    tickmode="linear",
                    tick0=-10,
                    dtick=2,
                    thickness=15,
                    len=0.7,
                    x=1.02
                ),
                line=dict(width=2, color='white')
            )
        ))
        
        fig.update_layout(
            title=f"Biểu đồ Nhiệt - {sector if sector != 'Tất cả' else 'Tất cả Ngành'} ({exchange})<br>"
                  f"<sub>Kích thước ô = Vốn hóa thị trường | "
                  f"Màu sắc: Đỏ đậm (giảm mạnh) → Xám (không đổi) → Xanh đậm (tăng mạnh)</sub>",
            height=600,
            font=dict(size=11)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Thống kê chi tiết
        st.markdown("### Thống kê Thị trường")

        # Tính toán số mã cổ phiếu tăng, giảm, biến động nhẹ
        num_increase = (pct_change > 0.5).sum()  # Tăng > 0.5%
        num_decrease = (pct_change < -0.5).sum()  # Giảm > 0.5%
        num_light_fluctuation = ((pct_change >= -0.5) & (pct_change <= 0.5)).sum()  # Biến động nhẹ trong khoảng ±0.5%
        total = len(pct_change)

        # Tính trung bình theo trọng số vốn hóa
        total_market_cap = sum(market_caps.values())
        weighted_avg_change = sum(pct_change[symbol] * market_caps.get(symbol, 0) / total_market_cap 
                                  for symbol in pct_change.index if symbol in market_caps)
        simple_avg_change = pct_change.mean()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Tăng giá",
                f"{num_increase} mã",
                f"{num_increase/total*100:.1f}%",
                help="Số mã cổ phiếu tăng giá > 0.5%"
            )
        
        with col2:
            st.metric(
                "Giảm giá",
                f"{num_decrease} mã",
                f"{num_decrease/total*100:.1f}%",
                help="Số mã cổ phiếu giảm giá > 0.5%"
            )
        
        with col3:
            st.metric(
                "Biến động nhẹ",
                f"{num_light_fluctuation} mã",
                f"{num_light_fluctuation/total*100:.1f}%",
                help="Số mã cổ phiếu có biến động nhẹ trong khoảng ±0.5% (không tăng/giảm mạnh)"
            )
        
        with col4:
            st.metric(
                "Tổng số",
                f"{total} mã"
            )
        
        # Hiển thị các chỉ số trung bình
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "Thay đổi TB (Đơn giản)",
                f"{simple_avg_change:.2f}%",
                help="Trung bình cộng đơn giản của % thay đổi giá tất cả cổ phiếu"
            )
        
        with col2:
            st.metric(
                "Thay đổi TB (Theo Vốn hóa)",
                f"{weighted_avg_change:.2f}%",
                help="Trung bình có trọng số theo vốn hóa thị trường - phản ánh tác động của các cổ phiếu lớn"
            )


def show_sector_treemap(df, data_loader_module):
    """
    Hiển thị biểu đồ cây phân cấp theo ngành và công ty.
    Cấp 1: Ngành
    Cấp 2: Công ty trong ngành
    Màu sắc: Tăng trưởng (xanh = tăng, đỏ = giảm)
    Kích thước: Vốn hóa thị trường
    
    Args:
        df (pd.DataFrame): DataFrame chứa thông tin công ty
        data_loader_module: Module data_loader để lấy dữ liệu giá
    """
    st.subheader("Biểu đồ Cây Phân tích Hiệu Suất Ngành")
    st.markdown("*Biểu đồ phân cấp: Ngành > Công ty. Kích thước ô thể hiện Vốn hóa thị trường. Màu sắc thể hiện % tăng trưởng giá (xanh = tăng, đỏ = giảm).*")
    
    # Chọn sàn giao dịch
    col1, col2 = st.columns(2)
    with col1:
        exchanges = df['exchange'].unique()
        default_index = list(exchanges).index(DEFAULT_MARKET) if DEFAULT_MARKET in exchanges else 0
        exchange = st.selectbox(
            "Chọn sàn giao dịch",
            exchanges,
            index=default_index,
            key="treemap_exchange"
        )
    
    with col2:
        analysis_period = st.selectbox(
            "Khoảng thời gian tính tăng trưởng",
            ["1 Tuần", "1 Tháng", "3 Tháng", "6 Tháng"],
            key="treemap_period"
        )
    
    # Lọc theo sàn
    filtered_df = df[df['exchange'] == exchange]
    
    # Giới hạn số lượng cổ phiếu mỗi ngành
    max_stocks_per_sector = st.slider(
        "Số lượng công ty tối đa mỗi ngành",
        5, 20, 10,
        key="treemap_stocks_per_sector"
    )
    
    # Chọn ngành để phân tích (tối đa 5 ngành)
    all_sectors = list(filtered_df['icb_name'].unique())
    selected_sectors = st.multiselect(
        "Chọn ngành để phân tích (tối đa 5 ngành)",
        all_sectors,
        default=all_sectors[:5] if len(all_sectors) >= 5 else all_sectors,
        max_selections=5,
        key="treemap_sectors"
    )
    
    if not selected_sectors:
        st.warning("Vui lòng chọn ít nhất một ngành để phân tích.")
        return
    
    if st.button("Tạo Biểu đồ Cây", key="create_treemap"):
        # Tính toán ngày
        end_date = datetime.now().date()
        period_map = {
            "1 Tuần": 7,
            "1 Tháng": 30,
            "3 Tháng": 90,
            "6 Tháng": 180
        }
        start_date = end_date - timedelta(days=period_map[analysis_period])
        
        treemap_data = []
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for idx, sector in enumerate(selected_sectors):
            status_text.text(f"Đang xử lý ngành {sector}... ({idx+1}/{len(selected_sectors)})")
            
            # Lấy danh sách công ty trong ngành
            sector_companies = filtered_df[filtered_df['icb_name'] == sector]['symbol'].tolist()[:max_stocks_per_sector]
            
            if not sector_companies:
                continue
            
            # Lấy dữ liệu giá
            price_data, skipped = data_loader_module.fetch_stock_data2(
                sector_companies,
                start_date,
                end_date
            )
            
            if price_data.empty:
                continue
            
            # Lấy dữ liệu phân tích cơ bản để tính vốn hóa thị trường 
            fundamental_data = data_loader_module.fetch_fundamental_data_batch(sector_companies)
            
            sector_total_market_cap = 0
            sector_weighted_growth = 0
            sector_company_count = 0
            
            for company in sector_companies:
                if company not in price_data.columns:
                    continue
                
                # Tính % thay đổi giá
                company_prices = price_data[company].dropna()
                if len(company_prices) < 2:
                    continue
                
                price_change = ((company_prices.iloc[-1] - company_prices.iloc[0]) / company_prices.iloc[0]) * 100
                
                # Tính vốn hóa thị trường 
                closing_price = company_prices.iloc[-1]
                market_cap = None
                
                if fundamental_data is not None and not fundamental_data.empty:
                    company_fund = fundamental_data[fundamental_data['symbol'] == company]
                    if not company_fund.empty:
                        eps = company_fund.iloc[0].get('eps', None)
                        pe = company_fund.iloc[0].get('pe', None)
                        
                        if eps and pe and pd.notna(eps) and pd.notna(pe) and closing_price:
                            profit = company_fund.iloc[0].get('profit', None)
                            if profit and pd.notna(profit):
                                market_cap = abs(float(profit)) * float(pe) if float(pe) > 0 else None
                
                # Nếu không có market cap, ước tính từ giá trị giao dịch
                if not market_cap or market_cap <= 0:
                    avg_price = company_prices.mean()
                    market_cap = float(avg_price) * 1000000 if avg_price else 1000000
                
                # Lấy tên công ty
                company_name = filtered_df[filtered_df['symbol'] == company]['organ_name'].values
                company_display = company_name[0] if len(company_name) > 0 else company
                
                # Format vốn hóa để hiển thị
                market_cap_display = f"{market_cap/1000:,.0f} tỷ" if market_cap > 1000 else f"{market_cap:,.0f} triệu"
                
                # Tạo hover text chi tiết (ẩn giá đầu và giá cuối)
                hover_text = (
                    f"<b>{company}</b><br>"
                    f"{company_display}<br>"
                    f"──────────────────<br>"
                    f"Ngành: {sector}<br>"
                    f"Tăng trưởng: <b>{price_change:.2f}%</b><br>"
                    f"Vốn hóa TT (ước tính): {market_cap_display} VND"
                )
                
                treemap_data.append({
                    'labels': company,  # Chỉ hiển thị mã cổ phiếu
                    'parents': sector,
                    'values': market_cap,
                    'growth': price_change,
                    'text': f"{price_change:+.2f}%",  # Hiển thị mã và % ở 2 dòng riêng
                    'hover': hover_text,
                    'symbol': company,
                    'company_name': company_display,
                    'sector': sector
                })
                
                # Tích lũy cho tính toán ngành
                sector_total_market_cap += market_cap
                sector_weighted_growth += price_change * market_cap
                sector_company_count += 1
            
            # Tính tăng trưởng trung bình có trọng số theo vốn hóa
            sector_avg_growth = sector_weighted_growth / sector_total_market_cap if sector_total_market_cap > 0 else 0
            # Tính tăng trưởng trung bình có trọng số theo vốn hóa
            sector_avg_growth = sector_weighted_growth / sector_total_market_cap if sector_total_market_cap > 0 else 0
            
            # Đếm số công ty trong ngành
            num_companies = sector_company_count
            
            # Format vốn hóa tổng
            market_cap_total_display = f"{sector_total_market_cap/1000:,.0f} tỷ" if sector_total_market_cap > 1000 else f"{sector_total_market_cap:,.0f} triệu"
            
            # Hover text cho ngành - hiển thị cả % tăng trưởng
            sector_hover = (
                f"<b>{sector}</b><br>"
                f"──────────────────<br>"
                f"Số công ty: {num_companies}<br>"
                f"Tăng trưởng TB (theo VH): <b>{sector_avg_growth:+.2f}%</b><br>"
                f"Tổng vốn hóa TT: {market_cap_total_display} VND<br>"
                f"<br><i>Click để xem chi tiết!</i>"
            )
            
            treemap_data.append({
                'labels': sector,
                'parents': '',
                'values': sector_total_market_cap,
                'growth': sector_avg_growth,
                'text': f"{sector_avg_growth:+.2f}%",
                'hover': sector_hover,
                'symbol': '',
                'company_name': '',
                'sector': sector
            })
            
            progress_bar.progress((idx + 1) / len(selected_sectors))
        
        progress_bar.empty()
        status_text.empty()
        
        if not treemap_data:
            st.error("Không có dữ liệu để hiển thị biểu đồ cây.")
            return
        
        # Tạo DataFrame
        treemap_df = pd.DataFrame(treemap_data)
        
        # Tạo biểu đồ Treemap với cải thiện hiển thị
        fig = go.Figure(go.Treemap(
            labels=treemap_df['labels'],
            parents=treemap_df['parents'],
            values=treemap_df['values'],
            text=treemap_df['text'],
            textposition="middle center",
            textfont=dict(size=11, family="Arial"),
            hovertext=treemap_df['hover'],
            hovertemplate='%{hovertext}<extra></extra>',
            customdata=treemap_df[['sector', 'symbol', 'company_name']].values,
            marker=dict(
                colors=treemap_df['growth'],
                colorscale=[
                    [0, '#d32f2f'],      # Đỏ đậm (giảm mạnh)
                    [0.25, '#ef5350'],   # Đỏ nhạt
                    [0.45, '#ffcdd2'],   # Đỏ rất nhạt
                    [0.5, '#f5f5f5'],    # Xám nhạt (không thay đổi)
                    [0.55, '#c8e6c9'],   # Xanh rất nhạt
                    [0.75, '#66bb6a'],   # Xanh lá
                    [1, '#2e7d32']       # Xanh đậm (tăng mạnh)
                ],
                cmid=0,
                colorbar=dict(
                    title=dict(
                        text="% Tăng trưởng",
                        side="right",
                        font=dict(size=12)
                    ),
                    thickness=20,
                    len=0.7,
                    tickmode="linear",
                    tick0=-10,
                    dtick=2
                ),
                line=dict(width=3, color='white'),  # Đường viền dày hơn để phân biệt rõ các ngành
                pad=dict(t=35, l=5, r=5, b=5)  # Thêm padding để tránh khoảng trống
            ),
            branchvalues="total",  # Đảm bảo các ô con lấp đầy không gian
            pathbar=dict(visible=False),  # Ẩn thanh đường dẫn để gọn gàng hơn
            marker_coloraxis=None  # Cho phép màu sắc áp dụng cho cả node cha và con
        ))
        
        fig.update_layout(
            title=dict(
                text=f"Biểu đồ Cây Phân tích Hiệu Suất Ngành - {exchange} ({analysis_period})<br>"
                     f"<sub>Kích thước ô = Vốn hóa thị trường | Màu sắc = % Tăng trưởng giá (Đỏ: giảm, Xanh: tăng)</sub>",
                font=dict(size=16)
            ),
            height=700,
            font=dict(size=11),
            margin=dict(t=100, l=10, r=10, b=10)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Thống kê tổng quan
        st.markdown("### Thống kê Tổng quan")
        col1, col2, col3, col4 = st.columns(4)
        
        companies_data = treemap_df[treemap_df['parents'] != '']
        
        with col1:
            st.metric(
                "Tổng số công ty",
                len(companies_data)
            )
        
        with col2:
            positive = len(companies_data[companies_data['growth'] > 0])
            st.metric(
                "Số CP tăng giá",
                positive,
                f"{positive/len(companies_data)*100:.1f}%"
            )
        
        with col3:
            st.metric(
                "Tăng trưởng TB",
                f"{companies_data['growth'].mean():.2f}%",
                help="Tăng trưởng trung bình được tính theo trọng số vốn hóa thị trường. Phản ánh chính xác hơn so với trung bình đơn giản vì tính đến tác động của các công ty có vốn hóa lớn."
            )
        
        with col4:
            best_company = companies_data.loc[companies_data['growth'].idxmax()]
            st.metric(
                "Tăng mạnh nhất",
                best_company['labels'].split('<br>')[0],
                f"+{best_company['growth']:.2f}%"
            )
        
        # Top 5 công ty với tùy chọn sắp xếp
        st.markdown("### Top 5 Công ty Tăng trưởng Cao nhất")
        
       # Sắp xếp theo tăng trưởng
        companies_data_copy = companies_data.copy()
        top_companies = companies_data_copy.nlargest(5, 'growth')
        top_companies = top_companies[['labels', 'growth', 'parents', 'values']].copy()
        top_companies['Mã CP'] = top_companies['labels'].apply(lambda x: x.split('<br>')[0])
        top_companies['Ngành'] = top_companies['parents']
        top_companies['Tăng trưởng (%)'] = top_companies['growth'].round(2)
        top_companies['Vốn hóa (tỷ VND)'] = (top_companies['values'] / 1000).round(2)
        
        display_df = top_companies[['Mã CP', 'Ngành', 'Tăng trưởng (%)', 'Vốn hóa (tỷ VND)']]
        
        st.info("Các công ty có tốc độ tăng trưởng giá cao nhất trong khoảng thời gian phân tích")
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )


def show_sector_overview_page(df, data_loader_module):
    """
    Hiển thị trang tổng quan ngành đầy đủ.
    
    Args:
        df (pd.DataFrame): DataFrame chứa thông tin công ty
        data_loader_module: Module data_loader để lấy dữ liệu giá
    """
    st.title("Tổng quan Thị trường & Ngành")
    
    # Lấy trạng thái đã lưu
    market_state = get_market_overview_state()
    
    # Kiểm tra xem có drill-down từ biểu đồ cây không
    drilldown_sector = st.session_state.get('drilldown_sector', None)
    drilldown_exchange = st.session_state.get('drilldown_exchange', None)
    
    # Nếu có drill-down, hiển thị nút quay lại
    if drilldown_sector:
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("Quay lại", key="back_button"):
                # Xóa session state và reload
                if 'drilldown_sector' in st.session_state:
                    del st.session_state['drilldown_sector']
                if 'drilldown_exchange' in st.session_state:
                    del st.session_state['drilldown_exchange']
                # Cập nhật trạng thái
                save_market_overview_state(None, 'market')
                st.rerun()
        with col2:
            st.info(f"Đang xem chi tiết ngành: **{drilldown_sector}** trên sàn **{drilldown_exchange}**")
        
        # Lưu trạng thái
        save_market_overview_state(drilldown_exchange, 'sector')
    
    # Tạo tabs
    tab1, tab2 = st.tabs(["Biểu đồ Nhiệt", "Biểu đồ Cây"])
    
    # Nếu có drill-down, mặc định hiển thị tab Biểu đồ Nhiệt
    if drilldown_sector:
        with tab1:
            show_market_heatmap(df, data_loader_module, 
                              preselected_sector=drilldown_sector,
                              preselected_exchange=drilldown_exchange)
        
        with tab2:
            show_sector_treemap(df, data_loader_module)
    else:
        with tab1:
            show_market_heatmap(df, data_loader_module)
        
        with tab2:
            show_sector_treemap(df, data_loader_module)
