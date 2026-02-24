"""Utilities for CSV reading and feature engineering."""
from typing import Tuple
import pandas as pd


def read_sales_csv(file_path: str) -> pd.DataFrame:
    """Read CSV with at least columns ['date','revenue'] and parse dates."""
    df = pd.read_csv(file_path)
    if 'date' not in df.columns or 'revenue' not in df.columns:
        raise ValueError("CSV must contain 'date' and 'revenue' columns")
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)
    return df


def create_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add month, year and simple lag/rolling features.

    Expects df with 'date' and 'revenue'
    """
    df = df.copy()
    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year
    # Use lag-1, lag-2, lag-3 and lag-6 for consistency with forecasting spec
    df['lag_1'] = df['revenue'].shift(1)
    df['lag_2'] = df['revenue'].shift(2)
    df['lag_3'] = df['revenue'].shift(3)
    df['lag_6'] = df['revenue'].shift(6)
    # rolling mean of the previous 3 values (shifted so it does not include current row)
    df['rolling_mean_3'] = df['revenue'].rolling(3, min_periods=1).mean().shift(1)
    df = df.dropna().reset_index(drop=True)
    return df
