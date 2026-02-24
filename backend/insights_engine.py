"""Insights engine to produce executive-level narratives based on signals."""
from typing import Dict, Any


def build_insight(payload: Dict[str, Any]) -> str:
    """Construct a structured executive insight.

    Payload expected keys:
      - predictions (list)
      - volatility_percent
      - composite_score
      - risk_label
      - recent_short_pct
      - recent_long_pct
      - drawdown
      - stability_index
    """
    preds = payload.get('predictions', [])
    last_actual = payload.get('last_actual', None)
    volatility = payload.get('volatility_percent', None)
    score = payload.get('composite_score', None)
    risk = payload.get('risk_label', None)
    recent_short = payload.get('recent_short_pct', None)
    recent_long = payload.get('recent_long_pct', None)
    # support both keys 'drawdown' and 'drawdown_percent'
    drawdown = payload.get('drawdown', None)
    if drawdown is None:
        drawdown = payload.get('drawdown_percent', None)
    stability = payload.get('stability_index', None)

    # Forecast numbers
    if preds:
        next_vals = ', '.join([f'{p:.2f}' for p in preds[:3]])
        avg_forecast = sum(preds) / len(preds)
    else:
        next_vals = 'N/A'
        avg_forecast = None

    parts = []
    
    # Trend Summary with investor-ready language
    if recent_short is not None and recent_long is not None and avg_forecast is not None:
        forecast_pct = ((avg_forecast - last_actual) / last_actual * 100) if last_actual and last_actual != 0 else 0.0
        trend_summary = f"Revenue Trend: "
        if recent_short < -0.15:  # Significant decline
            trend_summary += f"📉 downward trend expected with {forecast_pct:.1f}% change next month."
        elif recent_short > 0.10:  # Strong growth
            trend_summary += f"📈 upward trajectory with {forecast_pct:+.1f}% projected next month."
        else:
            trend_summary += f"➡️ modest movement of {forecast_pct:+.1f}% anticipated next month."
        parts.append(trend_summary)
    else:
        parts.append('Revenue Trend: Insufficient data for detailed analysis.')

    # Risk Assessment with investor-ready context
    if risk is not None:
        risk_assess = f"Risk Assessment: Business classified as {risk} Risk"
        if score is not None:
            risk_assess += f" (Composite Score: {score:.1f}/100)"
        risk_assess += "."
        if volatility is not None and drawdown is not None:
            risk_assess += f" Volatility: {volatility:.1f}%, Drawdown from Peak: {drawdown:.1f}%."
        parts.append(risk_assess)
    else:
        parts.append("Risk Assessment: Insufficient data.")

    # Investor-ready Strategic Recommendation (context-specific, not generic)
    # Check both risk classification AND trend direction for appropriate messaging
    rec = "Recommendation:"
    
    # Determine forecast change
    forecast_pct_change = 0
    if avg_forecast and last_actual and last_actual != 0:
        forecast_pct_change = (avg_forecast - last_actual) / last_actual * 100
    
    if risk == 'High':
        rec += (
            "\n• 🚨 Critical Action Required: Revenue trajectory indicates sustained decline with elevated instability. "
            "Immediate cash preservation measures are essential. "
            "Prioritize high-ROI retention initiatives, execute targeted cost reductions, "
            "and conduct urgent root-cause analysis of revenue deterioration. "
            "Stress-test 6-month cash runway and prepare contingency planning."
        )
    elif risk == 'Medium':
        # More sophisticated language for Medium Risk based on direction
        if recent_short and recent_short < -0.10:
            # Medium Risk + significant decline
            rec += (
                f"\n• ⚖️ Revenue is projected to decline significantly next month ({forecast_pct_change:.1f}%). "
                "While risk remains moderate, continued downward momentum could elevate risk exposure. "
                "Close monitoring and corrective planning are advised. "
                "Recommend quarterly business reviews of retention metrics, unit economics, and go-to-market effectiveness."
            )
        elif recent_short and recent_short > 0.10:
            # Medium Risk + growth (volatile growth scenario)
            rec += (
                "\n• ⚖️ Growth trajectory present but constrained by elevated volatility. "
                "Recommend strengthening financial buffers to weather potential revenue fluctuations. "
                "Increase frequency of performance tracking, diversify customer acquisition channels, "
                "and validate sustainability through multiple leading indicators."
            )
        else:
            # Medium Risk + flat
            rec += (
                "\n• ⚖️ Moderate risk environment with mixed signals. "
                "Enhance observability: tighten cohort tracking, increase cadence of operational reviews, "
                "and maintain flexible budget allocations to respond to emerging trends."
            )
    elif risk == 'Low' and recent_short and recent_short < -0.10:
        # Special case: Low Risk (stable patterns) BUT significant decline in trend
        # This indicates controlled decline—not chaotic volatility
        rec += (
            f"\n• ⚖️ Controlled Decline: Revenue projecting {forecast_pct_change:.1f}% decrease next month "
            "with predictable patterns (low volatility). "
            "Recommend prioritizing retention improvements, conducting cohort analysis, "
            "and reviewing pricing/product-market fit to arrest decline. "
            "Consider segmented strategy for high-value customer retention while optimizing cost structure."
        )
    else:  # Low Risk (stable, no significant decline)
        rec += (
            "\n• ✅ Strong operational stability supports strategic initiatives. "
            "Leverage this period to invest prudently in growth, expand addressable market, "
            "and strengthen competitive positioning while maintaining disciplined margin management."
        )

    parts.append(rec)

    insight = "\n\n".join(parts)
    return insight
