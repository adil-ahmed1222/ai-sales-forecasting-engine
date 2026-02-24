"""Forecasting module using ETS (Exponential Smoothing) with safety constraints.

Provides deterministic recursive forecasting, confidence intervals (approx),
and gentle constraints to avoid unrealistic rebounds after sustained decline.
"""
from typing import List, Tuple, Dict, Any
import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing


def _residual_std(fitted_values: np.ndarray, actual: np.ndarray) -> float:
    res = actual - fitted_values
    return float(np.std(res, ddof=0))


def ets_recursive_forecast(
    series: pd.Series,
    steps: int = 3,
    seasonal_periods: int = 12,
    use_seasonal: bool = True,
    max_growth_multiplier: float = 3.0,
) -> Dict[str, Any]:
    """Fit ETS model and produce recursive forecasts with bounds.

    Returns:
      - predictions: list of floats (exact revenue magnitudes)
      - lower: list
      - upper: list
      - fitted: fitted series (for residuals)
    """
    if series.empty:
        raise ValueError('Empty series provided')

    s = series.astype(float)

    seasonal = 'add' if use_seasonal and len(s) >= 2 * seasonal_periods else None

    if len(s.dropna()) < 3:
        # Not enough data -> repeat last observed value
        last = float(s.iloc[-1])
        return {
            'predictions': [last] * steps,
            'lower': [last] * steps,
            'upper': [last] * steps,
            'fitted': s,
        }

    model = ExponentialSmoothing(
        s,
        trend='add',
        seasonal=seasonal,
        seasonal_periods=seasonal_periods if seasonal is not None else None,
        initialization_method='estimated',
    )
    fitted = model.fit(optimized=True)
    preds_raw = fitted.forecast(steps=steps)

    # Approximate confidence interval using residual std
    resid_std = _residual_std(fitted.fittedvalues.values, s.values)
    z = 1.96
    lower = preds_raw - z * resid_std
    upper = preds_raw + z * resid_std

    preds = [float(x) for x in preds_raw]
    lower = [float(x) if not np.isnan(x) else float(preds[i]) for i, x in enumerate(lower)]
    upper = [float(x) if not np.isnan(x) else float(preds[i]) for i, x in enumerate(upper)]

    # Safety constraint: avoid unrealistic rebound. Constrain monthly change
    # relative to recent average pct change.
    if len(s) >= 3:
        recent = s.iloc[-3:]
        pct = recent.pct_change().dropna()
        recent_pct = float(pct.mean()) if not pct.empty else 0.0
    else:
        recent_pct = 0.0

    adjusted = []
    adjusted_lower = []
    adjusted_upper = []
    prev = float(s.iloc[-1])
    floor = 0.01
    for i, p in enumerate(preds):
        allowed = max(abs(recent_pct) * max_growth_multiplier, floor)
        max_up = prev * (1 + allowed)
        min_down = prev * (1 - allowed * max_growth_multiplier)
        if recent_pct < 0 and p > prev:
            p_adj = min(p, max_up)
        else:
            p_adj = max(min(p, max_up), min_down)
        adjusted.append(float(p_adj))
        # Adjust bounds consistently
        l = lower[i]
        u = upper[i]
        adjusted_lower.append(float(max(min_down, l)))
        adjusted_upper.append(float(min(max_up, u)))
        prev = p_adj

    return {
        'predictions': adjusted,
        'lower': adjusted_lower,
        'upper': adjusted_upper,
        'fitted': fitted.fittedvalues,
    }
