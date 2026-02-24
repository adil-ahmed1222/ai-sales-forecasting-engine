"""Risk analysis utilities: volatility, drawdown, momentum, composite score."""
from typing import Dict, Any
import numpy as np
import pandas as pd


def volatility_percent(series: pd.Series, window: int = 12) -> float:
    s = series.dropna()
    if s.empty:
        return 0.0
    recent = s.iloc[-window:]
    mean = recent.mean()
    if mean == 0:
        return float('inf')
    vol = (recent.std(ddof=0) / mean) * 100.0
    return float(vol)


def peak_to_current_drawdown(series: pd.Series) -> float:
    s = series.dropna()
    if s.empty:
        return 0.0
    peak = float(s.max())
    current = float(s.iloc[-1])
    if peak == 0:
        return 0.0
    drawdown = ((peak - current) / peak) * 100.0
    return float(drawdown)


def momentum_score(series: pd.Series, months: int = 3) -> float:
    s = series.dropna()
    if len(s) < 2:
        return 0.0
    window = min(months, len(s) - 1)
    recent = s.iloc[-(window + 1):]
    # simple slope per month
    x = np.arange(len(recent))
    y = recent.values
    m, _ = np.linalg.lstsq(np.vstack([x, np.ones(len(x))]).T, y, rcond=None)[0]
    mean = recent.mean()
    if mean == 0:
        return 0.0
    pct_per_month = (m / mean) * 100.0
    return float(pct_per_month)


def composite_risk_score(series: pd.Series) -> float:
    """Compute composite risk score (0-100) using volatility, trend (slope), drawdown.

    We map components into 0-100 scales and combine with weights:
      volatility (40%), negative trend (30%), drawdown (30%)
    """
    vol = volatility_percent(series)
    draw = peak_to_current_drawdown(series)
    mom = momentum_score(series, months=6)

    # Trend contribution: penalize negative momentum; positive momentum reduces risk
    trend_pct = -min(mom, 0.0)  # only negative contributes (in percent)

    # Normalize contributors
    vol_norm = min(vol, 100.0)
    draw_norm = min(draw, 100.0)
    trend_norm = min(abs(trend_pct), 100.0)

    score = 0.4 * vol_norm + 0.3 * trend_norm + 0.3 * draw_norm
    return float(max(0.0, min(100.0, score)))


def classify_score(score: float) -> str:
    if score < 30.0:
        return 'Low'
    if score < 60.0:
        return 'Medium'
    return 'High'
