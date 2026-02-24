"""
Test for exact scenario from user screenshot:
Medium Risk + 50% downward change expected next month.
"""
import pandas as pd
import numpy as np
from prediction import enterprise_forecast_pipeline

print("=" * 90)
print("MATCHING USER SCREENSHOT: Medium Risk + 50% Decline")
print("=" * 90)

# Create extreme decline scenario to trigger Medium/High Risk
# This mimics what they showed in the screenshot
dates = pd.date_range('2024-01', periods=12, freq='MS')
# Simulate: some volatility, then sharp cliff
values = [
    10000,
    10500,
    10200,
    9800,
    9200,
    8500,
    7800,
    7200,
    6500,
    5800,
    5000,
    5000   # Next month forecast should drop dramatically
]

df = pd.DataFrame({'date': dates, 'revenue': values})
result = enterprise_forecast_pipeline(df, months=3)

# Calculate what the "50% change" would be
last = values[-1]
predicted_change = (result['predictions'][0] - last) / last * 100

print("\n📊 SCENARIO DATA:")
print(f"  Current Month Revenue: ${last:,.0f}")
print(f"  Predicted Next Month: ${result['predictions'][0]:,.0f}")
print(f"  Expected Change: {predicted_change:.1f}%")
print(f"  Last 3-Month Trend: {result['recent_short_pct']:.1%}")

print("\n📈 FORECAST KPIs:")
print(f"  Composite Score: {result['composite_score']:.2f}/100")
print(f"  Risk Classification: {result['risk_label']}")
print(f"  Volatility: {result['volatility_percent']:.1f}%")
print(f"  Drawdown from Peak: {result['drawdown_percent']:.1f}%")
print(f"  Momentum (% per month): {result['momentum_pct_per_month']:.2f}%")
print(f"  Stability Index: {result['stability_index']:.1f}/100")

print("\n" + "=" * 90)
print("💡 INVESTOR-READY INSIGHT (Enhanced Language):")
print("=" * 90)
print(result['insight'])

# Also print consistency explanation if present
if result.get('consistency_explanation'):
    print("\n⚠️  CONSISTENCY ALERT:")
    print(result['consistency_explanation'])

print("\n" + "=" * 90)
print("✅ OUTPUT COMPARISON:")
print("=" * 90)
print("\n❌ OLD (Generic):")
print("  • ⚠️ Monitor metrics closely.")

print("\n✅ NEW (Investor-Ready):")
if result['risk_label'] == 'Medium' and predicted_change < -10:
    print(f"  • ⚖️ Revenue is projected to decline {abs(predicted_change):.1f}% next month.")
    print("    While risk remains moderate, continued downward momentum could elevate risk exposure.")
    print("    Close monitoring and corrective planning are advised.")
else:
    print(f"  [Output based on risk score {result['composite_score']:.1f} and trend]")
    recommendation_lines = result['insight'].split('\n')
    for line in recommendation_lines:
        if 'Recommendation' in line or line.startswith('•'):
            print(f"  {line}")
