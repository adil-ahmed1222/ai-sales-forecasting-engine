"""High-level pipeline that composes modular preprocessing, forecasting,
risk analysis, insight generation and consistency validation."""
from typing import Dict, Any
try:
    # Support both package and script execution contexts
    from preprocessing import prepare_series
    from forecasting import ets_recursive_forecast
    from risk_analysis import (
        volatility_percent,
        peak_to_current_drawdown,
        momentum_score,
        composite_risk_score,
        classify_score,
    )
    from insights_engine import build_insight
    from consistency_validator import validate_and_adjust
except Exception:
    from .preprocessing import prepare_series
    from .forecasting import ets_recursive_forecast
    from .risk_analysis import (
        volatility_percent,
        peak_to_current_drawdown,
        momentum_score,
        composite_risk_score,
        classify_score,
    )
    from .insights_engine import build_insight
    from .consistency_validator import validate_and_adjust
    
import pandas as pd
import numpy as np


def enterprise_forecast_pipeline(df: pd.DataFrame, months: int = 3) -> Dict[str, Any]:
    """Run the full enterprise-grade pipeline and return structured KPIs.

    Returns a dict with:
      - predictions, lower, upper
      - volatility_percent, drawdown, momentum
      - composite_score, risk_label
      - stability_index, confidence intervals
      - insight and consistency_explanation (if any)
    """
    s = prepare_series(df)
    last_actual = float(s.iloc[-1])

    forecast_res = ets_recursive_forecast(s, steps=months)
    preds = forecast_res['predictions']
    lower = forecast_res['lower']
    upper = forecast_res['upper']

    vol = volatility_percent(s)
    draw = peak_to_current_drawdown(s)
    mom = momentum_score(s)
    comp = composite_risk_score(s)
    risk_label = classify_score(comp)

    # Trends
    recent_short = (s.iloc[-1] - s.iloc[-3]) / s.iloc[-3] if len(s) >= 3 and s.iloc[-3] != 0 else 0.0
    recent_long = (s.iloc[-1] - s.iloc[-6]) / s.iloc[-6] if len(s) >= 6 and s.iloc[-6] != 0 else recent_short

    # Stability index: inverted volatility scaled 0-100
    stability_index = float(max(0.0, min(100.0, 100.0 - vol)))

    payload = {
        'predictions': preds,
        'lower': lower,
        'upper': upper,
        'volatility_percent': float(round(vol, 3)),
        'drawdown_percent': float(round(draw, 3)),
        'momentum_pct_per_month': float(round(mom, 4)),
        'composite_score': float(round(comp, 2)),
        'risk_label': risk_label,
        'last_actual': last_actual,
        'recent_short_pct': float(recent_short),
        'recent_long_pct': float(recent_long),
        'stability_index': float(round(stability_index, 2)),
    }

    # Attach insight
    insight = build_insight(payload)
    payload['insight'] = insight

    # Consistency check
    payload = validate_and_adjust(payload)

    return payload


# Backwards compatible name used earlier
def forecast_pipeline(
    df: pd.DataFrame,
    months: int = 3,
    target_scaler=None,  # legacy parameter (not used in ETS pipeline)
    feature_scaler=None,  # legacy parameter (not used in ETS pipeline)
    **kwargs
) -> Dict[str, Any]:
    """Backward-compatible wrapper that ignores legacy scaling parameters."""
    return enterprise_forecast_pipeline(df, months=months)
