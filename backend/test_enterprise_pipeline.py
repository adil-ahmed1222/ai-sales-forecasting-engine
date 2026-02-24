import pandas as pd
from pathlib import Path
from prediction import enterprise_forecast_pipeline

csv = Path(__file__).parent / 'demo_sales.csv'
df = pd.read_csv(csv)
res = enterprise_forecast_pipeline(df, months=3)
print('Predictions:', res['predictions'])
print('Lower:', res['lower'])
print('Upper:', res['upper'])
print('Volatility %:', res['volatility_percent'])
print('Drawdown %:', res['drawdown_percent'])
print('Composite Score:', res['composite_score'])
print('Risk Label:', res['risk_label'])
print('Stability Index:', res['stability_index'])
print('Insight:\n', res['insight'])
