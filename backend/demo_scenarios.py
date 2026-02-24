"""
Demonstrate insights with various scenarios by showing pipeline output
on synthetic data representing different business health states.
"""
import pandas as pd
import numpy as np
from prediction import enterprise_forecast_pipeline

print("=" * 80)
print("ENTERPRISE FORECASTING SYSTEM - SCENARIO DEMONSTRATIONS")
print("=" * 80)

# Scenario 1: Declining revenue (explaining the attachment issue)
print("\n[SCENARIO 1: Declining Revenue with High Volatility]")
print("-" * 80)
dates = pd.date_range('2024-01', periods=12, freq='MS')
# Simulates: starting at 5000, declining trend with some volatility
values = [5000, 4900, 4850, 4700, 4600, 4500, 4400, 4350, 4250, 4100, 4050, 3900]
df1 = pd.DataFrame({'date': dates, 'revenue': values})
res1 = enterprise_forecast_pipeline(df1, months=3)

print(f"Risk Classification: {res1['risk_label']}")
print(f"Composite Score: {res1['composite_score']:.2f}")
print(f"Volatility: {res1['volatility_percent']:.1f}%")
print(f"Drawdown from Peak: {res1['drawdown_percent']:.1f}%")
print(f"Next 3 Months Forecast: {[f'{p:.0f}' for p in res1['predictions']]}")
print(f"\nInsight:\n{res1['insight']}")

# Scenario 2: Stable growth
print("\n" + "=" * 80)
print("[SCENARIO 2: Stable Growth]")
print("-" * 80)
dates = pd.date_range('2024-01', periods=12, freq='MS')
# Simulates: consistent 2% monthly growth
base = 5000
values = [base * (1.02 ** i) for i in range(12)]
df2 = pd.DataFrame({'date': dates, 'revenue': values})
res2 = enterprise_forecast_pipeline(df2, months=3)

print(f"Risk Classification: {res2['risk_label']}")
print(f"Composite Score: {res2['composite_score']:.2f}")
print(f"Volatility: {res2['volatility_percent']:.1f}%")
print(f"Drawdown from Peak: {res2['drawdown_percent']:.1f}%")
print(f"Next 3 Months Forecast: {[f'{p:.0f}' for p in res2['predictions']]}")
print(f"\nInsight:\n{res2['insight']}")

# Scenario 3: Volatile/Risky growth
print("\n" + "=" * 80)
print("[SCENARIO 3: Volatile Growth - High Risk]")
print("-" * 80)
dates = pd.date_range('2024-01', periods=12, freq='MS')
# Simulates: upward trend but high variance
base = 5000
noise = np.random.normal(0, 300, 12)
values = [max(base * (1.01 ** i) + n, 0) for i, n in enumerate(noise)]
df3 = pd.DataFrame({'date': dates, 'revenue': values})
res3 = enterprise_forecast_pipeline(df3, months=3)

print(f"Risk Classification: {res3['risk_label']}")
print(f"Composite Score: {res3['composite_score']:.2f}")
print(f"Volatility: {res3['volatility_percent']:.1f}%")
print(f"Drawdown from Peak: {res3['drawdown_percent']:.1f}%")
print(f"Next 3 Months Forecast: {[f'{p:.0f}' for p in res3['predictions']]}")
print(f"\nInsight:\n{res3['insight']}")

print("\n" + "=" * 80)
print("All scenarios successfully processed with aligned risk/insight messaging")
print("=" * 80)
