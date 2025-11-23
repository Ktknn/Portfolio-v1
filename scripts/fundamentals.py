"""Helpers dedicated to fetching fundamental (financial) data for tickers."""

from typing import Dict, List, Optional

import pandas as pd
from vnstock import Vnstock


def fetch_fundamental_data(symbol: str) -> Optional[Dict[str, float]]:
    """Fetch yearly financial ratios for a single ticker."""
    try:
        stock = Vnstock().stock(symbol=symbol, source='VCI')
        financial_ratio = stock.finance.ratio(period='year', lang='vi')
        if financial_ratio is None or financial_ratio.empty:
            print(f"Không có dữ liệu phân tích cơ bản cho {symbol}")
            return None

        latest_data = financial_ratio.iloc[0] if not financial_ratio.empty else None
        if latest_data is None:
            return None

        return {
            'symbol': symbol,
            'pe': latest_data.get('priceToEarning'),
            'pb': latest_data.get('priceToBook'),
            'eps': latest_data.get('earningPerShare'),
            'roe': latest_data.get('roe'),
            'roa': latest_data.get('roa'),
            'profit_margin': latest_data.get('netProfitMargin'),
            'revenue': latest_data.get('revenue'),
            'profit': latest_data.get('postTaxProfit'),
        }
    except Exception as exc:  # pragma: no cover - network/IO
        print(f"Lỗi khi lấy dữ liệu phân tích cơ bản cho {symbol}: {exc}")
        return None


def fetch_fundamental_data_batch(symbols: List[str]) -> pd.DataFrame:
    """Batch fetch fundamental data for multiple tickers."""
    fundamental_list = []
    print(f"\nĐang lấy dữ liệu phân tích cơ bản cho {len(symbols)} mã cổ phiếu...")
    for i, symbol in enumerate(symbols, 1):
        print(f"[{i}/{len(symbols)}] Đang xử lý {symbol}...", end=" ")
        data = fetch_fundamental_data(symbol)
        if data:
            fundamental_list.append(data)
            print("✓ Thành công")
        else:
            print("✗ Không có dữ liệu")

    if fundamental_list:
        df = pd.DataFrame(fundamental_list)
        print(f"\n✓ Hoàn thành! Lấy dữ liệu thành công cho {len(df)}/{len(symbols)} mã cổ phiếu")
        return df

    print(f"\n✗ Không thể lấy dữ liệu phân tích cơ bản cho bất kỳ mã cổ phiếu nào")
    return pd.DataFrame()


__all__ = ['fetch_fundamental_data', 'fetch_fundamental_data_batch']
