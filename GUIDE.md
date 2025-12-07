# Developer Guide - Portfolio Optimization Dashboard

> **Mục đích**: Hướng dẫn developer hiểu cấu trúc project, đọc code, và sửa/mở rộng tính năng dễ dàng.

---

## 📑 Mục lục

1. [Kiến trúc tổng quan](#1-kiến-trúc-tổng-quan)
2. [Cấu trúc thư mục chi tiết](#2-cấu-trúc-thư-mục-chi-tiết)
3. [Luồng hoạt động chính](#3-luồng-hoạt-động-chính)
4. [Module Reference](#4-module-reference)
5. [Session State Management](#5-session-state-management)
6. [Hướng dẫn Debug](#6-hướng-dẫn-debug)
7. [Thêm tính năng mới](#7-thêm-tính-năng-mới)
8. [Best Practices](#8-best-practices)
9. [Troubleshooting](#9-troubleshooting)

---

## 1. Kiến trúc tổng quan

### 1.1. Pattern áp dụng

Project sử dụng **Modular Architecture** kết hợp với **Layered Pattern**:

```
┌─────────────────────────────────────────────┐
│         PRESENTATION LAYER                   │
│         (dashboard.py)                       │
│  - Routing tabs                              │
│  - User input handling                       │
│  - Display coordination                      │
└─────────────┬───────────────────────────────┘
              │
    ┌─────────┴─────────────┬──────────────────┐
    ▼                       ▼                  ▼
┌──────────┐         ┌──────────┐      ┌──────────┐
│UI LAYER  │         │DATA LAYER│      │BUSINESS  │
│(ui/)     │         │(data_    │      │LAYER     │
│          │         │ process/)│      │(portfolio│
│- Viz     │◄────────│          │─────►│_models)  │
│- Components│       │- Fetchers│      │          │
│- Market  │         │- Processors│    │- Optimization│
└──────────┘         │- Quant   │      │- Backtest│
                     └──────────┘      └──────────┘
                            │                │
                            ▼                ▼
                     ┌──────────────────────────┐
                     │    UTILITY LAYER         │
                     │  (utils/, chatbot/)      │
                     │                          │
                     │- Config                  │
                     │- Session Manager         │
                     │- Chatbot Service         │
                     └──────────────────────────┘
```

### 1.2. Core Concepts

**1. Single Entry Point**: `scripts/dashboard.py`
- Điểm khởi đầu duy nhất của app
- Xử lý routing giữa các tab
- Khởi tạo session state

**2. Separation of Concerns**
- **Data Layer**: Lấy & xử lý dữ liệu thô
- **Business Layer**: Logic tối ưu hóa & tính toán
- **UI Layer**: Hiển thị & visualization
- **Utils Layer**: Tiện ích dùng chung

**3. State Management**
- Centralized state trong `session_manager.py`
- Phân biệt rõ Manual mode vs Auto mode
- Persistence giữa các tab transitions

---

## 2. Cấu trúc thư mục chi tiết

```
Portfolio-Project/
│
├── 📄 README.md                    # User documentation
├── 📄 DEVELOPER_GUIDE.md          # File này - Dev documentation
├── 📄 requirements.txt             # Pip dependencies
├── 📄 pyproject.toml              # UV/modern Python project config
├── 📄 .python-version             # Python version lock (3.11)
│
├── 📁 data/                        # Static data files
│   └── company_info.csv           # Danh sách công ty, sàn, ngành
│
└── 📁 scripts/                     # Main source code
    │
    ├── 🎯 dashboard.py            # ★ ENTRY POINT - Start here
    │   ├─ Khởi tạo app
    │   ├─ Sidebar navigation
    │   ├─ Tab routing
    │   └─ Coordination layer
    │
    ├── 📊 portfolio_models.py     # ★ CORE LOGIC - Optimization models
    │   ├─ markowitz_optimization()
    │   ├─ max_sharpe()
    │   ├─ min_volatility()
    │   ├─ min_cvar()
    │   ├─ min_cdar()
    │   └─ hrp_model()
    │
    ├── 🔄 auto_optimization.py    # Batch run all models
    │   └─ run_all_models()
    │
    ├── 📈 optimization_comparison.py  # Results comparison tab
    │   └─ render_optimization_comparison_tab()
    │
    ├── 📰 news_tab.py             # News aggregation tab
    │   └─ render()
    │
    ├── 🔐 secret_config.py        # ⚠️ API keys (gitignored)
    │   └─ GEMINI_API_KEY
    │
    ├── 📁 data_process/           # ★ DATA LAYER
    │   │
    │   ├── data_loader.py         # Facade/compatibility layer
    │   │   └─ Re-exports all data functions
    │   │
    │   ├── fetchers.py            # Raw data fetching
    │   │   ├─ fetch_data_from_csv()      # Load company list
    │   │   ├─ fetch_stock_data2()        # Historical prices
    │   │   ├─ get_latest_prices()        # Realtime prices
    │   │   ├─ fetch_ohlc_data()          # OHLC candlestick data
    │   │   └─ get_realtime_index_board() # Market indices
    │   │
    │   ├── processors.py          # Data transformation
    │   │   ├─ get_indices_history()      # Index time series
    │   │   ├─ summarize_sector_performance()
    │   │   ├─ get_foreign_flow_leaderboard()
    │   │   └─ get_sector_heatmap_matrix()
    │   │
    │   ├── quant.py               # Quantitative calculations
    │   │   ├─ calculate_metrics()        # Return, Risk, Sharpe
    │   │   └─ get_return_correlation_matrix()
    │   │
    │   └── fundamentals.py        # Company fundamentals
    │       ├─ fetch_fundamental_data()
    │       └─ fetch_fundamental_data_batch()
    │
    ├── 📁 ui/                     # ★ PRESENTATION LAYER
    │   │
    │   ├── visualization.py       # Charts & plots
    │   │   ├─ plot_efficient_frontier()
    │   │   ├─ plot_candlestick_chart()
    │   │   ├─ backtest_portfolio()
    │   │   └─ display_results()
    │   │
    │   ├── ui_components.py       # Reusable UI components
    │   │   ├─ display_selected_stocks()
    │   │   └─ display_selected_stocks_2()
    │   │
    │   └── market_overview.py     # Market dashboard
    │       └─ render_bang_dieu_hanh()
    │
    ├── 📁 chatbot/                # ★ AI ASSISTANT
    │   │
    │   ├── chatbot_service.py     # Gemini API integration
    │   │   ├─ load_gemini_api_key()
    │   │   └─ generate_response()
    │   │
    │   ├── chatbot_ui.py          # Chat interface
    │   │   └─ render_chatbot_page()
    │   │
    │   └── market_data_adapter.py # Context provider for AI
    │       └─ get_market_context_for_chatbot()
    │
    └── 📁 utils/                  # ★ UTILITIES
        │
        ├── config.py              # Global configuration
        │   ├─ ANALYSIS_START_DATE
        │   ├─ ANALYSIS_END_DATE
        │   ├─ DEFAULT_INVESTMENT_AMOUNT
        │   └─ GEMINI_API_KEY
        │
        └── session_manager.py     # ★★★ STATE MANAGEMENT
            ├─ initialize_session_state()
            ├─ save_optimization_result()
            ├─ get_optimization_results()
            ├─ clear_optimization_results()
            ├─ update_current_tab()
            └─ get_current_tab()
```

### 2.1. Files Priority (đọc theo thứ tự này)

**Để hiểu project nhanh nhất:**

1. ✅ `scripts/dashboard.py` - Hiểu flow tổng thể
2. ✅ `scripts/utils/session_manager.py` - Hiểu state management
3. ✅ `scripts/portfolio_models.py` - Hiểu business logic
4. ✅ `scripts/data_process/fetchers.py` - Hiểu data source
5. ✅ `scripts/ui/visualization.py` - Hiểu cách hiển thị

---

## 3. Luồng hoạt động chính

### 3.1. Application Startup Flow

```python
# File: scripts/dashboard.py

1. Import dependencies
   └─ warnings.filterwarnings()  # Tắt warning vnai

2. st.set_page_config()
   └─ Configure page title, layout, sidebar

3. sys.path.append()
   └─ Thêm đường dẫn để import modules

4. Import all modules
   ├─ from utils.config import ...
   ├─ from data_process.data_loader import ...
   ├─ from scripts.portfolio_models import ...
   ├─ from ui.visualization import ...
   └─ from utils.session_manager import ...

5. fetch_data_from_csv(file_path)
   └─ Load danh sách công ty → df

6. initialize_session_state()
   └─ Setup all session variables

7. Render sidebar navigation
   └─ st.sidebar.radio() → selected_tab

8. Route to appropriate tab
   └─ if selected_tab == "...": render_tab()
```

### 3.2. Manual Stock Selection Flow

```
USER ACTION                    SYSTEM RESPONSE
─────────────────────────────────────────────────────────

1. Select Exchange (HOSE/HNX)
   └─> Filter df by exchange
                               
2. Select Industry
   └─> Filter df by industry
   └─> Display stock multiselect
                               
3. Select stocks
   └─> Save to st.session_state.selected_stocks
                               
4. Click "Lấy dữ liệu"
   └─> fetch_stock_data2(stocks, start, end)
       ├─ Call vnstock API
       ├─ Cache 24h
       └─ Return DataFrame (date × ticker)
   
   └─> calculate_metrics(data)
       ├─ Calculate returns
       ├─ Calculate risk
       └─ Calculate Sharpe
   
   └─> Display metrics table
   └─> Plot price chart

5. Click "🚀 Chạy Tất cả Mô hình"
   └─> clear_optimization_results('manual')
   
   └─> run_all_models(data, investment, 'manual')
       │
       ├─ Progress bar initialization
       │
       ├─ For each model:
       │   ├─ markowitz_optimization()
       │   ├─ max_sharpe()
       │   ├─ min_volatility()
       │   ├─ min_cvar()
       │   ├─ min_cdar()
       │   └─ hrp_model()
       │
       ├─ save_optimization_result(model_name, result, 'manual')
       │
       └─ Update progress bar
   
   └─> update_current_tab("Tổng hợp Kết quả")
   └─> st.rerun()

6. Auto-navigate to Comparison Tab
   └─> render_optimization_comparison_tab()
       └─ Display all results with charts
```

### 3.3. Auto Stock Recommendation Flow

```
1. User selects multiple exchanges + industries
   
2. User sets stocks_per_sector + filter criteria
   
3. System filters & ranks stocks
   ├─ Group by sector
   ├─ Calculate metrics per stock
   ├─ Sort by criteria (Return/Risk)
   └─ Take top N per sector

4. Display recommended stocks
   
5. User clicks "Thêm vào danh mục"
   └─> Save to st.session_state.selected_stocks_2

6. Continue same as Manual Flow from step 4
```

### 3.4. Single Model Optimization Flow

```python
# File: scripts/portfolio_models.py

def markowitz_optimization(data, total_investment, get_latest_prices_func):
    """
    STEP 1: Validate Input
    """
    if data.empty or len(data.columns) == 0:
        raise ValueError("Dữ liệu không hợp lệ")
    
    tickers = data.columns.tolist()
    
    """
    STEP 2: Calculate Expected Returns
    """
    mu = expected_returns.capm_return(
        prices=data,
        market_prices=None,
        risk_free_rate=0.02
    )
    
    """
    STEP 3: Calculate Covariance Matrix
    """
    S = risk_models.sample_cov(data)
    
    """
    STEP 4: Create Optimizer & Solve
    """
    ef = EfficientFrontier(mu, S)
    
    # Generate efficient frontier points
    frontier_volatility = []
    frontier_returns = []
    
    for target_return in np.linspace(mu.min(), mu.max(), 100):
        try:
            ef_temp = EfficientFrontier(mu, S)
            ef_temp.efficient_return(target_return)
            frontier_weights = ef_temp.clean_weights()
            
            perf = ef_temp.portfolio_performance()
            frontier_volatility.append(perf[1])
            frontier_returns.append(perf[0])
        except:
            continue
    
    # Find optimal point
    utility = [r - 2 * v for r, v in zip(frontier_returns, frontier_volatility)]
    optimal_idx = np.argmax(utility)
    optimal_return = frontier_returns[optimal_idx]
    
    # Get optimal weights
    ef.efficient_return(optimal_return)
    raw_weights = ef.clean_weights()
    
    """
    STEP 5: Clean Weights (remove < 1%)
    """
    cleaned_weights = {
        ticker: weight 
        for ticker, weight in raw_weights.items() 
        if weight >= 0.01
    }
    
    """
    STEP 6: Discrete Allocation (% → shares)
    """
    latest_prices_dict = get_latest_prices_func(list(cleaned_weights.keys()))
    latest_prices = _prepare_latest_price_series(
        list(cleaned_weights.keys()),
        latest_prices_dict,
        data
    )
    
    da = DiscreteAllocation(
        cleaned_weights,
        latest_prices,
        total_portfolio_value=total_investment
    )
    
    allocation, leftover = da.lp_portfolio()
    
    """
    STEP 7: Calculate Performance Metrics
    """
    expected_return, volatility, sharpe = ef.portfolio_performance(
        verbose=True,
        risk_free_rate=0.02
    )
    
    """
    STEP 8: Backtest
    """
    backtest_results = backtest_portfolio(
        cleaned_weights,
        data,
        total_investment
    )
    
    """
    STEP 9: Return Result Dictionary
    """
    return {
        'Trọng số danh mục': cleaned_weights,
        'Lợi nhuận kỳ vọng': expected_return,
        'Rủi ro (Độ lệch chuẩn)': volatility,
        'Sharpe Ratio': sharpe,
        'Phân bổ thực tế': allocation,
        'Số tiền đầu tư thực tế': sum(shares * latest_prices[ticker] 
                                      for ticker, shares in allocation.items()),
        'Tiền dư': leftover,
        'Backtest Results': backtest_results,
        'Efficient Frontier': {
            'volatility': frontier_volatility,
            'returns': frontier_returns,
            'optimal_idx': optimal_idx
        }
    }
```

---

## 4. Module Reference

### 4.1. Data Layer

#### `data_process/fetchers.py`

**Core Functions:**

```python
def fetch_data_from_csv(file_path: str) -> pd.DataFrame:
    """
    Load danh sách công ty từ CSV.
    
    Returns:
        DataFrame with columns: [Ticker, Exchange, ICB Name, ...]
    
    Used by: dashboard.py (startup)
    """

def fetch_stock_data2(symbols: List[str], 
                      start_date: str, 
                      end_date: str) -> pd.DataFrame:
    """
    Lấy dữ liệu giá lịch sử từ vnstock.
    
    Args:
        symbols: ['VNM', 'VCB', ...]
        start_date: '2023-01-01'
        end_date: '2024-12-31'
    
    Returns:
        DataFrame with:
        - Index: DatetimeIndex
        - Columns: symbols
        - Values: close prices
    
    Caching: 24 hours (@st.cache_data)
    
    Used by: dashboard.py (after user selects stocks)
    """

def get_latest_prices(symbols: List[str]) -> Dict[str, float]:
    """
    Lấy giá realtime mới nhất.
    
    Returns:
        {'VNM': 85000, 'VCB': 92000, ...}
    
    Used by: portfolio_models.py (for discrete allocation)
    """
```

#### `data_process/processors.py`

```python
def summarize_sector_performance(exchange: str = 'HOSE') -> pd.DataFrame:
    """
    Tính toán hiệu suất theo ngành.
    
    Returns:
        DataFrame with columns:
        - Sector
        - 1W Change (%)
        - 1M Change (%)
        - YTD Change (%)
    
    Used by: market_overview.py
    """
```

#### `data_process/quant.py`

```python
def calculate_metrics(data: pd.DataFrame) -> pd.DataFrame:
    """
    Tính toán metrics cho từng cổ phiếu.
    
    Input:
        date × ticker DataFrame
    
    Output:
        DataFrame with columns:
        - Ticker
        - Return (%)
        - Risk (%)
        - Sharpe Ratio
    
    Formula:
        Return = (price[-1] / price[0]) - 1
        Risk = std(daily_returns) * sqrt(252)
        Sharpe = (Return - 0.02) / Risk
    
    Used by: dashboard.py (after fetching data)
    """
```

### 4.2. Business Layer

#### `portfolio_models.py`

**Model Comparison:**

| Model | Objective | Best For | Pros | Cons |
|-------|-----------|----------|------|------|
| **Markowitz** | Max utility | Balanced investors | Classic, interpretable | May underperform in extreme markets |
| **Max Sharpe** | Max risk-adjusted return | Performance seekers | Best Sharpe ratio | Can be concentrated |
| **Min Volatility** | Min variance | Risk-averse | Most stable | Lower returns |
| **Min CVaR** | Min tail risk | Risk managers | Protects downside | Conservative |
| **Min CDaR** | Min drawdown | Long-term | Prevents big losses | May miss upside |
| **HRP** | Risk parity | Large portfolios | Diversified, robust | Complex |

**Common Pattern:**

```python
def [model_name](data, total_investment, get_latest_prices_func):
    # 1. Validate
    # 2. Calculate mu (expected returns)
    # 3. Calculate S (covariance)
    # 4. Create optimizer
    # 5. Solve optimization
    # 6. Clean weights
    # 7. Discrete allocation
    # 8. Backtest
    # 9. Return result dict
```

### 4.3. UI Layer

#### `ui/visualization.py`

```python
def display_results(model_name: str, result: dict):
    """
    Hiển thị kết quả tối ưu hóa.
    
    Displays:
    - Metrics (Return, Risk, Sharpe)
    - Weight allocation pie chart
    - Discrete allocation table
    - Investment summary
    
    Used by: dashboard.py (after optimization)
    """

def backtest_portfolio(weights: dict, 
                       data: pd.DataFrame, 
                       initial_investment: float) -> dict:
    """
    Backtest danh mục trên dữ liệu lịch sử.
    
    Returns:
        {
            'portfolio_value': time series,
            'cumulative_returns': time series,
            'max_drawdown': float,
            'final_return': float,
            'sharpe_ratio': float
        }
    
    Used by: All optimization models
    """
```

### 4.4. Utils Layer

#### `utils/session_manager.py`

**Session State Structure:**

```python
st.session_state = {
    # Navigation
    'current_tab': str,              # Tab hiện tại
    'previous_tab': str,             # Tab trước đó
    
    # Manual Mode (Tự chọn)
    'selected_stocks': List[str],    # ['VNM', 'VCB']
    'manual_investment_amount': float,
    'manual_filter_state': {
        'exchange': str,
        'icb_name': str,
        'start_date': str,
        'end_date': str
    },
    'manual_optimization_results': {
        'Mô hình Markowitz': result_dict,
        'Mô hình Max Sharpe': result_dict,
        ...
    },
    
    # Auto Mode (Đề xuất)
    'selected_stocks_2': List[str],
    'auto_investment_amount': float,
    'auto_filter_state': {...},
    'auto_optimization_results': {...},
}
```

**Key Functions:**

```python
def save_optimization_result(model_name: str, 
                             result: dict, 
                             mode: str = 'manual'):
    """
    Lưu kết quả tối ưu hóa vào session state.
    
    Args:
        model_name: 'Mô hình Markowitz'
        result: result dictionary from optimization
        mode: 'manual' or 'auto'
    
    Saves to:
        st.session_state.{mode}_optimization_results[model_name]
    """

def get_optimization_results(mode: str = 'manual') -> dict:
    """
    Lấy tất cả kết quả đã lưu.
    
    Returns:
        {'Mô hình 1': result_dict, 'Mô hình 2': result_dict, ...}
    """

def clear_optimization_results(mode: str = 'manual'):
    """
    Xóa tất cả kết quả cũ (trước khi chạy lại).
    """
```

---

## 5. Session State Management

### 5.1. Tại sao cần Session State?

**Problem:**
- Streamlit rerun toàn bộ script từ đầu mỗi khi user interaction
- Mất dữ liệu nếu không lưu vào st.session_state
- Switching tabs = rerun = mất state

**Solution:**
- Lưu tất cả state quan trọng vào `st.session_state`
- Centralized management trong `session_manager.py`
- Phân biệt rõ Manual vs Auto mode

### 5.2. State Lifecycle

```python
# 1. Initialization (app startup)
initialize_session_state()
# → Tạo tất cả keys với giá trị mặc định

# 2. User Interaction
# User selects stocks → Save
st.session_state.selected_stocks = ['VNM', 'VCB']

# 3. Optimization
# Run model → Save result
save_optimization_result('Mô hình Markowitz', result, 'manual')

# 4. Tab Switch
update_current_tab("Tổng hợp Kết quả")
st.rerun()

# 5. Display Results
results = get_optimization_results('manual')
# → Still available!
```

### 5.3. Accessing State

**❌ Bad Practice:**
```python
# Direct access - risky nếu key chưa tồn tại
value = st.session_state.some_key
```

**✅ Good Practice:**
```python
# Use getter function - safe với default value
value = st.session_state.get('some_key', default_value)

# Or check existence
if 'some_key' in st.session_state:
    value = st.session_state.some_key
```

---

## 6. Hướng dẫn Debug

### 6.1. Debug Session State

Thêm vào `dashboard.py` để xem toàn bộ state:

```python
# Add to sidebar
with st.sidebar.expander("🐛 Debug Info"):
    st.write("**Current Tab:**", get_current_tab())
    st.write("**Selected Stocks (Manual):**", st.session_state.selected_stocks)
    st.write("**Selected Stocks (Auto):**", st.session_state.selected_stocks_2)
    
    st.write("**Manual Results:**")
    st.json(list(st.session_state.manual_optimization_results.keys()))
    
    st.write("**Auto Results:**")
    st.json(list(st.session_state.auto_optimization_results.keys()))
    
    # Full state dump
    st.write("**Full Session State:**")
    st.json({k: str(v)[:100] for k, v in dict(st.session_state).items()})
```

### 6.2. Debug Data Flow

**Check data at each step:**

```python
# After fetching data
st.write("Data shape:", data.shape)
st.write("Columns:", data.columns.tolist())
st.write("Date range:", data.index.min(), "to", data.index.max())
st.write("Missing values:", data.isnull().sum().sum())
st.dataframe(data.head())

# After optimization
st.write("Weights:", result['Trọng số danh mục'])
st.write("Allocation:", result['Phân bổ thực tế'])
st.write("Leftover:", result['Tiền dư'])
```

### 6.3. Debug với Logging

```python
import logging

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Use in functions
logger.info(f"Fetching data for {len(symbols)} stocks")
logger.debug(f"Data shape: {data.shape}")
logger.error(f"Failed to optimize: {e}")
```

**View logs in terminal:**
```bash
uv run streamlit run scripts/dashboard.py
# Logs sẽ xuất hiện trong terminal
```

### 6.4. Common Issues & Fixes

**Issue 1: KeyError trong session_state**
```python
# ❌ Error
value = st.session_state.some_key

# ✅ Fix
value = st.session_state.get('some_key', default_value)
```

**Issue 2: Data shape mismatch**
```python
# ❌ Error: weights có 5 stocks, prices có 4 stocks
da = DiscreteAllocation(weights, prices, total_investment)

# ✅ Fix: Đảm bảo keys khớp
prices = {k: prices[k] for k in weights.keys() if k in prices}
```

**Issue 3: Empty data**
```python
# ✅ Always validate
if data.empty or len(data.columns) == 0:
    st.error("Không có dữ liệu")
    return
```

---

## 7. Thêm tính năng mới

### 7.1. Thêm Model Tối ưu hóa mới

**Step 1: Tạo function trong `portfolio_models.py`**

```python
def my_custom_model(data, total_investment, get_latest_prices_func):
    """
    Mô tả model của bạn.
    
    Args:
        data: DataFrame giá lịch sử
        total_investment: Số tiền đầu tư
        get_latest_prices_func: Function lấy giá realtime
    
    Returns:
        dict: Standard result format
    """
    # 1. Validate input
    if data.empty:
        raise ValueError("Data is empty")
    
    # 2. Tính toán của bạn
    mu = expected_returns.mean_historical_return(data)
    S = risk_models.sample_cov(data)
    
    # 3. Optimization logic
    # ... your custom logic ...
    
    # 4. Clean weights
    cleaned_weights = {k: v for k, v in raw_weights.items() if v >= 0.01}
    
    # 5. Discrete allocation
    latest_prices_dict = get_latest_prices_func(list(cleaned_weights.keys()))
    latest_prices = _prepare_latest_price_series(
        list(cleaned_weights.keys()),
        latest_prices_dict,
        data
    )
    da = DiscreteAllocation(cleaned_weights, latest_prices, total_investment)
    allocation, leftover = da.lp_portfolio()
    
    # 6. Performance metrics
    expected_return = sum(mu[k] * v for k, v in cleaned_weights.items())
    volatility = np.sqrt(
        sum(cleaned_weights[i] * cleaned_weights[j] * S.loc[i, j]
            for i in cleaned_weights for j in cleaned_weights)
    )
    sharpe = (expected_return - 0.02) / volatility
    
    # 7. Backtest
    backtest_results = backtest_portfolio(cleaned_weights, data, total_investment)
    
    # 8. Return standard format
    return {
        'Trọng số danh mục': cleaned_weights,
        'Lợi nhuận kỳ vọng': expected_return,
        'Rủi ro (Độ lệch chuẩn)': volatility,
        'Sharpe Ratio': sharpe,
        'Phân bổ thực tế': allocation,
        'Số tiền đầu tư thực tế': sum(
            shares * latest_prices[ticker] 
            for ticker, shares in allocation.items()
        ),
        'Tiền dư': leftover,
        'Backtest Results': backtest_results
    }
```

**Step 2: Thêm vào `dashboard.py`**

```python
# Import model mới
from scripts.portfolio_models import my_custom_model

# Thêm vào dictionary
models = {
    # ... existing models ...
    "Tên hiển thị của Model": {
        "function": lambda d, ti: my_custom_model(d, ti, get_latest_prices),
        "original_name": "Mô hình Custom"
    },
}
```

**Step 3: Thêm vào `auto_optimization.py`**

```python
def run_all_models(data, total_investment, get_latest_prices_func, mode='manual'):
    models = {
        # ... existing models ...
        "Mô hình Custom": lambda d, ti: my_custom_model(d, ti, get_latest_prices_func),
    }
    # ... rest of function
```

### 7.2. Thêm Data Source mới

**Step 1: Tạo fetcher trong `data_process/fetchers.py`**

```python
@st.cache_data(ttl=3600)  # Cache 1 hour
def fetch_from_new_source(symbols: List[str], 
                          start_date: str, 
                          end_date: str) -> pd.DataFrame:
    """
    Lấy dữ liệu từ nguồn mới (ví dụ: Yahoo Finance, Alpha Vantage).
    """
    import yfinance as yf  # Example
    
    data = yf.download(
        tickers=symbols,
        start=start_date,
        end=end_date,
        progress=False
    )['Close']
    
    return data
```

**Step 2: Export trong `data_process/data_loader.py`**

```python
from data_process.fetchers import fetch_from_new_source

__all__ = [
    # ... existing exports ...
    'fetch_from_new_source',
]
```

**Step 3: Use trong `dashboard.py`**

```python
from data_process.data_loader import fetch_from_new_source

# Option to switch data source
data_source = st.selectbox("Nguồn dữ liệu", ["vnstock", "Yahoo Finance"])

if data_source == "Yahoo Finance":
    data = fetch_from_new_source(selected_stocks, start_date, end_date)
else:
    data = fetch_stock_data2(selected_stocks, start_date, end_date)
```

### 7.3. Thêm Tab mới

**Step 1: Tạo file `scripts/my_new_tab.py`**

```python
import streamlit as st
import pandas as pd

def render_my_new_tab():
    """
    Render tab mới của bạn.
    """
    st.title("📊 Tab Mới")
    
    # Your tab content here
    st.write("Nội dung tab mới...")
    
    # Example: Display some data
    df = pd.DataFrame({
        'A': [1, 2, 3],
        'B': [4, 5, 6]
    })
    st.dataframe(df)
```

**Step 2: Import và add route trong `dashboard.py`**

```python
# Import
from scripts.my_new_tab import render_my_new_tab

# Add to sidebar options
tabs = [
    "Tổng quan Thị trường & Ngành",
    "Tự chọn mã cổ phiếu",
    "Hệ thống đề xuất mã cổ phiếu tự động",
    "Tổng hợp Kết quả Tối ưu hóa",
    "Tin tức Thị trường & Phân tích",
    "Trợ lý AI",
    "Tab Mới",  # ← Add here
]

selected_tab = st.sidebar.radio("🎯 Chọn chức năng", tabs)

# Add routing
if selected_tab == "Tab Mới":
    render_my_new_tab()
```

### 7.4. Thêm Visualization mới

**Step 1: Tạo function trong `ui/visualization.py`**

```python
import plotly.graph_objects as go

def plot_custom_chart(data: pd.DataFrame, title: str = "Custom Chart"):
    """
    Vẽ biểu đồ custom của bạn.
    """
    fig = go.Figure()
    
    # Add traces
    for col in data.columns:
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data[col],
            name=col,
            mode='lines'
        ))
    
    # Update layout
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Value",
        hovermode='x unified',
        template='plotly_white'
    )
    
    return fig
```

**Step 2: Use trong dashboard hoặc tab**

```python
from ui.visualization import plot_custom_chart

# Display chart
fig = plot_custom_chart(data, "My Custom Chart")
st.plotly_chart(fig, use_container_width=True)
```

---

## 8. Best Practices

### 8.1. Code Organization

**✅ DO:**
- Một function làm một việc rõ ràng
- Đặt tên function theo verb: `fetch_`, `calculate_`, `render_`
- Đặt tên variable có ý nghĩa: `total_investment` > `ti`
- Thêm docstring cho mọi public function
- Group related functions cùng file

**❌ DON'T:**
- Function quá dài (>100 lines) → split nhỏ
- Magic numbers → dùng constants
- Hardcode paths → dùng os.path.join()
- Ignore exceptions → proper error handling

### 8.2. Error Handling

**❌ Bad:**
```python
def fetch_data(symbols):
    data = api.get_data(symbols)
    return data
```

**✅ Good:**
```python
def fetch_data(symbols):
    try:
        if not symbols:
            raise ValueError("Symbols list is empty")
        
        data = api.get_data(symbols)
        
        if data.empty:
            st.warning("No data returned from API")
            return pd.DataFrame()
        
        return data
        
    except ValueError as e:
        st.error(f"Input error: {e}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Failed to fetch data: {e}")
        logger.error(f"Fetch error: {e}", exc_info=True)
        return pd.DataFrame()
```

### 8.3. Performance

**Caching Strategy:**
```python
# Cache data fetching (24h)
@st.cache_data(ttl=86400)
def fetch_stock_data2(symbols, start, end):
    ...

# Cache expensive calculations (1h)
@st.cache_data(ttl=3600)
def calculate_correlation_matrix(data):
    ...

# Don't cache time-sensitive data
def get_latest_prices(symbols):
    # No cache - need realtime
    ...
```

**Lazy Loading:**
```python
# ❌ Load everything upfront
all_data = fetch_all_stocks()  # Heavy!

# ✅ Load only what's needed
selected_data = fetch_stock_data2(selected_stocks, start, end)
```

### 8.4. Testing Tips

**Manual Testing Checklist:**

```python
# Test với edge cases:
✓ 1 stock only
✓ 20+ stocks
✓ Stock with missing data
✓ Very short time period (1 month)
✓ Very long time period (10 years)
✓ All stocks from same sector
✓ Investment amount = 1000 VND
✓ Investment amount = 1 billion VND

# Test flows:
✓ Manual → Run 1 model → Check result
✓ Manual → Run all models → Check comparison tab
✓ Auto → Generate recommendations → Add to portfolio
✓ Switch tabs → Check state preserved
✓ Refresh page → Check cache working
```

---

## 9. Troubleshooting

### 9.1. Common Errors

**Error: "ModuleNotFoundError: No module named 'scripts'"**

**Cause:** Python path không bao gồm project root

**Fix:**
```python
# Add to top of dashboard.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
```

---

**Error: "KeyError: 'Ticker'"**

**Cause:** CSV format không đúng hoặc thiếu cột

**Fix:**
```python
# Check CSV có đúng columns
required_columns = ['Ticker', 'Exchange', 'ICB Name']
if not all(col in df.columns for col in required_columns):
    raise ValueError(f"CSV must have columns: {required_columns}")
```

---

**Error: "No data returned from vnstock API"**

**Cause:** 
- Ticker không tồn tại
- API down
- Rate limit

**Fix:**
```python
# Add retry logic
import time

for attempt in range(3):
    try:
        data = stock.quote.history(...)
        if not data.empty:
            break
    except:
        if attempt < 2:
            time.sleep(2 ** attempt)  # Exponential backoff
        else:
            raise
```

---

**Error: "Optimization failed: Infeasible problem"**

**Cause:**
- Constraints quá strict
- Dữ liệu không đủ
- All negative returns

**Fix:**
```python
# Relax constraints hoặc fallback
try:
    ef.min_volatility()
except:
    # Fallback to equal weights
    weights = {ticker: 1/len(tickers) for ticker in tickers}
```

### 9.2. Performance Issues

**Issue: App chậm khi load nhiều stocks**

**Solutions:**
1. Giảm time range
2. Implement pagination
3. Load on-demand thay vì upfront
4. Increase cache TTL

```python
# Before
data = fetch_stock_data2(all_stocks, '2020-01-01', '2024-12-31')

# After
data = fetch_stock_data2(selected_stocks, '2023-01-01', '2024-12-31')
```

---

**Issue: Session state quá lớn**

**Solutions:**
1. Clear unused results
2. Store references thay vì full data
3. Compress data before storing

```python
# Clear old results before new run
clear_optimization_results(mode)

# Store only necessary fields
result_summary = {
    'weights': result['Trọng số danh mục'],
    'metrics': {
        'return': result['Lợi nhuận kỳ vọng'],
        'risk': result['Rủi ro (Độ lệch chuẩn)'],
        'sharpe': result['Sharpe Ratio']
    }
}
```

### 9.3. Debugging Workflow

```
1. Reproduce error
   └─ Note exact steps to trigger

2. Check terminal logs
   └─ Look for stack trace

3. Add debug prints
   └─ st.write() at key points

4. Check session state
   └─ Use debug expander

5. Isolate issue
   └─ Comment out sections to narrow down

6. Fix & test
   └─ Verify fix with edge cases

7. Add error handling
   └─ Prevent future occurrences
```

---

## 10. Useful Code Snippets

### 10.1. Quick Session State Inspector

```python
def show_debug_info():
    with st.expander("🔍 Debug Inspector"):
        tab1, tab2, tab3 = st.tabs(["Session State", "Data", "Metrics"])
        
        with tab1:
            st.json({k: str(v)[:100] for k, v in dict(st.session_state).items()})
        
        with tab2:
            if 'data' in locals():
                st.write(f"Shape: {data.shape}")
                st.dataframe(data.head())
        
        with tab3:
            st.write("Memory usage:")
            import sys
            st.write(f"Session size: {sys.getsizeof(st.session_state)} bytes")

# Use it
show_debug_info()
```

### 10.2. Timer Decorator

```python
import time
import functools

def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.2f}s")
        return result
    return wrapper

# Use it
@timer
def slow_function():
    time.sleep(2)
```

### 10.3. Safe Dictionary Get

```python
def safe_get(dictionary, keys, default=None):
    """
    Safely get nested dictionary value.
    
    Example:
        safe_get(result, ['Backtest Results', 'final_return'], 0.0)
    """
    value = dictionary
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default
    return value
```

---

## 11. Resources

### 11.1. Documentation Links

- **Streamlit**: https://docs.streamlit.io
- **PyPortfolioOpt**: https://pypi.org/project/PyPortfolioOpt/
- **vnstock**: https://vnstock.site
- **Plotly**: https://plotly.com/python/

### 11.2. Learning Path

**Để hiểu sâu về project:**

1. ✅ Đọc file này (DEVELOPER_GUIDE.md)
2. ✅ Chạy app và test tất cả flows
3. ✅ Đọc `dashboard.py` từ đầu đến cuối
4. ✅ Đọc `session_manager.py` để hiểu state
5. ✅ Pick 1 model trong `portfolio_models.py` và hiểu chi tiết
6. ✅ Thử thêm 1 feature nhỏ (ví dụ: new chart)
7. ✅ Đọc PyPortfolioOpt docs để hiểu optimization
8. ✅ Experiment với parameters khác nhau

---

## 12. Contact & Support

**Nếu bạn gặp vấn đề:**

1. Check [Troubleshooting](#9-troubleshooting) section
2. Search GitHub Issues
3. Create new issue với:
   - Steps to reproduce
   - Error message
   - Environment (Python version, OS)
   - Screenshots if applicable

---

**Happy Coding! 🚀**

*Last updated: December 7, 2025*
