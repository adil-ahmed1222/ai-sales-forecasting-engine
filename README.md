# AI Business Risk & Sales Forecasting System

Full-stack ML application: forecasts next 3 months revenue, classifies business risk, with FastAPI backend + Streamlit frontend.

## 📁 Structure

```
ai_business_forecasting/
├── backend/
│   ├── __init__.py
│   ├── main.py                 (FastAPI app with /forecast, /risk, /health endpoints)
│   ├── model_training.py       (trains & saves models via joblib)
│   ├── prediction.py           (forecast & risk classification logic)
│   ├── utils.py                (CSV reader, feature engineering)
│   └── models/
│       ├── forecast_model.pkl  (RandomForestRegressor)
│       └── risk_model.pkl      (RandomForestClassifier)
├── frontend/
│   └── app.py                  (Streamlit interactive UI)
├── requirements.txt
└── README.md
```

## 🚀 Quick Start

### 1. Setup Environment

```powershell
# Windows PowerShell
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r ai_business_forecasting/requirements.txt
```

### 2. Train Models

```powershell
cd ai_business_forecasting/backend
python model_training.py
# Or with your CSV:
python model_training.py --csv path/to/your/sales.csv
```

This generates synthetic data if no CSV provided and saves:
- `models/forecast_model.pkl` (revenue forecaster)
- `models/risk_model.pkl` (risk classifier)

### 3. Run Backend

```powershell
# From workspace root
uvicorn ai_business_forecasting.backend.main:APP --reload --port 8000
```

Backend will start at `http://localhost:8000`

### 4. Run Frontend (Separate Terminal)

```powershell
# Ensure venv is activated
.venv\Scripts\Activate.ps1

# Run Streamlit app
streamlit run ai_business_forecasting/frontend/app.py
```

Frontend opens at `http://localhost:8501`

## 📊 CSV Format

Required columns:
- `date` - Any parseable date format
- `revenue` - Numeric sales/revenue values

Example:
```
date,revenue
2023-01-31,1050.25
2023-02-28,1065.50
2023-03-31,1080.75
...
```

## 🔗 API Endpoints

### POST `/forecast`
Upload CSV → returns next 3 months revenue predictions
```json
{
  "predictions": [1100.50, 1150.75, 1200.25]
}
```

### POST `/risk`
Upload CSV → returns risk classification (Low/Medium/High)
```json
{
  "risk": "Low"
}
```

### GET `/health`
Health check
```json
{
  "status": "ok"
}
```

## 🤖 Risk Classification Rules

- **Low Risk**: Revenue growth > 10%
- **Medium Risk**: Revenue stable (0 - 10% growth)
- **High Risk**: Revenue declining (< 0%)

## 🔧 Model Details

### Forecast Model
- **Algorithm**: RandomForestRegressor (100 estimators)
- **Features**: month, year, lag_1, lag_3, lag_6, rolling_mean_3
- **Target**: Next month revenue
- **Metrics**: MAE, RMSE, R²

### Risk Model
- **Algorithm**: RandomForestClassifier (100 estimators)
- **Target**: Risk category (0=High, 1=Medium, 2=Low)
- **Accuracy**: Evaluated on 20% test split

## 📝 Notes

- Models load once on API startup for efficiency
- Lazy loading available if models not found at startup
- CORS enabled for cross-origin requests
- Forecast uses iterative feature generation for multi-step predictions

## 🛠️ Troubleshooting

**"streamlit is not recognized"**
- Ensure venv is activated: `.venv\Scripts\Activate.ps1`
- Install again: `pip install streamlit`

**"Backend not running"**
- Check uvicorn started: `uvicorn ai_business_forecasting.backend.main:APP --reload --port 8000`
- Allow firewall access if needed

**"Models not found"**
- Run training: `python ai_business_forecasting/backend/model_training.py`
- Verify files exist in `ai_business_forecasting/backend/models/`
