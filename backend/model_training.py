"""Model training script: trains and saves RandomForest models for forecasting and risk classification."""
from typing import Tuple
import os
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

from utils import read_sales_csv, create_time_features


def prepare_datasets(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series]:
    """Create features and targets for forecasting and risk classification.

    Returns X_train, y_reg_train, X_clf, y_clf
    """
    df = df.copy()
    df = create_time_features(df)

    # Forecast target: next period revenue
    df['target_revenue'] = df['revenue'].shift(-1)
    df = df.dropna().reset_index(drop=True)

    # Use lag-1, lag-2, lag-3 per spec
    feature_cols = ['month', 'year', 'lag_1', 'lag_2', 'lag_3', 'rolling_mean_3']
    X = df[feature_cols]
    y_reg = df['target_revenue']

    # Risk label based on growth
    growth = (df['target_revenue'] - df['revenue']) / df['revenue']
    # Label mapping: 0=High, 1=Medium, 2=Low
    def map_label(g: float) -> int:
        if g > 0.10:
            return 2  # Low Risk
        if g >= 0.0:
            return 1  # Medium Risk
        return 0  # High Risk

    y_clf = growth.apply(map_label)

    return X, y_reg, X, y_clf


def train_and_save(csv_path: str, models_dir: str = 'models') -> None:
    """Train both models on CSV data and save to models_dir."""
    os.makedirs(models_dir, exist_ok=True)
    df = read_sales_csv(csv_path)

    X_reg, y_reg, X_clf, y_clf = prepare_datasets(df)

    X_train_r, X_test_r, y_train_r, y_test_r = train_test_split(
        X_reg, y_reg, test_size=0.2, random_state=42
    )
    X_train_c, X_test_c, y_train_c, y_test_c = train_test_split(
        X_clf, y_clf, test_size=0.2, random_state=42
    )

    # Scale features and target to stabilize LinearRegression training
    feature_scaler = StandardScaler()
    target_scaler = StandardScaler()

    X_train_r_scaled = feature_scaler.fit_transform(X_train_r)
    X_test_r_scaled = feature_scaler.transform(X_test_r)

    y_train_r_scaled = target_scaler.fit_transform(y_train_r.values.reshape(-1, 1)).ravel()
    y_test_r_orig = y_test_r.values

    # Train regressor (LinearRegression per spec)
    reg = LinearRegression()
    reg.fit(X_train_r_scaled, y_train_r_scaled)

    # Train classifier
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train_c, y_train_c)

    # Evaluate regressor
    # Predict on scaled features then inverse-transform to original revenue scale
    preds_scaled = reg.predict(X_test_r_scaled)
    preds = target_scaler.inverse_transform(preds_scaled.reshape(-1, 1)).ravel()

    mae = mean_absolute_error(y_test_r_orig, preds)
    mse = mean_squared_error(y_test_r_orig, preds)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test_r_orig, preds)
    print(f"Regressor MAE: {mae:.4f}, RMSE: {rmse:.4f}, R2: {r2:.4f}")

    # Evaluate classifier
    c_preds = clf.predict(X_test_c)
    clf_acc = (c_preds == y_test_c).mean()
    print(f"Classifier accuracy: {clf_acc:.4f}")

    # Save models
    reg_path = os.path.join(models_dir, 'forecast_model.pkl')
    clf_path = os.path.join(models_dir, 'risk_model.pkl')
    feat_scaler_path = os.path.join(models_dir, 'feature_scaler.pkl')
    target_scaler_path = os.path.join(models_dir, 'target_scaler.pkl')

    joblib.dump(reg, reg_path)
    joblib.dump(clf, clf_path)
    joblib.dump(feature_scaler, feat_scaler_path)
    joblib.dump(target_scaler, target_scaler_path)

    print(f"Saved regressor to {reg_path}")
    print(f"Saved classifier to {clf_path}")
    print(f"Saved feature scaler to {feat_scaler_path}")
    print(f"Saved target scaler to {target_scaler_path}")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Train forecasting and risk models')
    parser.add_argument('--csv', type=str, help='Path to sales CSV', required=False)
    parser.add_argument('--models-dir', type=str, default='models')
    args = parser.parse_args()

    if args.csv is None:
        # Generate a small synthetic dataset for quick demo
        print('No CSV provided, generating synthetic demo dataset: demo_sales.csv')
        dates = pd.date_range(end=pd.Timestamp.today(), periods=36, freq='M')
        revenue = (1000 + (np.arange(len(dates)) * 10) + np.random.normal(0, 50, len(dates))).round(2)
        demo = pd.DataFrame({'date': dates, 'revenue': revenue})
        demo.to_csv('demo_sales.csv', index=False)
        csv_path = 'demo_sales.csv'
    else:
        csv_path = args.csv

    train_and_save(csv_path, args.models_dir)
