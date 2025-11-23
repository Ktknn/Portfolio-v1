"""Data fetching utilities for CSV files and market APIs."""

import warnings

warnings.filterwarnings('ignore', message='pkg_resources is deprecated')

from concurrent.futures import ThreadPoolExecutor, as_completed
import datetime
import os
from functools import lru_cache
from typing import Iterable, List, Optional, Tuple

import pandas as pd
from vnstock import Vnstock


def fetch_data_from_csv(file_path: str) -> pd.DataFrame:
    """Load a CSV file containing company metadata."""
    try:
        if os.path.exists(file_path):
            return pd.read_csv(file_path)
        print(f"File {file_path} không tồn tại. Vui lòng kiểm tra lại.")
        return pd.DataFrame()
    except Exception as exc:
        print(f"Lỗi khi đọc dữ liệu từ file CSV: {exc}")
        return pd.DataFrame()


def create_vnstock_instance():
    """Return a default Vnstock instance used across the app."""
    return Vnstock().stock(symbol='VN30F1M', source='VCI')


def _normalize_symbols(symbols: Iterable[str]) -> Tuple[List[str], List[str]]:
    """Return uppercase symbols without duplicates and list of discarded ones."""
    seen = set()
    unique: List[str] = []
    duplicates: List[str] = []
    for raw in symbols:
        ticker = (raw or "").strip().upper()
        if not ticker:
            continue
        if ticker in seen:
            duplicates.append(ticker)
            continue
        seen.add(ticker)
        unique.append(ticker)
    return unique, duplicates


@lru_cache(maxsize=128)
def _fetch_single_stock_cached(ticker: str, start_date: str, end_date: str) -> Tuple[pd.DataFrame, Optional[str]]:
    """Fetch a single ticker history and cache the response per date range."""
    try:
        stock = Vnstock().stock(symbol=ticker, source='VCI')
        stock_data = stock.quote.history(start=str(start_date), end=str(end_date))
    except Exception as exc:  # pragma: no cover - network/IO
        error_msg = str(exc)
        if "RetryError" in error_msg:
            error_msg = "Không thể kết nối đến server"
        elif "ValueError" in error_msg:
            error_msg = "Dữ liệu không hợp lệ"
        return pd.DataFrame(), error_msg

    if stock_data is None or stock_data.empty:
        return pd.DataFrame(), "Không có dữ liệu"

    stock_data = stock_data[['time', 'close']].copy()
    stock_data['time'] = pd.to_datetime(stock_data['time'])
    return stock_data.set_index('time'), None


def fetch_stock_data2(symbols: List[str], start_date: str, end_date: str,
                      verbose: bool = True) -> Tuple[pd.DataFrame, List[str]]:
    """Download historical prices for a list of tickers (deduped + cached)."""
    data = pd.DataFrame()
    skipped_tickers: List[str] = []

    unique_symbols, duplicates = _normalize_symbols(symbols)

    if duplicates and verbose:
        dedup_list = ", ".join(sorted(set(duplicates)))
        print(f"Bỏ qua mã trùng lặp: {dedup_list}")

    if not unique_symbols:
        if verbose:
            print("Danh sách cổ phiếu rỗng, không có dữ liệu để tải")
        return data, skipped_tickers

    def fetch_single_stock(ticker: str):
        cached_data, error = _fetch_single_stock_cached(ticker, start_date, end_date)
        if error:
            if verbose:
                print(f"Lỗi khi lấy dữ liệu {ticker}: {error}")
            return ticker, pd.DataFrame(), error
        # Copy to avoid mutating cached DataFrame when renaming columns
        result = cached_data.copy().rename(columns={'close': ticker})
        return ticker, result, None

    if verbose:
        print(f"Đang tải dữ liệu song song cho {len(unique_symbols)} cổ phiếu...")

    max_workers = min(8, max(1, len(unique_symbols)))
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_ticker = {
            executor.submit(fetch_single_stock, ticker): ticker for ticker in unique_symbols
        }

        for i, future in enumerate(as_completed(future_to_ticker), 1):
            ticker = future_to_ticker[future]
            if verbose:
                print(f"[{i}/{len(unique_symbols)}] Đang tải {ticker}...", end=" ")

            try:
                ticker_name, result, error = future.result()
            except Exception as exc:  # pragma: no cover
                error = str(exc)
                ticker_name = ticker
                result = pd.DataFrame()

            if not result.empty:
                if verbose:
                    print("✓ Thành công")
                if data.empty:
                    data = result
                else:
                    data = pd.merge(data, result, how='outer', on='time')
            else:
                if verbose:
                    print(f"✗ Bỏ qua ({error})")
                skipped_tickers.append(ticker_name)

    if not data.empty:
        data = data.interpolate(method='linear', limit_direction='both')
        if verbose:
            print(f"\n✓ Hoàn thành! Tải thành công {len(data.columns)}/{len(unique_symbols)} cổ phiếu")
    elif verbose:
        print(f"\n✗ Không thể tải dữ liệu cho bất kỳ cổ phiếu nào")

    return data, skipped_tickers


@lru_cache(maxsize=256)
def _fetch_latest_price_single(ticker: str, start_date: str, end_date: str) -> Tuple[Optional[float], Optional[str]]:
    """Return latest close price (in VND) for ticker and cache by date range."""
    try:
        stock = Vnstock().stock(symbol=ticker, source='VCI')
        stock_data = stock.quote.history(start=str(start_date), end=str(end_date))
    except Exception as exc:  # pragma: no cover - network/IO
        error_msg = str(exc)
        lowered = error_msg.lower()
        if "timeout" in lowered:
            error_msg = "Timeout khi kết nối API"
        elif "retryerror" in lowered:
            error_msg = "Không thể kết nối"
        elif "valueerror" in lowered:
            error_msg = "Dữ liệu không hợp lệ"
        return None, error_msg

    if stock_data is None or stock_data.empty:
        return None, "Không có dữ liệu"

    latest_price = float(stock_data['close'].iloc[-1]) * 1000
    return latest_price, None


def get_latest_prices(tickers: List[str]) -> dict:
    """Fetch the latest close price for each ticker using cached parallel calls."""
    latest_prices: dict = {}
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=7)

    unique_tickers, duplicates = _normalize_symbols(tickers)
    total_requested = len(tickers)

    if duplicates:
        dup_list = ", ".join(sorted(set(duplicates)))
        print(f"Bỏ qua mã trùng lặp khi lấy giá: {dup_list}")

    if not unique_tickers:
        print("Danh sách cổ phiếu rỗng, không có dữ liệu để lấy giá")
        return latest_prices

    print(f"\nĐang lấy giá mới nhất cho {len(unique_tickers)} cổ phiếu...")

    def worker(ticker: str) -> Tuple[str, Optional[float], Optional[str]]:
        price, error = _fetch_latest_price_single(ticker, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
        return ticker, price, error

    max_workers = min(4, max(1, len(unique_tickers)))
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(worker, ticker): ticker for ticker in unique_tickers}
        for i, future in enumerate(as_completed(futures), 1):
            ticker = futures[future]
            try:
                symbol, price, error = future.result()
            except Exception as exc:  # pragma: no cover
                price = None
                error = str(exc)
                symbol = ticker

            if price is not None:
                latest_prices[symbol] = price
                print(f"[{i}/{len(unique_tickers)}] {symbol}: {price:,.0f} VND ✓")
            else:
                print(f"[{i}/{len(unique_tickers)}] {symbol}: Lỗi - {error} ✗")

    print(f"✓ Hoàn thành! Lấy giá thành công cho {len(latest_prices)}/{len(unique_tickers)} cổ phiếu\n")
    if total_requested != len(unique_tickers):
        print(f"(Bao gồm {total_requested - len(unique_tickers)} mã trùng lặp đã bỏ qua)")
    return latest_prices


def fetch_ohlc_data(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Fetch OHLCV data for a single ticker."""
    try:
        stock = Vnstock().stock(symbol=ticker, source='VCI')
        stock_data = stock.quote.history(start=str(start_date), end=str(end_date))
        if stock_data is None or stock_data.empty:
            print(f"Không có dữ liệu OHLC cho {ticker}")
            return pd.DataFrame()

        required_columns = ['time', 'open', 'high', 'low', 'close', 'volume']
        available_columns = [col for col in required_columns if col in stock_data.columns]
        ohlc_data = stock_data[available_columns].copy()
        ohlc_data['time'] = pd.to_datetime(ohlc_data['time'])
        return ohlc_data
    except Exception as exc:  # pragma: no cover
        print(f"Lỗi khi lấy dữ liệu OHLC cho {ticker}: {exc}")
        return pd.DataFrame()


def _resolve_date_range(start_date: Optional[str], end_date: Optional[str],
                        months: int = 6) -> Tuple[str, str]:
    today = datetime.date.today()
    end = datetime.datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else today
    if start_date:
        start = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    else:
        start = end - datetime.timedelta(days=months * 30)
    if start > end:
        start = end - datetime.timedelta(days=months * 30)
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


@lru_cache(maxsize=16)
def get_index_history(symbol: str = "VNINDEX", start_date: Optional[str] = None,
                      end_date: Optional[str] = None, months: int = 6,
                      source: str = "VCI") -> pd.DataFrame:
    """Fetch historical quotes for a market index."""
    start, end = _resolve_date_range(start_date, end_date, months)
    try:
        stock = Vnstock().stock(symbol=symbol, source=source)
        history = stock.quote.history(start=start, end=end)
    except Exception as exc:  # pragma: no cover
        print(f"Lỗi khi lấy dữ liệu chỉ số {symbol}: {exc}")
        return pd.DataFrame(columns=["time", "close", "volume", "symbol"])

    if history is None or history.empty:
        return pd.DataFrame(columns=["time", "close", "volume", "symbol"])

    history = history.copy()
    history['time'] = pd.to_datetime(history['time'])
    history['symbol'] = symbol
    return history[['time', 'close', 'volume', 'symbol']]


def get_sector_snapshot(exchange: str = "HOSE,HNX,UPCOM", size: int = 400,
                        source: str = "TCBS", columns: Optional[List[str]] = None) -> pd.DataFrame:
    """Fetch the latest screener snapshot covering the entire market."""

    columns_key: Optional[Tuple[str, ...]] = tuple(columns) if columns else None
    return _get_sector_snapshot_cached(exchange, size, source, columns_key)


@lru_cache(maxsize=4)
def _get_sector_snapshot_cached(exchange: str, size: int, source: str,
                                 columns_key: Optional[Tuple[str, ...]]) -> pd.DataFrame:
    try:
        stock = Vnstock().stock(symbol='VNINDEX', source=source)
        params = {"exchangeName": exchange, "size": size}
        snapshot = stock.screener.stock(params=params)
    except Exception as exc:  # pragma: no cover
        print(f"Không thể tải dữ liệu screener: {exc}")
        return pd.DataFrame()

    if snapshot is None or snapshot.empty:
        return pd.DataFrame()

    if columns_key:
        mandatory = ["industry", "ticker"]
        ordered = mandatory + [col for col in columns_key if col not in mandatory]
        selected = [col for col in ordered if col in snapshot.columns]
        if selected:
            snapshot = snapshot[selected].copy()
        else:
            snapshot = snapshot.copy()
    else:
        snapshot = snapshot.copy()

    snapshot['industry'] = snapshot['industry'].fillna('Ngành khác')
    numeric_columns = [
        'market_cap', 'price_growth_1w', 'price_growth_1m', 'avg_trading_value_20d',
        'avg_trading_value_10d', 'avg_trading_value_5d', 'foreign_buysell_20s',
        'foreign_vol_pct', 'percent_price_vs_ma20', 'percent_price_vs_ma50',
        'percent_price_vs_ma100', 'percent_price_vs_ma200'
    ]
    for column in numeric_columns:
        if column in snapshot.columns:
            snapshot[column] = pd.to_numeric(snapshot[column], errors='coerce')
    return snapshot


def get_realtime_index_board(symbols: List[str]) -> pd.DataFrame:
    """Fetch real-time index board data using the price_board API."""
    if not symbols:
        return pd.DataFrame(columns=['symbol', 'gia_khop', 'thay_doi', 'ty_le_thay_doi'])

    try:
        stock = Vnstock().stock(symbol='VNINDEX', source='VCI')
        board = stock.trading.price_board(symbols)
    except Exception as exc:  # pragma: no cover - external service
        print(f"Không thể tải price_board: {exc}")
        return pd.DataFrame(columns=['symbol', 'gia_khop', 'thay_doi', 'ty_le_thay_doi'])

    if board is None or board.empty:
        return pd.DataFrame(columns=['symbol', 'gia_khop', 'thay_doi', 'ty_le_thay_doi'])

    board = board.copy()
    if isinstance(board.columns, pd.MultiIndex):
        board.columns = ['_'.join([str(level) for level in levels if level and str(level) != 'nan']).lower()
                         for levels in board.columns]

    rename_map = {
        'listing_symbol': 'symbol',
        'match_match_price': 'gia_khop',
        'match_reference_price': 'gia_tham_chieu'
    }
    board = board.rename(columns=rename_map)
    board = board.dropna(subset=['symbol'])
    for column in ['gia_khop', 'gia_tham_chieu']:
        if column in board.columns:
            board[column] = pd.to_numeric(board[column], errors='coerce')

    board['symbol'] = board['symbol'].astype(str).str.upper()

    board['thay_doi'] = board['gia_khop'] - board['gia_tham_chieu']
    board['ty_le_thay_doi'] = board.apply(
        lambda row: ((row['gia_khop'] - row['gia_tham_chieu']) / row['gia_tham_chieu'] * 100)
        if row['gia_tham_chieu'] not in (0, None) else 0,
        axis=1
    )
    board['last_updated'] = datetime.datetime.now()

    return board[['symbol', 'gia_khop', 'gia_tham_chieu', 'thay_doi', 'ty_le_thay_doi', 'last_updated']]


__all__ = [
    'fetch_data_from_csv', 'create_vnstock_instance', 'fetch_stock_data2',
    'get_latest_prices', 'fetch_ohlc_data', 'get_index_history', 'get_sector_snapshot',
    'get_realtime_index_board'
]
