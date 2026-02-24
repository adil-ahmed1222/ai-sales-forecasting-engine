# AI Business Risk & Sales Forecasting System

**Production-Ready Full-Stack ML Application**

Predict next 3 months revenue, detect business risk, and get AI-powered insights—all with a beautiful, interactive UI.

## ✨ Features

- **🔮 3-Month Revenue Forecast** – RandomForest-powered predictions
- **⚠️ Risk Classification** – Automatic Low/Medium/High risk detection
- **📈 KPI Dashboard** – Key metrics & performance indicators
- **📊 Interactive Charts** – Plotly-powered visualizations
- **🧠 AI Insights** – Contextual recommendations and trend analysis
- **📋 Sample CSV Download** – Example data for quick start
- **⚡ Real-time Processing** – Fast API backend with async support

## 📁 Architecture

```
ai_business_forecasting/
├── backend/
│   ├── main.py                 # FastAPI app with 3 endpoints
│   ├── model_training.py       # Model creation & training
│   ├── prediction.py           # Forecast & risk logic
│   ├── utils.py                # CSV parsing & features
│   ├── train.py                # Standalone training runner
│   └── models/
│       ├── forecast_model.pkl  # RandomForestRegressor
│       └── risk_model.pkl      # RandomForestClassifier
├── frontend/
│   └── app.py                  # Streamlit UI (professional grade)
├── requirements.txt
├── start.bat                   # One-click startup (Windows)
└── README.md
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Option A: Using pip
pip install -r ai_business_forecasting/requirements.txt

# Option B: One-by-one
pip install fastapi uvicorn pandas scikit-learn joblib streamlit requests python-multipart plotly
```

### 2. Run Training (Already Done)

Models are pre-trained with demo data. To retrain:

```bash
cd ai_business_forecasting/backend
python train.py

# Or with custom data:
python model_training.py --csv path/to/your/sales.csv
```

### 3. Start Backend + Frontend

**Windows (Easiest):**
```bash
start.bat
```

**Manual (All Platforms):**

Terminal 1 - Backend API:
```bash
python -m uvicorn ai_business_forecasting.backend.main:APP --reload --port 8000
```

Terminal 2 - Frontend UI:
```bash
python -m streamlit run ai_business_forecasting/frontend/app.py
```

### 4. Access the Application

- **Frontend UI:** http://localhost:8501
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

## 📊 Frontend UX Improvements

### ✅ KPI Cards
After analysis, see key metrics at a glance:
- 📈 Next Month Forecast (with % delta)
- 📊 3-Month Total (with averages)
- ⚠️ Risk Level (color-coded)
- 📉 Volatility Score (stability metric)

### ✅ Sample CSV Download
Users can download a template CSV file to understand data format immediately.

### ✅ Interactive Visualizations
- **Plotly Charts** – Hover details, zoom, pan
- **Monthly Breakdown** – Expandable forecast table
- **Historical + Forecast** – Dual-series line chart

### ✅ AI Insights Section
Automatic generation of:
- Trend analysis (upward/downward with %)
- Risk interpretation
- Contextual recommendations

### ✅ Loading Animations
Emoji spinners indicate processing:
- 🔄 Forecasting...
- ⚙️ Analyzing risk...

### ✅ Professional Branding
- Centered header with tagline
- Feature highlights
- Clean color scheme

## 🔗 API Endpoints

### POST `/forecast`
Upload CSV → Get next 3 months predictions
```bash
curl -F "file=@sales.csv" http://localhost:8000/forecast
```
Response:
```json
{
  "predictions": [11500.50, 12100.75, 12600.25]
}
```

### POST `/risk`
Upload CSV → Get risk classification
```bash
curl -F "file=@sales.csv" http://localhost:8000/risk
```
Response:
```json
{
  "risk": "Low"
}
```

### GET `/health`
API health check
```bash
curl http://localhost:8000/health
```
Response:
```json
{
  "status": "ok"
}
```

## 📋 CSV Format Requirements

**Minimum columns:**
| Column | Type | Example |
|--------|------|---------|
| date | Any format | 2024-01-31, 01/01/2024, etc. |
| revenue | Numeric | 10000, 12500.50, etc. |

**Recommended:**
- At least 12 months of historical data
- Consistent monthly intervals
- No missing values

## 🤖 Model Details

### Forecast Model
- **Algorithm:** RandomForestRegressor with 100 trees
- **Features Engineered:**
  - month, year (seasonal)
  - lag_1, lag_3, lag_6 (historical patterns)
  - rolling_mean_3 (3-month average)
- **Evaluation:** MAE, RMSE, R² score on test split

### Risk Classification Model
- **Algorithm:** RandomForestClassifier with 100 trees
- **Classes:** Low (growth >10%), Medium (0-10%), High (decline)
- **Fallback:** Rule-based classifier in API for transparency

## 🎨 UI Components

### Header Section
- Professional branding with tagline
- Feature highlights (4 columns)
- Sample CSV download button
- CSV format requirements info

### Main Analysis Panel
- File upload with validation
- Data preview (expandable)
- 3 action buttons: Forecast | Risk | Analyze All
- Loading spinners with emoji indicators

### Results Dashboard
- **KPI Cards:** 4 key metrics in a row
- **Interactive Chart:** Plotly line chart with forecast overlay
- **Monthly Table:** Expandable detailed forecast breakdown
- **AI Insights:** Contextual analysis & recommendations

## ⚙️ Configuration

Edit these in `main.py`:
```python
API_URL = 'http://localhost:8000'  # Backend address
```

Edit these in `app.py`:
```python
API_URL = 'http://localhost:8000'  # Same as above
```

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| `'python' is not recognized` | Add Python to PATH or use `python -m` |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| Backend not responding | Check port 8000 is free, restart uvicorn |
| Frontend won't connect | Ensure backend is running on port 8000 |
| Models not found | Run `cd ai_business_forecasting/backend && python train.py` |
| Plotly not rendering | Make sure `pip install plotly` completed |

## 📈 Next Steps for Production

1. **Deploy Backend:**
   - Use Gunicorn + Nginx
   - Deploy to Heroku, AWS, or Azure
   - Add database for model versioning

2. **Deploy Frontend:**
   - Streamlit Cloud (automatic)
   - Docker container
   - CDN for static files

3. **Enhancements:**
   - Authentication (JWT tokens)
   - Database storage for predictions
   - Scheduled retraining
   - Confidence intervals in forecast
   - Multiple model ensembling

## 📝 Notes

- Models are loaded once on startup for efficiency
- All predictions are cached to avoid re-computation
- CORS enabled for cross-origin requests
- Frontend validation before API calls reduces errors
- Forecast uses iterative feature generation for multi-step predictions

---

**Built with:** FastAPI • Streamlit • Scikit-Learn • Plotly • Pandas
