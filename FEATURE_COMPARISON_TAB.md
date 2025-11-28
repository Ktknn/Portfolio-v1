# Tab Tổng hợp Kết quả Tối ưu hóa

## 📋 Tổng quan

Tab mới **"Tổng hợp Kết quả Tối ưu hóa"** được tạo ra để giúp người dùng so sánh và phân tích kết quả từ các mô hình tối ưu hóa danh mục đầu tư khác nhau, từ đó đưa ra quyết định đầu tư tốt nhất.

## ✨ Tính năng chính

### 1. **Bảng So sánh Tổng quan**
- So sánh các chỉ số quan trọng của tất cả mô hình:
  - Lợi nhuận kỳ vọng (%)
  - Rủi ro - Độ lệch chuẩn (%)
  - Tỷ lệ Sharpe
  - Tỷ lệ Return/Risk
  - Số lượng mã cổ phiếu
  - Vốn sử dụng và vốn còn lại
  - Tỷ lệ sử dụng vốn (%)
  - Chỉ số đa dạng hóa

- **Highlight tự động**: Các giá trị tốt nhất được tô màu xanh
- **Export CSV**: Tải xuống bảng so sánh để phân tích offline

### 2. **Biểu đồ Phân tích**
- **Biểu đồ Rủi ro - Lợi nhuận**: Scatter plot so sánh vị trí của các mô hình
- **Biểu đồ Tỷ lệ Sharpe**: Bar chart so sánh hiệu suất điều chỉnh theo rủi ro
- **Biểu đồ Đa dạng hóa**: So sánh mức độ phân tán đầu tư và số lượng mã CP
- **Biểu đồ Phân bổ Trọng số**: Pie charts hiển thị cấu trúc danh mục của từng mô hình

### 3. **Chi tiết Phân bổ**
- **Bảng So sánh Trọng số**: Xem tỷ trọng của từng mã cổ phiếu trong các mô hình
- **Bảng Số lượng Cổ phiếu**: Chi tiết số lượng cổ phiếu cần mua cho mỗi mã

### 4. **Khuyến nghị Đầu tư**
- **Xếp hạng Top 3**: Tự động xếp hạng các mô hình dựa trên điểm tổng hợp
- **Phân tích Điểm mạnh**: Chỉ ra ưu điểm của từng mô hình
- **Hướng dẫn Lựa chọn**: Gợi ý mô hình phù hợp với từng mục tiêu đầu tư

## 🎯 Các chỉ số đánh giá

### Chỉ số cơ bản
1. **Lợi nhuận kỳ vọng**: Lợi nhuận dự kiến hàng năm (%)
2. **Rủi ro (Std)**: Độ lệch chuẩn, đo lường biến động
3. **Tỷ lệ Sharpe**: Lợi nhuận trên mỗi đơn vị rủi ro (càng cao càng tốt)
4. **Return/Risk**: Tỷ lệ lợi nhuận/rủi ro trực tiếp

### Chỉ số nâng cao
5. **Chỉ số Đa dạng hóa** (0-1):
   - Tính bằng Herfindahl Index đảo ngược
   - Giá trị gần 1: Đa dạng hóa tốt
   - Giá trị gần 0: Tập trung vào ít mã CP

6. **Tỷ lệ Sử dụng Vốn**: 
   - Phần trăm vốn đã được đầu tư
   - Giúp đánh giá hiệu quả triển khai

7. **Số mã CP & Tổng số cổ phiếu**:
   - Đánh giá tính khả thi của danh mục
   - Xem xét chi phí giao dịch

## 🔄 Cách sử dụng

### Bước 1: Chạy các mô hình tối ưu hóa
1. Vào tab **"Tự chọn mã cổ phiếu"** hoặc **"Hệ thống đề xuất mã cổ phiếu tự động"**
2. Chọn danh sách cổ phiếu
3. Chạy các mô hình tối ưu hóa:
   - Markowitz
   - Max Sharpe
   - Min Volatility
   - Min CVaR
   - Min CDaR
   - HRP

### Bước 2: Xem kết quả tổng hợp
1. Chuyển sang tab **"Tổng hợp Kết quả Tối ưu hóa"**
2. Chọn chế độ hiển thị (Tự chọn hoặc Đề xuất tự động)
3. Xem các tab phân tích:
   - **Bảng So sánh Tổng quan**: Xem tổng quan nhanh
   - **Biểu đồ Phân tích**: Trực quan hóa so sánh
   - **Chi tiết Phân bổ**: Xem chi tiết cấu trúc danh mục
   - **Khuyến nghị Đầu tư**: Nhận gợi ý từ hệ thống

### Bước 3: Ra quyết định
- Dựa trên bảng xếp hạng và phân tích
- Cân nhắc mục tiêu đầu tư cá nhân:
  - **Mục tiêu tăng trưởng**: Chọn mô hình có Sharpe và Return cao
  - **Mục tiêu an toàn**: Chọn Min Volatility hoặc Min CVaR
  - **Cân bằng**: Chọn Markowitz hoặc Max Sharpe
  - **Đa dạng hóa**: Chọn HRP

## 💾 Quản lý dữ liệu

### Lưu trữ tự động
- Kết quả từ mỗi mô hình được tự động lưu vào session state
- Phân biệt giữa chế độ "Tự chọn" và "Đề xuất tự động"
- Hiển thị số lượng kết quả đã lưu trong sidebar

### Xóa dữ liệu
- Nút **"Xóa tất cả kết quả"** trong sidebar của tab Tổng hợp
- Xóa riêng biệt cho từng chế độ (Manual/Auto)

## 📊 Ví dụ phân tích

### Kịch bản 1: Nhà đầu tư ưu tiên lợi nhuận
```
Kết quả:
- Max Sharpe: Return 25%, Risk 18%, Sharpe 1.28 ⭐
- Markowitz: Return 23%, Risk 16%, Sharpe 1.31 
- Min Volatility: Return 15%, Risk 12%, Sharpe 1.08

→ Khuyến nghị: Max Sharpe (cân bằng tốt giữa return cao và sharpe)
```

### Kịch bản 2: Nhà đầu tư ưu tiên an toàn
```
Kết quả:
- Min Volatility: Return 15%, Risk 12%, Sharpe 1.08 ⭐
- Min CVaR: Return 16%, Risk 13%, Sharpe 1.07
- HRP: Return 18%, Risk 14%, Sharpe 1.12

→ Khuyến nghị: Min Volatility (rủi ro thấp nhất)
```

### Kịch bản 3: Nhà đầu tư cân bằng
```
Kết quả:
- Markowitz: Return 23%, Risk 16%, Sharpe 1.31 ⭐
- HRP: Return 20%, Risk 15%, Sharpe 1.20, Diversification 0.85
- Max Sharpe: Return 25%, Risk 18%, Sharpe 1.28

→ Khuyến nghị: Markowitz (Sharpe cao nhất, cân bằng tốt)
```

## 🛠️ Cấu trúc kỹ thuật

### Files mới
1. **`scripts/optimization_comparison.py`**: Module chính chứa tất cả logic so sánh
2. **`FEATURE_COMPARISON_TAB.md`**: Tài liệu hướng dẫn

### Files đã cập nhật
1. **`scripts/dashboard.py`**: 
   - Thêm tab mới vào menu
   - Lưu kết quả tối ưu hóa
   - Hiển thị số lượng kết quả trong sidebar

2. **`scripts/utils/session_manager.py`**:
   - Thêm `manual_optimization_results` và `auto_optimization_results`
   - Thêm các hàm `save_optimization_result()`, `get_optimization_results()`, `clear_optimization_results()`

### Các hàm chính

#### `calculate_portfolio_metrics(result)`
Tính toán các chỉ số đánh giá từ kết quả tối ưu hóa

#### `create_comparison_table(results_dict)`
Tạo bảng so sánh tổng quan

#### `highlight_best_values(df)`
Tô màu các giá trị tốt nhất trong bảng

#### `plot_risk_return_comparison(results_dict)`
Vẽ biểu đồ scatter rủi ro - lợi nhuận

#### `plot_sharpe_comparison(results_dict)`
Vẽ biểu đồ cột so sánh Sharpe ratio

#### `plot_allocation_comparison(results_dict)`
Vẽ pie charts so sánh phân bổ trọng số

#### `plot_diversification_comparison(results_dict)`
Vẽ biểu đồ so sánh đa dạng hóa

#### `provide_investment_recommendation(results_dict)`
Đưa ra khuyến nghị đầu tư tự động

#### `render_optimization_comparison_tab(results_dict)`
Hàm chính render toàn bộ tab

## 🎓 Công thức tính toán

### 1. Tỷ lệ Sharpe
```
Sharpe Ratio = (Return - Risk_Free_Rate) / Volatility
```

### 2. Return/Risk Ratio
```
Return/Risk = Expected_Return / Volatility
```

### 3. Chỉ số Đa dạng hóa (Normalized Herfindahl)
```
H = Σ(wi²)  # Herfindahl Index
Diversification Index = (1 - H) / (1 - 1/N)
```
Trong đó:
- `wi`: Trọng số của cổ phiếu i
- `N`: Số lượng cổ phiếu trong danh mục
- Giá trị = 1: Đa dạng hóa hoàn hảo (trọng số đều nhau)
- Giá trị = 0: Tập trung hoàn toàn (1 mã CP)

### 4. Tỷ lệ Sử dụng Vốn
```
Capital Utilization = (Total_Invested / Total_Capital) × 100%
```

### 5. Điểm Tổng hợp (cho xếp hạng)
```
Score = Sharpe_Ratio × 40 
      + Expected_Return × 30 
      + Diversification × 20 
      + Capital_Utilization × 10
```

## 🔍 Tips sử dụng hiệu quả

1. **So sánh ít nhất 3-4 mô hình** để có cái nhìn toàn diện
2. **Chú ý đến Sharpe Ratio** - đây là chỉ số quan trọng nhất
3. **Xem xét mục tiêu cá nhân** trước khi quyết định
4. **Kiểm tra tính khả thi**: Số lượng mã CP, vốn còn lại
5. **Kết hợp với Backtesting** để xác nhận hiệu suất lịch sử
6. **Export CSV** để lưu trữ và so sánh theo thời gian

## 🚀 Tính năng tương lai (Roadmap)

- [ ] Lưu kết quả vào database/file
- [ ] So sánh kết quả giữa các phiên khác nhau
- [ ] Thêm các chỉ số risk-adjusted khác (Sortino, Calmar, ...)
- [ ] Tích hợp Monte Carlo simulation
- [ ] Export báo cáo PDF
- [ ] Thêm biểu đồ so sánh Efficient Frontier
- [ ] Phân tích sensitivity của các mô hình

## 📞 Hỗ trợ

Nếu gặp vấn đề hoặc có đề xuất cải tiến, vui lòng:
1. Kiểm tra log trong console
2. Đảm bảo đã chạy ít nhất 1 mô hình tối ưu hóa
3. Thử xóa kết quả và chạy lại

---

**Phiên bản**: 1.0  
**Ngày tạo**: 28/11/2025  
**Tác giả**: GitHub Copilot
