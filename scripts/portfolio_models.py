"""
Module portfolio_models.py
Chứa các hàm tối ưu hóa danh mục đầu tư: Markowitz, Max Sharpe, Min Volatility, Min CVaR, Min CDaR, HRP.
"""

import numpy as np
import pandas as pd
import logging
from pypfopt import (
    EfficientFrontier, 
    risk_models, 
    expected_returns, 
    DiscreteAllocation,
    EfficientCVaR, 
    EfficientCDaR, 
    HRPOpt
)

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def run_integer_programming(weights, latest_prices, total_portfolio_value):
    """
    Sử dụng Integer Programming (LP) để tối ưu phân bổ mã cổ phiếu.
    
    Args:
    weights (dict): Trọng số của từng mã cổ phiếu
    latest_prices (pd.Series): Giá mã cổ phiếu mới nhất
        total_portfolio_value (float): Tổng giá trị danh mục đầu tư
        
    Returns:
        tuple: (allocation_lp, leftover_lp)
    """
    # Validation: Kiểm tra số tiền đầu tư
    if total_portfolio_value <= 0:
        logger.error(f"So tien dau tu phai lon hon 0. Nhan duoc: {total_portfolio_value:,.0f} VND")
        raise ValueError(f"So tien dau tu phai lon hon 0. Nhan duoc: {total_portfolio_value:,.0f} VND")
    
    logger.info("=" * 60)
    logger.info("BAT DAU PHAN BO DANH MUC DAU TU")
    logger.info(f"So tien dau tu: {total_portfolio_value:,.0f} VND")
    
    allocation = DiscreteAllocation(
        weights, 
        latest_prices, 
        total_portfolio_value=total_portfolio_value
    )
    allocation_lp, leftover_lp = allocation.lp_portfolio(
        reinvest=False, 
        verbose=True, 
        solver='ECOS_BB'
    )
    
    # Validation: Kiểm tra kết quả phân bổ
    total_spent = sum(allocation_lp[ticker] * latest_prices[ticker] for ticker in allocation_lp)
    total_check = total_spent + leftover_lp
    
    logger.info("-" * 60)
    logger.info("KET QUA PHAN BO:")
    logger.info(f"Tong tien da su dung: {total_spent:,.0f} VND")
    logger.info(f"So tien con lai: {leftover_lp:,.0f} VND")
    logger.info(f"Tong cong (kiem tra): {total_check:,.0f} VND")
    
    # Kiểm tra tổng tiền có khớp không
    if abs(total_check - total_portfolio_value) > 1:  # Cho phép sai số 1 VND
        logger.warning(f"Co su chenh lech: {abs(total_check - total_portfolio_value):,.0f} VND")
    else:
        logger.info("PHAN BO DANH MUC THANH CONG!")
    logger.info("=" * 60)
    
    return allocation_lp, leftover_lp


def markowitz_optimization(price_data, total_investment, get_latest_prices_func):
    """
    Mô hình Markowitz: Tối ưu hóa giữa lợi nhuận và rủi ro.
    
    Args:
    price_data (pd.DataFrame): Dữ liệu giá mã cổ phiếu
    total_investment (float): Tổng số tiền đầu tư
    get_latest_prices_func (function): Hàm lấy giá mã cổ phiếu mới nhất
        
    Returns:
        dict: Kết quả tối ưu hóa
    """
    logger.info(f"[MARKOWITZ] Nhan total_investment: {total_investment:,.0f} VND")
    
    tickers = price_data.columns.tolist()
    num_assets = len(tickers)

    if num_assets == 0:
        logger.error("Danh sach ma ma co phieu da chon khong hop le")
        print("Danh sách mã cổ phiếu đã chọn không hợp lệ. Vui lòng kiểm tra lại.")
        return None

    log_ret = np.log(price_data / price_data.shift(1)).dropna()
    n_portfolios = 10000
    all_weights = np.zeros((n_portfolios, num_assets))
    ret_arr = np.zeros(n_portfolios)
    vol_arr = np.zeros(n_portfolios)
    sharpe_arr = np.zeros(n_portfolios)

    mean_returns = log_ret.mean() * 252  # Lợi nhuận kỳ vọng hàng năm
    cov_matrix = log_ret.cov() * 252  # Ma trận hiệp phương sai hàng năm

    np.random.seed(42)  # Thiết lập giá trị seed để kết quả ổn định

    for i in range(n_portfolios):
        weights = np.random.random(num_assets)
        weights /= np.sum(weights)
        all_weights[i, :] = weights

        rf = 0.02
        ret_arr[i] = np.dot(mean_returns, weights)
        vol_arr[i] = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        sharpe_arr[i] = (ret_arr[i] - rf) / vol_arr[i]

    max_sharpe_idx = sharpe_arr.argmax()
    optimal_weights = all_weights[max_sharpe_idx]

    weight2 = dict(zip(tickers, optimal_weights))
    latest_prices = get_latest_prices_func(tickers)
    latest_prices_series = pd.Series(latest_prices)
    
    logger.info(f"[MARKOWITZ] Truoc khi gan total_portfolio_value: {total_investment:,.0f} VND")
    total_portfolio_value = total_investment
    logger.info(f"[MARKOWITZ] Sau khi gan total_portfolio_value: {total_portfolio_value:,.0f} VND")
    
    allocation_lp, leftover_lp = run_integer_programming(
        weight2, 
        latest_prices_series, 
        total_portfolio_value
    )

    result = {
        "Trọng số danh mục": dict(zip(tickers, optimal_weights)),
        "Lợi nhuận kỳ vọng": ret_arr[max_sharpe_idx],
        "Rủi ro (Độ lệch chuẩn)": vol_arr[max_sharpe_idx],
        "Tỷ lệ Sharpe": sharpe_arr[max_sharpe_idx],
        "Số mã cổ phiếu cần mua": allocation_lp,
        "Số tiền còn lại": leftover_lp,
        "Giá mã cổ phiếu": latest_prices,
        # Thêm dữ liệu cho biểu đồ
        "ret_arr": ret_arr,
        "vol_arr": vol_arr,
        "sharpe_arr": sharpe_arr,
        "all_weights": all_weights,
        "max_sharpe_idx": max_sharpe_idx
    }

    return result


def max_sharpe(data, total_investment, get_latest_prices_func):
    """
    Mô hình Max Sharpe Ratio: Tối đa hóa tỷ lệ Sharpe.
    
    Args:
        data (pd.DataFrame): Dữ liệu giá cổ phiếu
        total_investment (float): Tổng số tiền đầu tư
        get_latest_prices_func (function): Hàm lấy giá cổ phiếu mới nhất
        
    Returns:
        dict: Kết quả tối ưu hóa
    """
    logger.info(f"[MAX_SHARPE] Nhan total_investment: {total_investment:,.0f} VND")
    
    try:
        tickers = data.columns.tolist()
        num_assets = len(tickers)
        
        # Tính toán mean returns và covariance matrix
        mean_returns = expected_returns.mean_historical_return(data)
        cov_matrix = risk_models.sample_cov(data)

        # Tối ưu hóa Max Sharpe
        ef = EfficientFrontier(mean_returns, cov_matrix)
        weights = ef.max_sharpe()
        performance = ef.portfolio_performance(verbose=False)
        cleaned_weights = ef.clean_weights()

        # Tạo 10,000 danh mục ngẫu nhiên để vẽ scatter plot
        log_ret = np.log(data / data.shift(1)).dropna()
        n_portfolios = 10000
        all_weights = np.zeros((n_portfolios, num_assets))
        ret_arr = np.zeros(n_portfolios)
        vol_arr = np.zeros(n_portfolios)
        sharpe_arr = np.zeros(n_portfolios)

        mean_returns_annual = log_ret.mean() * 252
        cov_matrix_annual = log_ret.cov() * 252

        np.random.seed(42)
        rf = 0.04  # Risk-free rate 4%

        for i in range(n_portfolios):
            w = np.random.random(num_assets)
            w /= np.sum(w)
            all_weights[i, :] = w

            ret_arr[i] = np.dot(mean_returns_annual, w)
            vol_arr[i] = np.sqrt(np.dot(w.T, np.dot(cov_matrix_annual, w)))
            sharpe_arr[i] = (ret_arr[i] - rf) / vol_arr[i]

        latest_prices = get_latest_prices_func(tickers)
        latest_prices_series = pd.Series(latest_prices)
        total_portfolio_value = total_investment
        allocation_lp, leftover_lp = run_integer_programming(
            weights, 
            latest_prices_series, 
            total_portfolio_value
        )

        return {
            "Trọng số danh mục": cleaned_weights,
            "Lợi nhuận kỳ vọng": performance[0],
            "Rủi ro (Độ lệch chuẩn)": performance[1],
            "Tỷ lệ Sharpe": performance[2],
            "Số cổ phiếu cần mua": allocation_lp,
            "Số tiền còn lại": leftover_lp,
            "Giá cổ phiếu": latest_prices,
            # Thêm dữ liệu cho biểu đồ Max Sharpe
            "ret_arr": ret_arr,
            "vol_arr": vol_arr,
            "sharpe_arr": sharpe_arr,
            "all_weights": all_weights,
            "risk_free_rate": rf
        }
    except Exception as e:
        logger.error(f"Loi trong mo hinh Max Sharpe: {e}")
        print(f"Lỗi trong mô hình Max Sharpe: {e}")
        return None


def min_volatility(data, total_investment, get_latest_prices_func):
    """
    Mô hình Min Volatility: Tối thiểu hóa độ lệch chuẩn (rủi ro).
    
    Args:
        data (pd.DataFrame): Dữ liệu giá cổ phiếu
        total_investment (float): Tổng số tiền đầu tư
        get_latest_prices_func (function): Hàm lấy giá cổ phiếu mới nhất
        
    Returns:
        dict: Kết quả tối ưu hóa
    """
    logger.info(f"[MIN_VOLATILITY] Nhan total_investment: {total_investment:,.0f} VND")
    
    try:
        tickers = data.columns.tolist()
        num_assets = len(tickers)
        
        mean_returns = expected_returns.mean_historical_return(data)
        cov_matrix = risk_models.sample_cov(data)

        # Tối ưu hóa Min Volatility
        ef = EfficientFrontier(mean_returns, cov_matrix)
        weights = ef.min_volatility()
        performance = ef.portfolio_performance(verbose=False)
        cleaned_weights = ef.clean_weights()
        
        # Tối ưu hóa Max Sharpe để so sánh
        ef_sharpe = EfficientFrontier(mean_returns, cov_matrix)
        weights_sharpe = ef_sharpe.max_sharpe()
        performance_sharpe = ef_sharpe.portfolio_performance(verbose=False)
        cleaned_weights_sharpe = ef_sharpe.clean_weights()

        # Tạo 10,000 danh mục ngẫu nhiên để vẽ scatter plot
        log_ret = np.log(data / data.shift(1)).dropna()
        n_portfolios = 10000
        all_weights = np.zeros((n_portfolios, num_assets))
        ret_arr = np.zeros(n_portfolios)
        vol_arr = np.zeros(n_portfolios)
        sharpe_arr = np.zeros(n_portfolios)

        mean_returns_annual = log_ret.mean() * 252
        cov_matrix_annual = log_ret.cov() * 252

        np.random.seed(42)
        rf = 0.02  # Risk-free rate 2%

        for i in range(n_portfolios):
            w = np.random.random(num_assets)
            w /= np.sum(w)
            all_weights[i, :] = w

            ret_arr[i] = np.dot(mean_returns_annual, w)
            vol_arr[i] = np.sqrt(np.dot(w.T, np.dot(cov_matrix_annual, w)))
            sharpe_arr[i] = (ret_arr[i] - rf) / vol_arr[i]

        latest_prices = get_latest_prices_func(tickers)
        latest_prices_series = pd.Series(latest_prices)
        total_portfolio_value = total_investment
        allocation_lp, leftover_lp = run_integer_programming(
            weights, 
            latest_prices_series, 
            total_portfolio_value
        )

        return {
            "Trọng số danh mục": cleaned_weights,
            "Lợi nhuận kỳ vọng": performance[0],
            "Rủi ro (Độ lệch chuẩn)": performance[1],
            "Tỷ lệ Sharpe": performance[2],
            "Số cổ phiếu cần mua": allocation_lp,
            "Số tiền còn lại": leftover_lp,
            "Giá cổ phiếu": latest_prices,
            # Thêm dữ liệu cho biểu đồ Min Volatility
            "ret_arr": ret_arr,
            "vol_arr": vol_arr,
            "sharpe_arr": sharpe_arr,
            "all_weights": all_weights,
            "risk_free_rate": rf,
            # Thêm thông tin Max Sharpe để so sánh
            "max_sharpe_return": performance_sharpe[0],
            "max_sharpe_volatility": performance_sharpe[1],
            # Thêm trọng số thực sự của Min Volatility và Max Sharpe
            "min_vol_weights": cleaned_weights,
            "max_sharpe_weights": cleaned_weights_sharpe
        }
    except Exception as e:
        logger.error(f"Loi trong mo hinh Min Volatility: {e}")
        print(f"Lỗi trong mô hình Min Volatility: {e}")
        return None


def min_cvar(data, total_investment, get_latest_prices_func, beta=0.95):
    """
    Mô hình Min CVaR: Tối thiểu hóa Conditional Value at Risk.
    
    Args:
        data (pd.DataFrame): Dữ liệu giá cổ phiếu
        total_investment (float): Tổng số tiền đầu tư
        get_latest_prices_func (function): Hàm lấy giá cổ phiếu mới nhất
        beta (float): Mức độ tin cậy (mặc định 0.95)
        
    Returns:
        dict: Kết quả tối ưu hóa
    """
    logger.info(f"[MIN_CVAR] Nhan total_investment: {total_investment:,.0f} VND")
    
    try:
        mean_returns = expected_returns.mean_historical_return(data)
        returns = expected_returns.returns_from_prices(data).dropna()

        cvar_optimizer = EfficientCVaR(mean_returns, returns, beta=beta)
        weights = cvar_optimizer.min_cvar()
        performance = cvar_optimizer.portfolio_performance()
        
        # Tính ma trận hiệp phương sai
        cov_matrix = risk_models.sample_cov(data)

        # Tính độ lệch chuẩn của danh mục
        weights_array = np.array(list(weights.values()))
        portfolio_std = np.sqrt(np.dot(weights_array.T, np.dot(cov_matrix, weights_array)))
        rf = 0.02
        sharpe_ratio = (performance[0] - rf) / portfolio_std

        tickers = data.columns.tolist()
        latest_prices = get_latest_prices_func(tickers)
        latest_prices_series = pd.Series(latest_prices)
        total_portfolio_value = total_investment
        allocation_lp, leftover_lp = run_integer_programming(
            weights, 
            latest_prices_series, 
            total_portfolio_value
        )

        return {
            "Trọng số danh mục": weights,
            "Lợi nhuận kỳ vọng": performance[0],
            "Rủi ro CVaR": performance[1],
            "Số cổ phiếu cần mua": allocation_lp,
            "Số tiền còn lại": leftover_lp,
            "Giá cổ phiếu": latest_prices,
            "Rủi ro (Độ lệch chuẩn)": portfolio_std,
            "Tỷ lệ Sharpe": sharpe_ratio
        }
    except Exception as e:
        logger.error(f"Loi trong mo hinh Min CVaR: {e}")
        print(f"Lỗi trong mô hình Min CVaR: {e}")
        return None


def min_cdar(data, total_investment, get_latest_prices_func, beta=0.95):
    """
    Mô hình Min CDaR: Tối thiểu hóa Conditional Drawdown at Risk.
    
    Args:
        data (pd.DataFrame): Dữ liệu giá cổ phiếu
        total_investment (float): Tổng số tiền đầu tư
        get_latest_prices_func (function): Hàm lấy giá cổ phiếu mới nhất
        beta (float): Mức độ tin cậy (mặc định 0.95)
        
    Returns:
        dict: Kết quả tối ưu hóa
    """
    logger.info(f"[MIN_CDAR] Nhan total_investment: {total_investment:,.0f} VND")
    
    try:
        mean_returns = expected_returns.mean_historical_return(data)
        returns = expected_returns.returns_from_prices(data).dropna()

        cdar_optimizer = EfficientCDaR(mean_returns, returns, beta=beta)
        weights = cdar_optimizer.min_cdar()
        performance = cdar_optimizer.portfolio_performance()

        cov_matrix = risk_models.sample_cov(data)
        weights_array = np.array(list(weights.values()))
        portfolio_std = np.sqrt(np.dot(weights_array.T, np.dot(cov_matrix, weights_array)))
        rf = 0.02
        sharpe_ratio = (performance[0] - rf) / portfolio_std

        tickers = data.columns.tolist()
        latest_prices = get_latest_prices_func(tickers)
        latest_prices_series = pd.Series(latest_prices)
        total_portfolio_value = total_investment
        allocation_lp, leftover_lp = run_integer_programming(
            weights, 
            latest_prices_series, 
            total_portfolio_value
        )

        return {
            "Trọng số danh mục": weights,
            "Lợi nhuận kỳ vọng": performance[0],
            "Rủi ro CDaR": performance[1],
            "Số cổ phiếu cần mua": allocation_lp,
            "Số tiền còn lại": leftover_lp,
            "Giá cổ phiếu": latest_prices,
            "Rủi ro (Độ lệch chuẩn)": portfolio_std,
            "Tỷ lệ Sharpe": sharpe_ratio
        }
    except Exception as e:
        logger.error(f"Loi trong mo hinh Min CDaR: {e}")
        print(f"Lỗi trong mô hình Min CDaR: {e}")
        return None


def hrp_model(data, total_investment, get_latest_prices_func):
    """
    Mô hình HRP (Hierarchical Risk Parity): Phân bổ rủi ro phân cấp.
    
    Args:
        data (pd.DataFrame): Dữ liệu giá cổ phiếu
        total_investment (float): Tổng số tiền đầu tư
        get_latest_prices_func (function): Hàm lấy giá cổ phiếu mới nhất
        
    Returns:
        dict: Kết quả tối ưu hóa
    """
    logger.info(f"[HRP_MODEL] Nhan total_investment: {total_investment:,.0f} VND")
    
    try:
        returns = data.pct_change().dropna(how="all")
        hrp = HRPOpt(returns)
        weights = hrp.optimize(linkage_method="single")
        performance = hrp.portfolio_performance()

        tickers = data.columns.tolist()
        latest_prices = get_latest_prices_func(tickers)
        latest_prices_series = pd.Series(latest_prices)
        total_portfolio_value = total_investment
        allocation_lp, leftover_lp = run_integer_programming(
            weights, 
            latest_prices_series, 
            total_portfolio_value
        )

        return {
            "Trọng số danh mục": weights,
            "Lợi nhuận kỳ vọng": performance[0],
            "Rủi ro (Độ lệch chuẩn)": performance[1],
            "Tỷ lệ Sharpe": performance[2],
            "Số cổ phiếu cần mua": allocation_lp,
            "Số tiền còn lại": leftover_lp,
            "Giá cổ phiếu": latest_prices
        }
    except Exception as e:
        logger.error(f"Loi trong mo hinh HRP: {e}")
        print(f"Lỗi trong mô hình HRP: {e}")
        return None
