"""Standalone training script - no relative imports."""
import os
import sys
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

# Add backend to path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

from utils import read_sales_csv, create_time_features


def prepare_datasets(df: pd.DataFrame):
    """Create features and targets."""
    df = df.copy()
    df = create_time_features(df)
    df['target_revenue'] = df['revenue'].shift(-1)
    df = df.dropna().reset_index(drop=True)

    feature_cols = ['month', 'year', 'lag_1', 'lag_3', 'lag_6', 'rolling_mean_3']
    X = df[feature_cols]
    y_reg = df['target_revenue']

    growth = (df['target_revenue'] - df['revenue']) / df['revenue']
    def map_label(g: float) -> int:
        if g > 0.10:
            return 2  # Low Risk
        if g >= 0.0:
            return 1  # Medium Risk
        return 0  # High Risk

    y_clf = growth.apply(map_label)
    return X, y_reg, X, y_clf


def train_and_save(csv_path: str, models_dir: str = 'models') -> None:
    """Train and save models."""
    os.makedirs(models_dir, exist_ok=True)
    print(f"Reading CSV: {csv_path}")
    df = read_sales_csv(csv_path)
    print(f"Loaded {len(df)} rows")

    X_reg, y_reg, X_clf, y_clf = prepare_datasets(df)
    print(f"Features shape: {X_reg.shape}")

    X_train_r, X_test_r, y_train_r, y_test_r = train_test_split(
        X_reg, y_reg, test_size=0.2, random_state=42
    )
    X_train_c, X_test_c, y_train_c, y_test_c = train_test_split(
        X_clf, y_clf, test_size=0.2, random_state=42
    )

    print("Training regressor...")
    reg = RandomForestRegressor(n_estimators=100, random_state=42)
    reg.fit(X_train_r, y_train_r)

    print("Training classifier...")
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train_c, y_train_c)

    # Evaluate
    preds = reg.predict(X_test_r)
    mae = mean_absolute_error(y_test_r, preds)
    mse = mean_squared_error(y_test_r, preds)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test_r, preds)
    print(f"Regressor MAE: {mae:.4f}, RMSE: {rmse:.4f}, R2: {r2:.4f}")

    c_preds = clf.predict(X_test_c)
    clf_acc = (c_preds == y_test_c).mean()
    print(f"Classifier accuracy: {clf_acc:.4f}")

    # Save
    reg_path = os.path.join(models_dir, 'forecast_model.pkl')
    clf_path = os.path.join(models_dir, 'risk_model.pkl')
    joblib.dump(reg, reg_path)
    joblib.dump(clf, clf_path)
    print(f"✅ Saved regressor to {reg_path}")
    print(f"✅ Saved classifier to {clf_path}")


if __name__ == '__main__':
    # Generate demo data
    print("Generating synthetic demo dataset...")
    dates = pd.date_range(end=pd.Timestamp.today(), periods=36, freq='M')
    revenue = (1000 + (np.arange(len(dates)) * 10) + np.random.normal(0, 50, len(dates))).round(2)
    demo = pd.DataFrame({'date': dates, 'revenue': revenue})
    csv_path = 'demo_sales.csv'
    demo.to_csv(csv_path, index=False)
    print(f"Created {csv_path}")

    train_and_save(csv_path, 'models')
    print("✅ Training complete!")
