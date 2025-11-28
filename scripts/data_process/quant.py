"""Quantitative helpers for portfolio statistics."""

import datetime
from typing import Iterable, Optional, Sequence, Tuple

import pandas as pd

from data_process.fetchers import fetch_stock_data2


def calculate_metrics(data: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
    """Return mean return and volatility for the given price table."""
    returns = data.pct_change().dropna()
    mean_returns = returns.mean()
    volatility = returns.std()
    return mean_returns, volatility


def get_return_correlation_matrix(symbols: Optional[Iterable[str]] = None,
                                   lookback_days: int = 120) -> pd.DataFrame:
    """Compute the return correlation matrix for representative tickers."""
    if symbols is None:
        symbols = ('VCB', 'VIC', 'VNM', 'FPT', 'HPG', 'MWG')

    symbol_list: Sequence[str] = list(symbols)
    end = datetime.date.today()
    start = end - datetime.timedelta(days=max(lookback_days, 30))
    price_data, _ = fetch_stock_data2(
        list(symbol_list), start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"), verbose=False
    )

    if price_data.empty:
        return pd.DataFrame()

    returns = price_data.pct_change().dropna(how='all')
    return returns.corr().dropna(how='all', axis=0).dropna(how='all', axis=1)


__all__ = ['calculate_metrics', 'get_return_correlation_matrix']
