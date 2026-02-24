"""Preprocessing utilities for time-series revenue data."""
from typing import Tuple
import pandas as pd


def prepare_series(df: pd.DataFrame, date_col: str = 'date', value_col: str = 'revenue') -> pd.Series:
    """Validate and prepare monthly revenue series.

    - Ensures `date_col` and `value_col` exist
    - Parses dates, sorts, groups by month-end and sums revenue per month
    - Returns a pd.Series indexed by period index with float values
    """
    if date_col not in df.columns or value_col not in df.columns:
        raise ValueError(f"Input must contain '{date_col}' and '{value_col}' columns")

    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])

    # Normalize to month-end dates to ensure regular monthly series
    df['__month_end'] = df[date_col].dt.to_period('M').dt.to_timestamp('M')
    grouped = df.groupby('__month_end', as_index=True)[value_col].sum()
    series = grouped.sort_index()
    series.index.name = 'date'
    series = series.astype(float)
    return series
