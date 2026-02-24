from importlib import util
import pandas as pd
from pathlib import Path

spec = util.spec_from_file_location('prediction', Path(__file__).parent / 'prediction.py')
mod = util.module_from_spec(spec)
spec.loader.exec_module(mod)

csv = Path(__file__).parent / 'demo_sales.csv'
df = pd.read_csv(csv)
df['date'] = pd.to_datetime(df['date'])
res = mod.forecast_pipeline(df, months=3)
print('RISK:', res.get('risk'))
print('VOLATILITY %:', res.get('volatility_percent'))
print('SCENARIO:', res.get('scenario'))
print('INSIGHT:', res.get('insight'))
print('PREDICTIONS:', res.get('predictions'))
