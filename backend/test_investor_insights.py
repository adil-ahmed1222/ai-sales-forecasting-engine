"""
Test investor-ready insights for Medium Risk + significant decline scenario.
This demonstrates the enhanced language from your feedback.
"""
import pandas as pd
import numpy as np
from prediction import enterprise_forecast_pipeline

print("=" * 90)
print("INVESTOR-READY INSIGHTS TEST: Medium Risk + Significant Decline")
print("=" * 90)

# Create data: Strong starting revenue, then sharp decline (>10% last 3 months)
# This should trigger Medium Risk with significant decline messaging
dates = pd.date_range('2024-01', periods=12, freq='MS')
values = [
    5000,  # Jan
    5100,  # Feb
    5050,  # Mar (stable start)
    5000,  # Apr
    4800,  # May (decline starts)
    4600,  # Jun - 9% decline from peak
    4400,  # Jul - 12% decline
    4200,  # Aug - 14% decline (triggers >10% short-term)
    4100,  # Sep - volatile decline
    4050,  # Oct
    3900,  # Nov
    3700   # Dec - 26% decline from peak (significant drawdown)
]

df = pd.DataFrame({'date': dates, 'revenue': values})
result = enterprise_forecast_pipeline(df, months=3)

print("\n📊 SCENARIO DATA:")
print(f"  Starting Revenue: ${values[0]:,.0f}")
print(f"  Ending Revenue: ${values[-1]:,.0f}")
print(f"  Decline: {((values[-1] - values[0]) / values[0] * 100):.1f}%")
print(f"  Last 3-Month Trend: {result['recent_short_pct']:.1%}")

print("\n📈 FORECAST KPIs:")
print(f"  Composite Score: {result['composite_score']:.2f}/100")
print(f"  Risk Classification: {result['risk_label']}")
print(f"  Volatility: {result['volatility_percent']:.1f}%")
print(f"  Drawdown from Peak: {result['drawdown_percent']:.1f}%")
print(f"  3-Month Forecast: {[f'${p:,.0f}' for p in result['predictions']]}")

print("\n" + "=" * 90)
print("💡 INVESTOR-READY INSIGHT (What your board/investors see):")
print("=" * 90)
print(result['insight'])
print("\n" + "=" * 90)
