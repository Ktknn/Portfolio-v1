## Portfolio – Dashboard tối ưu hóa danh mục cổ phiếu

Ứng dụng Streamlit hỗ trợ nhà đầu tư chứng khoán Việt Nam:

- Phân tích tổng quan thị trường & ngành (VNINDEX, VN30, HNX, UPCoM…)
- Lọc & chọn cổ phiếu theo sàn/ngành, tự chọn hoặc đề xuất tự động
- Chạy nhiều mô hình tối ưu hóa danh mục (Markowitz, Max Sharpe, Min Vol, Min CVaR, Min CDaR, HRP)
- Backtest hiệu quả danh mục trong khoảng thời gian phân tích
- So sánh kết quả giữa các mô hình và gợi ý phân bổ số lượng cổ phiếu thực tế
- Tích hợp tab tin tức & trợ lý AI (chatbot) hỗ trợ phân tích.

---

## 1. Yêu cầu hệ thống

- **Python 3.11+** (yêu cầu tối thiểu)
- **Hệ điều hành**: Windows / macOS / Linux
- **Kết nối Internet** (để lấy dữ liệu thị trường & tin tức)
- **Quản lý gói**: `pip` hoặc `uv` (khuyến nghị dùng `uv` cho tốc độ nhanh hơn)

---

## 2. Cài đặt

### 2.1. Clone dự án

```bash
git clone https://github.com/HieuPC1101/Portfolio-v1.git
cd Portfolio-v1
```

### 2.2. Cài đặt với pip (phương pháp truyền thống)

1. Tạo môi trường ảo (khuyến nghị):

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # macOS / Linux
```

2. Cài đặt thư viện:

```bash
pip install -r requirements.txt
```

### 2.3. Cài đặt với uv (khuyến nghị - nhanh hơn)

`uv` là trình quản lý gói Python hiện đại, cài đặt nhanh hơn pip:

```bash
# Cài đặt uv (nếu chưa có)
pip install uv

# Sync dependencies từ pyproject.toml
uv sync
```

### 2.4. Cấu hình API key (cho chatbot AI)

- Tạo file `scripts/secret_config.py` với nội dung:

```python
GEMINI_API_KEY = "your-google-generative-ai-key-here"
```

- Hoặc đặt biến môi trường `GEMINI_API_KEY`

---

## 3. Chạy ứng dụng

### 3.1. Chạy với pip

```bash
streamlit run scripts/dashboard.py
```

### 3.2. Chạy với uv (khuyến nghị)

```bash
uv run streamlit run scripts/dashboard.py
```

Ứng dụng sẽ tự động mở trong trình duyệt tại `http://localhost:8501`


## 4. Các tab chính trong ứng dụng

Thanh sidebar bên trái cho phép chuyển giữa các tab:

1. **Tổng quan Thị trường & Ngành**  
	- Bảng điều hành thị trường realtime: VN-Index, VN30, HNX, UPCoM…  
	- So sánh hiệu suất các chỉ số, hiệu suất ngành (1W, 1M)  
	- Treemap vốn hóa, dòng tiền khối ngoại, ma trận tương quan.

2. **Tự chọn mã cổ phiếu**  
	- Lọc theo **sàn giao dịch** và **ngành** từ file `data/company_info.csv`.  
	- Chọn thủ công các mã muốn đầu tư, chọn khoảng thời gian phân tích.  
	- Xem biểu đồ giá (line / candlestick) và chạy từng mô hình tối ưu hóa.  
	- **Mới**: Tự động chuyển sang tab "Tổng hợp Kết quả" sau khi chạy tất cả các mô hình.

3. **Hệ thống đề xuất mã cổ phiếu tự động**  
	- Chọn **nhiều sàn** và **nhiều ngành** cùng lúc.  
	- Chọn số lượng cổ phiếu mỗi ngành, tiêu chí lọc: *Lợi nhuận lớn nhất* hoặc *Rủi ro bé nhất*.  
	- Hệ thống đề xuất danh sách mã, sau đó bạn có thể thêm vào danh mục để tối ưu.  
	- **Mới**: Tự động chuyển sang tab so sánh sau khi hoàn thành tối ưu hóa.

4. **Tổng hợp Kết quả Tối ưu hóa** 
	- Hiển thị lại các kết quả đã chạy (theo 2 mode: *Tự chọn* / *Đề xuất tự động*).  
	- So sánh lợi nhuận kỳ vọng, rủi ro, Sharpe, phân bổ cổ phiếu giữa các mô hình.  
	- **Biểu đồ trực quan**: So sánh đồng thời nhiều mô hình trên các chỉ số.  
	- **Bảng xếp hạng**: Xếp hạng mô hình theo từng tiêu chí (Sharpe, Return, Risk, Backtest).  
	- **Phân tích chi tiết**: Xem chi tiết phân bổ vốn, số lượng cổ phiếu thực tế, kết quả backtest.

5. **Tin tức Thị trường & Phân tích**  
	- Tổng hợp tin tức tài chính/chứng khoán, phục vụ đọc nhanh và tham khảo.  
	- **Cải tiến**: Sửa lỗi hiển thị và cải thiện giao diện.

6. **Trợ lý AI**  
	- Chatbot hỗ trợ trả lời câu hỏi về thị trường, cổ phiếu, hoặc giải thích kết quả phân tích.  
	- Cần cấu hình API key trong `scripts/secret_config.py`.  
	- Sử dụng Google Gemini API để phân tích và tư vấn thông minh.

---

## 5. Các mô hình tối ưu hóa danh mục

Ứng dụng sử dụng thư viện `PyPortfolioOpt` và một số tối ưu hóa bổ sung:

- **Markowitz (Mean-Variance)** – Tối ưu hóa giữa lợi nhuận và rủi ro, tạo đường biên hiệu quả.  
- **Max Sharpe Ratio** – Tối đa hóa tỷ lệ Sharpe, so sánh với danh mục ngẫu nhiên.  
- **Min Volatility** – Giảm thiểu độ lệch chuẩn danh mục, so sánh với Max Sharpe.  
- **Min CVaR** – Tối thiểu hóa rủi ro tổn thất cực đoan (Conditional Value at Risk).  
- **Min CDaR** – Tối thiểu hóa rủi ro drawdown kéo dài (Conditional Drawdown at Risk).  
- **HRP (Hierarchical Risk Parity)** – Phân bổ rủi ro theo cấu trúc phân cấp, phù hợp danh mục nhiều mã.

Sau khi tối ưu, hệ thống còn:

- Chuyển trọng số lý thuyết thành **số lượng cổ phiếu nguyên** gần nhất phù hợp số tiền đầu tư.  
- Thực hiện **backtest** hiệu quả danh mục trong khoảng thời gian cấu hình (`ANALYSIS_START_DATE`, `ANALYSIS_END_DATE` trong `utils/config.py`).

---

## 6. Cấu trúc thư mục

```text
Portfolio-v1/
│  README.md
│  requirements.txt          # Dependencies cho pip
│  pyproject.toml           # Dependencies cho uv, cấu hình project
│  uv.lock                  # Lock file cho uv
│  .python-version          # Python version (3.11)
│  .gitignore
│
├─data/
│   └─ company_info.csv        # Thông tin mã, ngành, sàn giao dịch
│
├─scripts/
│   ├─ dashboard.py            # Entry chính của ứng dụng Streamlit
│   ├─ portfolio_models.py     # Các mô hình tối ưu hóa danh mục
│   ├─ auto_optimization.py    # Chạy tất cả mô hình & so sánh
│   ├─ optimization_comparison.py  # Tab tổng hợp & so sánh kết quả
│   ├─ news_tab.py             # Tab tin tức (đã cải tiến)
│   ├─ secret_config.py        # File cấu hình API key (không commit)
│   │
│   ├─ chatbot/                # Module chatbot & tích hợp AI
│   │   ├─ chatbot_service.py  # Logic xử lý Gemini API
│   │   ├─ chatbot_ui.py       # Giao diện chatbot
│   │   └─ market_data_adapter.py  # Adapter dữ liệu thị trường
│   │
│   ├─ data_process/           # Module xử lý & lấy dữ liệu
│   │   ├─ data_collect.py     # Thu thập dữ liệu từ API
│   │   ├─ data_loader.py      # Load và cache dữ liệu
│   │   ├─ fetchers.py         # Các hàm fetch chuyên biệt
│   │   ├─ fundamentals.py     # Dữ liệu cơ bản doanh nghiệp
│   │   ├─ processors.py       # Xử lý & transform dữ liệu
│   │   └─ quant.py            # Tính toán định lượng
│   │
│   ├─ ui/                     # Module giao diện
│   │   ├─ market_overview.py  # Bảng điều hành thị trường
│   │   ├─ ui_components.py    # Components UI tái sử dụng
│   │   └─ visualization.py    # Biểu đồ & visualization
│   │
│   └─ utils/                  # Tiện ích & cấu hình
│       ├─ config.py           # Cấu hình global (ngày phân tích, API...)
│       └─ session_manager.py  # Quản lý session state
```

### Cải tiến về cấu trúc code

- **Module hóa**: Code được tách thành các module chuyên biệt (chatbot, data_process, ui, utils)
- **Session Manager**: Quản lý trạng thái ứng dụng tập trung, tránh mất dữ liệu khi chuyển tab
- **Optimization Comparison**: Module riêng để so sánh và trực quan hóa kết quả các mô hình
- **Cấu hình tập trung**: File `utils/config.py` chứa tất cả cấu hình quan trọng

---

## 7. Công nghệ & Thư viện sử dụng

### Core Libraries
- **Streamlit** (1.52.1+): Framework web app
- **vnstock** (3.2.6): API dữ liệu chứng khoán Việt Nam
- **vnai** (2.1.9): Phân tích AI cho thị trường VN

### Data & Analysis
- **pandas** (2.3.3+): Xử lý dữ liệu
- **numpy** (2.3.5+): Tính toán số học
- **scipy** (1.16.3+): Tối ưu hóa khoa học
- **statsmodels** (0.14.6+): Thống kê & mô hình kinh tế

### Portfolio Optimization
- **PyPortfolioOpt** (1.5.6+): Thư viện tối ưu hóa danh mục

### Visualization
- **plotly** (5.24.1+): Biểu đồ tương tác

### AI & Integration
- **google-generativeai** (0.8.5+): Gemini API cho chatbot
- **feedparser** (6.0.12+): Đọc tin tức RSS

---

## 8. Kiến trúc & Luồng hoạt động của ứng dụng

### 8.1. Tổng quan kiến trúc

```
┌─────────────────────────────────────────────────────────┐
│                    STREAMLIT APP                        │
│                   (dashboard.py)                        │
└──────────────┬──────────────────────────┬───────────────┘
               │                          │
       ┌───────▼────────┐        ┌───────▼────────┐
       │   DATA LAYER   │        │   UI LAYER     │
       │  (data_process)│        │   (ui/)        │
       └───────┬────────┘        └───────┬────────┘
               │                          │
       ┌───────▼────────┐        ┌───────▼────────┐
       │  MODEL LAYER   │        │  UTILS LAYER   │
       │(portfolio_models)│      │(utils/,chatbot/)│
       └────────────────┘        └────────────────┘
```

### 8.2. Luồng hoạt động chính (Application Flow)

#### **Flow 1: Khởi động ứng dụng**

```python
1. Chạy dashboard.py
   ↓
2. initialize_session_state()  # Khởi tạo trạng thái
   ↓
3. fetch_data_from_csv()       # Load danh sách công ty
   ↓
4. Hiển thị sidebar + tabs
```

#### **Flow 2: Tự chọn mã cổ phiếu (Manual Mode)**

```
User chọn sàn/ngành → Chọn mã cổ phiếu
                    ↓
            fetch_stock_data2()  # Lấy dữ liệu giá lịch sử
                    ↓
            calculate_metrics()   # Tính toán Return/Risk
                    ↓
User click "Chạy Tất cả Mô hình"
                    ↓
            run_all_models()      # Chạy 6 mô hình
                    ↓
    ┌───────────────┴───────────────┐
    │   Các mô hình tối ưu hóa      │
    ├───────────────────────────────┤
    │ • markowitz_optimization()    │
    │ • max_sharpe()                │
    │ • min_volatility()            │
    │ • min_cvar()                  │
    │ • min_cdar()                  │
    │ • hrp_model()                 │
    └───────────────┬───────────────┘
                    ↓
    save_optimization_result()  # Lưu vào session state
                    ↓
    Tự động chuyển sang tab "Tổng hợp Kết quả"
                    ↓
    render_optimization_comparison_tab()  # Hiển thị so sánh
```

#### **Flow 3: Hệ thống đề xuất tự động (Auto Mode)**

```
User chọn nhiều sàn + nhiều ngành
                    ↓
Chọn tiêu chí lọc (Return/Risk) + Số lượng/ngành
                    ↓
            System lọc và xếp hạng
                    ↓
            Đề xuất danh sách cổ phiếu
                    ↓
User thêm vào danh mục → Tối ưu hóa (giống Flow 2)
```

### 8.3. Chi tiết các Module chính

#### **A. Module `data_process/` - Xử lý dữ liệu**

**File: `data_loader.py`** - Compatibility layer
- **Vai trò**: Tập hợp và export lại các function từ các module con
- **Pattern**: Facade pattern - đơn giản hóa interface

**File: `fetchers.py`** - Thu thập dữ liệu thô
```python
fetch_data_from_csv(file_path)
  └─> Đọc file company_info.csv → DataFrame

fetch_stock_data2(symbols, start_date, end_date)
  └─> Gọi vnstock API → Lấy giá lịch sử nhiều mã
  └─> Cache 24h để tăng tốc

get_latest_prices(symbols)
  └─> Lấy giá realtime từ vnstock → Dict {symbol: price}
```

**File: `processors.py`** - Xử lý và biến đổi dữ liệu
```python
get_indices_history(symbols, period)
  └─> Lấy lịch sử chỉ số VN-Index, VN30, HNX...
  
summarize_sector_performance(exchange)
  └─> Tính toán hiệu suất từng ngành
  └─> Return: DataFrame với metrics theo ngành

get_foreign_flow_leaderboard(exchange, top_n)
  └─> Xếp hạng dòng tiền nước ngoài
```

**File: `quant.py`** - Tính toán định lượng
```python
calculate_metrics(data)
  └─> Input: DataFrame giá lịch sử
  └─> Tính: Return (%), Risk (%), Sharpe Ratio
  └─> Output: DataFrame metrics cho từng mã

get_return_correlation_matrix(data)
  └─> Tính ma trận tương quan returns
  └─> Dùng cho phân tích đa dạng hóa
```

#### **B. Module `portfolio_models.py` - Các mô hình tối ưu hóa**

**Cấu trúc chung của mỗi mô hình:**

```python
def [model_name](data, total_investment, get_latest_prices_func):
    """
    Args:
        data: DataFrame giá lịch sử (date × tickers)
        total_investment: Số tiền đầu tư (VND)
        get_latest_prices_func: Function lấy giá hiện tại
    
    Returns:
        dict: {
            'Trọng số danh mục': {ticker: weight},
            'Lợi nhuận kỳ vọng': float,
            'Rủi ro (Độ lệch chuẩn)': float,
            'Sharpe Ratio': float,
            'Phân bổ thực tế': {ticker: shares},
            'Số tiền đầu tư thực tế': float,
            'Tiền dư': float,
            'Backtest Results': {...}
        }
    """
```

**1. Mô hình Markowitz (Mean-Variance Optimization)**
```python
markowitz_optimization(data, total_investment, get_latest_prices_func)
  │
  ├─> Tính expected returns (CAPM)
  ├─> Tính covariance matrix
  ├─> Tạo đường biên hiệu quả (efficient frontier)
  │   └─> Tìm điểm tối ưu: max(return - 2*risk)
  ├─> Chuyển trọng số → số lượng cổ phiếu
  └─> Backtest trên dữ liệu lịch sử
```

**2. Mô hình Max Sharpe Ratio**
```python
max_sharpe(data, total_investment, get_latest_prices_func)
  │
  ├─> Tối đa hóa: (Return - Risk_Free_Rate) / Risk
  ├─> Sử dụng PyPortfolioOpt.EfficientFrontier
  ├─> Generate danh mục ngẫu nhiên để so sánh
  └─> Visualize với Capital Allocation Line
```

**3. Mô hình Min Volatility**
```python
min_volatility(data, total_investment, get_latest_prices_func)
  │
  ├─> Tối thiểu hóa: Portfolio Variance
  ├─> Constraint: Sum(weights) = 1, weights ≥ 0
  └─> Phù hợp cho nhà đầu tư ưa an toàn
```

**4. Mô hình Min CVaR (Conditional Value at Risk)**
```python
min_cvar(data, total_investment, get_latest_prices_func)
  │
  ├─> Tính returns lịch sử
  ├─> Tối thiểu hóa: CVaR tại confidence level (95%)
  ├─> CVaR = E[Loss | Loss > VaR]
  └─> Phòng ngừa rủi ro đuôi (tail risk)
```

**5. Mô hình Min CDaR (Conditional Drawdown at Risk)**
```python
min_cdar(data, total_investment, get_latest_prices_func)
  │
  ├─> Tính drawdown series (sụt giảm từ đỉnh)
  ├─> Tối thiểu hóa: CDaR tại confidence level
  └─> Kiểm soát tổn thất kéo dài
```

**6. Mô hình HRP (Hierarchical Risk Parity)**
```python
hrp_model(data, total_investment, get_latest_prices_func)
  │
  ├─> Tính correlation matrix
  ├─> Hierarchical clustering (cây phả hệ)
  ├─> Phân bổ risk đều nhau theo cấp bậc
  ├─> Optimize allocation với scipy.optimize.milp
  └─> Robust với danh mục lớn
```

#### **C. Module `utils/` - Tiện ích**

**File: `session_manager.py`** - Quản lý trạng thái
```python
initialize_session_state()
  └─> Khởi tạo tất cả biến session state
  └─> Phân biệt: manual vs auto mode

save_optimization_result(model_name, result, mode)
  └─> Lưu kết quả vào st.session_state
  └─> Key: manual_optimization_results / auto_optimization_results

get_optimization_results(mode)
  └─> Lấy danh sách kết quả đã chạy

clear_optimization_results(mode)
  └─> Xóa kết quả cũ trước khi chạy lại
```

**File: `config.py`** - Cấu hình global
```python
ANALYSIS_START_DATE = today - 2 years
ANALYSIS_END_DATE = today
DEFAULT_INVESTMENT_AMOUNT = 1,000,000 VND
CACHE_EXPIRY_HOURS = 24
GEMINI_API_KEY = load_from_secret_config()
```

#### **D. Module `ui/` - Giao diện**

**File: `visualization.py`** - Vẽ biểu đồ
```python
plot_efficient_frontier(data, tickers)
  └─> Plotly scatter: Risk vs Return
  └─> Highlight điểm tối ưu

plot_candlestick_chart(data, ticker)
  └─> Plotly candlestick với volume

backtest_portfolio(weights, data, investment)
  └─> Tính portfolio value theo thời gian
  └─> Return: cumulative returns, drawdown, metrics
```

**File: `ui_components.py`** - Components tái sử dụng
```python
display_selected_stocks(selected_stocks)
  └─> Hiển thị danh sách mã đã chọn
  └─> Cho phép xóa từng mã
```

**File: `market_overview.py`** - Dashboard thị trường
```python
render_bang_dieu_hanh()
  └─> Realtime index board
  └─> Sector performance comparison
  └─> Treemap market cap
  └─> Foreign flow analysis
```

#### **E. Module `chatbot/` - Trợ lý AI**

**File: `chatbot_service.py`** - Logic Gemini API
```python
load_gemini_api_key()
  └─> Load từ secret_config.py hoặc env

generate_response(prompt, context)
  └─> Gọi Gemini API
  └─> Stream response để UX mượt
```

**File: `chatbot_ui.py`** - Giao diện chat
```python
render_chatbot_page()
  └─> Chat history
  └─> Input box
  └─> Display bot response với markdown
```

**File: `market_data_adapter.py`** - Cung cấp context
```python
get_market_context_for_chatbot()
  └─> Lấy dữ liệu thị trường realtime
  └─> Format thành prompt context cho AI
```

### 8.4. Flow chi tiết: Chạy 1 mô hình tối ưu hóa

```
1. User click button "Chiến lược XYZ"
   ↓
2. dashboard.py gọi models.strategy_function(data, investment)
   ↓
3. [Trong portfolio_models.py]
   ├─> Tính expected_returns (CAPM hoặc mean historical)
   ├─> Tính risk_models (covariance matrix)
   ├─> Tạo optimizer object (EfficientFrontier, EfficientCVaR...)
   ├─> Gọi optimizer.method() → raw_weights
   ├─> Clean weights (làm tròn, loại bỏ < 0.01%)
   │
4. Discrete Allocation (chuyển % → số cổ phiếu)
   ├─> get_latest_prices() → current_prices
   ├─> DiscreteAllocation(cleaned_weights, prices, investment)
   ├─> lp_portfolio() → {ticker: shares_count}
   │
5. Backtest
   ├─> backtest_portfolio(weights, historical_data, investment)
   ├─> Tính cumulative returns, max drawdown, Sharpe...
   │
6. Return result dict
   ↓
7. [Quay lại dashboard.py]
   ├─> save_optimization_result(model_name, result, mode)
   ├─> display_results(model_name, result)
   └─> Vẽ biểu đồ tương ứng
```

### 8.5. Session State Management (Quản lý trạng thái)

**Cấu trúc Session State:**

```python
st.session_state = {
    # Tab navigation
    'current_tab': str,
    'previous_tab': str,
    
    # Manual mode
    'selected_stocks': List[str],
    'manual_filter_state': dict,
    'manual_optimization_results': {
        'Mô hình Markowitz': result_dict,
        'Mô hình Max Sharpe': result_dict,
        ...
    },
    'manual_investment_amount': float,
    
    # Auto mode
    'selected_stocks_2': List[str],
    'auto_filter_state': dict,
    'auto_optimization_results': {...},
    'auto_investment_amount': float,
    
    # Other states...
}
```

**Các hàm quan trọng:**

```python
# Lưu kết quả
save_optimization_result(model_name, result, mode='manual')
  └─> st.session_state[f'{mode}_optimization_results'][model_name] = result

# Lấy kết quả
get_optimization_results(mode='manual')
  └─> return st.session_state[f'{mode}_optimization_results']

# Xóa kết quả (trước khi chạy lại)
clear_optimization_results(mode='manual')
  └─> st.session_state[f'{mode}_optimization_results'] = {}
```

### 8.6. Optimization Comparison (So sánh các mô hình)

**File: `optimization_comparison.py`**

```python
render_optimization_comparison_tab()
  │
  ├─> Xác định mode (manual/auto) dựa trên previous_tab
  ├─> Lấy results = get_optimization_results(mode)
  │
  ├─> Nếu có results:
  │   ├─> Tab 1: Tổng quan
  │   │   ├─> Metrics comparison table
  │   │   └─> Radar chart (Return, Risk, Sharpe...)
  │   │
  │   ├─> Tab 2: So sánh chi tiết
  │   │   ├─> Bar charts: Return, Risk, Sharpe
  │   │   ├─> Scatter plot: Risk-Return tradeoff
  │   │   └─> Backtest comparison
  │   │
  │   ├─> Tab 3: Bảng xếp hạng
  │   │   ├─> Xếp hạng theo từng tiêu chí
  │   │   ├─> Highlight mô hình tốt nhất
  │   │   └─> Gợi ý cho nhà đầu tư
  │   │
  │   └─> Tab 4: Phân tích từng mô hình
  │       ├─> Expander cho mỗi mô hình
  │       ├─> Chi tiết phân bổ (weights, shares)
  │       ├─> Pie chart allocation
  │       └─> Backtest results
  │
  └─> Else: Hiển thị hướng dẫn chạy mô hình
```

---
