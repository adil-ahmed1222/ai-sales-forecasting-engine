"""FastAPI backend with endpoints for forecasting and risk classification."""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import joblib
import io
import os

from prediction import forecast_pipeline

APP = FastAPI(title='AI Business Risk & Sales Forecasting')

# Allow local Streamlit frontend and other origins to access API
APP.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

MODELS_DIR = os.path.join(os.path.dirname(__file__), 'models')
FORECAST_MODEL = None
RISK_MODEL = None
FEATURE_SCALER = None
TARGET_SCALER = None


class ForecastResponse(BaseModel):
    predictions: list
    volatility_percent: float | None = None
    risk: str | None = None
    scenario: str | None = None
    insight: str | None = None


class RiskResponse(BaseModel):
    risk: str


@APP.on_event('startup')
def load_models_on_startup():
    """Load models on startup if available."""
    global FORECAST_MODEL, RISK_MODEL
    try:
        reg_path = os.path.join(MODELS_DIR, 'forecast_model.pkl')
        clf_path = os.path.join(MODELS_DIR, 'risk_model.pkl')
        feat_scaler_path = os.path.join(MODELS_DIR, 'feature_scaler.pkl')
        target_scaler_path = os.path.join(MODELS_DIR, 'target_scaler.pkl')
        if os.path.exists(reg_path):
            FORECAST_MODEL = joblib.load(reg_path)
            print(f"Loaded forecast model from {reg_path}")
        if os.path.exists(clf_path):
            RISK_MODEL = joblib.load(clf_path)
            print(f"Loaded risk model from {clf_path}")
        if os.path.exists(feat_scaler_path):
            FEATURE_SCALER = joblib.load(feat_scaler_path)
            print(f"Loaded feature scaler from {feat_scaler_path}")
        if os.path.exists(target_scaler_path):
            TARGET_SCALER = joblib.load(target_scaler_path)
            print(f"Loaded target scaler from {target_scaler_path}")
    except Exception as exc:
        print('Warning: could not load models on startup:', exc)


def _read_upload_to_df(file: UploadFile) -> pd.DataFrame:
    """Read uploaded CSV file into DataFrame."""
    try:
        contents = file.file.read()
        df = pd.read_csv(io.BytesIO(contents))
        if 'date' not in df.columns or 'revenue' not in df.columns:
            raise HTTPException(
                status_code=400,
                detail="CSV must contain 'date' and 'revenue' columns"
            )
        df['date'] = pd.to_datetime(df['date'])
        return df.sort_values('date').reset_index(drop=True)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f'Failed to read CSV: {e}')


@APP.post('/forecast', response_model=ForecastResponse)
async def forecast(file: UploadFile = File(...)):
    """Forecast next 3 months of revenue."""
    df = _read_upload_to_df(file)
    # Use ETS forecasting pipeline (no external model required). This ensures
    # consistent forecasting behavior that is aligned with recent trends.
    try:
        result = forecast_pipeline(df, months=3, target_scaler=TARGET_SCALER)
        # Map enterprise pipeline keys to response model keys
        return {
            'predictions': result.get('predictions', []),
            'volatility_percent': result.get('volatility_percent'),
            'risk': result.get('risk_label'),  # Map risk_label -> risk
            'scenario': result.get('scenario'),
            'insight': result.get('insight'),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Forecast failure: {e}')


@APP.post('/risk', response_model=RiskResponse)
async def risk(file: UploadFile = File(...)):
    """Classify business risk as Low, Medium, or High."""
    df = _read_upload_to_df(file)
    try:
        # Use the forecasting pipeline to compute risk and insights deterministically
        result = forecast_pipeline(df, months=1)
        return {'risk': result.get('risk', 'Medium')}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Risk classification failure: {e}')


@APP.get('/health')
def health():
    """Health check endpoint."""
    return {'status': 'ok'}
