"""Streamlit frontend for business forecasting and risk analysis."""
import streamlit as st
import requests
import pandas as pd
import numpy as np
from io import BytesIO
import time
from fastapi import FastAPI

# Expose a minimal FastAPI `app` object so platforms that look for an
# ASGI application (or run health checks) can discover it when serving
# the frontend. This does not interfere with Streamlit execution.
app = FastAPI(title="AI Business Risk & Sales Forecasting")

API_URL = "https://ai-forecast-backend1.onrender.com"


def call_backend(endpoint, file_bytes):
    """Post a file to ``/endpoint`` on the backend and return JSON.

    The function handles Render's cold-start behaviour by retrying up to
    three times when the response is not JSON. If the ``Content-Type``
    header does not start with ``application/json`` we assume the
    service is still waking up and pause 5 seconds before trying again.

    Parameters
    ----------
    endpoint : str
        Path portion (eg. ``"forecast"`` or ``"risk"``) without leading
        slash.
    file_bytes : bytes
        The raw contents of the uploaded CSV file.

    Returns
    -------
    dict or None
        Parsed JSON from the backend, or ``None`` when all retries fail.
    """
    url = f"{API_URL}/{endpoint}"

    for attempt in range(3):
        try:
            response = requests.post(
                url,
                files={"file": ("upload.csv", file_bytes)},
                timeout=10,
            )

            content_type = response.headers.get("content-type", "")

            if content_type.startswith("application/json"):
                return response.json()
            else:
                # probably an HTML page from Render during cold start
                st.info("⏳ Waking up server, please wait...")
                time.sleep(5)

        except Exception:
            # any network error or timeout also triggers a retry
            st.info("⏳ Waking up server, please wait...")
            time.sleep(5)

    st.error("⚠️ Server is starting. Please try again in a moment.")
    return None

st.set_page_config(page_title='AI Business Risk & Sales Forecast', layout='wide')

# Professional Header with Branding
st.markdown("""
<h1 style='text-align: center; color: #1f77b4;'>
📊 AI Business Risk & Sales Forecasting
</h1>
<p style='text-align: center; font-size:18px; color:#555;'>
Predict revenue. Detect risk. Make smarter decisions.
</p>
<hr style='margin: 20px 0;'>
""", unsafe_allow_html=True)

# Feature Highlights
col_feat1, col_feat2, col_feat3, col_feat4 = st.columns(4)
with col_feat1:
    st.markdown("**🔮 3-Month Forecast**\nAccurate revenue predictions")
with col_feat2:
    st.markdown("**⚠️ Risk Detection**\nLow / Medium / High classification")
with col_feat3:
    st.markdown("**📈 Growth Analysis**\nTrend & volatility metrics")
with col_feat4:
    st.markdown("**🎯 Actionable Insights**\nAI-generated recommendations")

st.markdown("---")

# Sample CSV Download Section
st.subheader("📋 Get Started")
col_download, col_info = st.columns([2, 3])

with col_download:
    sample_df = pd.DataFrame({
        "date": ["2024-01-01", "2024-02-01", "2024-03-01", "2024-04-01", "2024-05-01"],
        "revenue": [10000, 12000, 9500, 11000, 13500]
    })
    csv_sample = sample_df.to_csv(index=False)
    st.download_button(
        label="⬇️ Download Sample CSV",
        data=csv_sample,
        file_name="sample_sales.csv",
        mime="text/csv",
        use_container_width=True
    )

with col_info:
    st.info("💡 **CSV Requirements:**\n- Column 1: `date` (any format)\n- Column 2: `revenue` (numeric values)\n- At least 12 months of data recommended")

st.markdown("---")

# File Upload
st.subheader("📤 Upload Your Sales Data")
uploaded = st.file_uploader('Choose a CSV file', type=['csv'])

if uploaded is not None:
    try:
        df = pd.read_csv(uploaded)
        
        # Validate data
        if 'date' not in df.columns or 'revenue' not in df.columns:
            st.error("❌ CSV must contain 'date' and 'revenue' columns")
        else:
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            st.success(f"✅ Loaded {len(df)} records | Date range: {df['date'].min().date()} to {df['date'].max().date()}")
            
            with st.expander("📊 View Data Preview", expanded=False):
                st.dataframe(df.tail(10), use_container_width=True)
            
            st.markdown("---")
            
            # Forecast and Risk Buttons
            col_forecast, col_risk, col_both = st.columns(3)
            
            forecast_clicked = col_forecast.button('🔮 Get Forecast', use_container_width=True, key='forecast_btn')
            risk_clicked = col_risk.button('⚡ Get Risk Assessment', use_container_width=True, key='risk_btn')
            both_clicked = col_both.button('🚀 Analyze All', use_container_width=True, key='both_btn')
            
            forecast_data = None
            risk_data = None
            
            # Get Forecast
            if forecast_clicked or both_clicked:
                with st.spinner('🔄 Forecasting next 3 months revenue...'):
                    json_resp = call_backend('forecast', uploaded.getvalue())
                    if json_resp is not None:
                        # successful call_backend already displayed any info
                        forecast_data = json_resp.get('predictions', [])
                        st.success('✅ Forecast complete')
                    # otherwise error message is shown by call_backend
            
            # Get Risk
            if risk_clicked or both_clicked:
                with st.spinner('⚙️ Analyzing business risk...'):
                    json_resp = call_backend('risk', uploaded.getvalue())
                    if json_resp is not None:
                        risk_data = json_resp.get('risk')
                        st.success('✅ Risk assessment complete')
                    # call_backend handles retries and error messaging
            
            st.markdown("---")
            
            # KPI Cards Section
            if forecast_data or risk_data:
                st.subheader("📊 Key Performance Indicators")
                
                kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
                
                if forecast_data:
                    # Calculate metrics
                    next_month = forecast_data[0]
                    total_forecast = sum(forecast_data)
                    avg_forecast = total_forecast / len(forecast_data)
                    current_revenue = df['revenue'].iloc[-1]
                    growth_pct = ((next_month - current_revenue) / current_revenue) * 100
                    
                    with kpi_col1:
                        st.metric(
                            "📈 Next Month Forecast",
                            f"${next_month:,.0f}",
                            delta=f"{growth_pct:+.1f}%" if growth_pct else None
                        )
                    
                    with kpi_col2:
                        st.metric(
                            "📊 3-Month Total",
                            f"${total_forecast:,.0f}",
                            delta=f"Avg: ${avg_forecast:,.0f}"
                        )
                
                if risk_data:
                    with kpi_col3:
                        if risk_data == 'Low':
                            risk_color = '🟢'
                        elif risk_data == 'Medium':
                            risk_color = '🟡'
                        else:
                            risk_color = '🔴'
                        st.metric("⚠️ Risk Level", f"{risk_color} {risk_data}")
                
                # Volatility score
                if len(df) > 1:
                    volatility = df['revenue'].std() / df['revenue'].mean() * 100
                    with kpi_col4:
                        st.metric(
                            "📉 Volatility Score",
                            f"{volatility:.1f}%",
                            delta="Revenue stability" if volatility < 15 else "High variance"
                        )
                
                st.markdown("---")
            
            # Forecast Visualization
            if forecast_data:
                st.subheader("📈 Revenue Forecast Trend")
                
                hist = df.copy()
                last_date = hist['date'].max()
                future_dates = pd.date_range(
                    last_date + pd.offsets.MonthEnd(1),
                    periods=len(forecast_data),
                    freq='M'
                )
                
                fut_df = pd.DataFrame({
                    'date': future_dates,
                    'revenue': forecast_data,
                    'type': 'Forecast'
                })
                
                hist['type'] = 'Historical'
                combined = pd.concat([
                    hist[['date', 'revenue', 'type']],
                    fut_df
                ], ignore_index=True)
                
                # Create enhanced chart with Plotly
                try:
                    import plotly.graph_objects as go
                    
                    fig = go.Figure()
                    
                    # Historical data
                    hist_data = combined[combined['type'] == 'Historical']
                    fig.add_trace(go.Scatter(
                        x=hist_data['date'],
                        y=hist_data['revenue'],
                        mode='lines+markers',
                        name='Historical Revenue',
                        line=dict(color='#1f77b4', width=3),
                        marker=dict(size=6)
                    ))
                    
                    # Forecast data
                    forecast_data_df = combined[combined['type'] == 'Forecast']
                    fig.add_trace(go.Scatter(
                        x=forecast_data_df['date'],
                        y=forecast_data_df['revenue'],
                        mode='lines+markers',
                        name='Predicted Revenue',
                        line=dict(color='#ff7f0e', width=3, dash='dash'),
                        marker=dict(size=8, symbol='diamond')
                    ))
                    
                    fig.update_layout(
                        title='Revenue Forecast vs Historical Data',
                        xaxis_title='Date',
                        yaxis_title='Revenue ($)',
                        hovermode='x unified',
                        height=450,
                        template='plotly_white'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                except ImportError:
                    # Fallback to basic line chart
                    combined_pivot = combined.set_index('date')
                    st.line_chart(combined_pivot['revenue'], use_container_width=True)
                
                # Month-by-month breakdown
                with st.expander("📋 Monthly Forecast Breakdown", expanded=False):
                    forecast_table = pd.DataFrame({
                        'Month': [(last_date + pd.offsets.MonthEnd(i+1)).strftime('%B %Y') 
                                 for i in range(len(forecast_data))],
                        'Predicted Revenue': [f"${v:,.2f}" for v in forecast_data]
                    })
                    st.table(forecast_table)
            
            # AI Insights Section
            if forecast_data and risk_data:
                st.markdown("---")
                st.subheader("🧠 AI-Generated Insights")
                
                current_rev = df['revenue'].iloc[-1]
                next_month_pred = forecast_data[0]
                trend = "📈 upward" if next_month_pred > current_rev else "📉 downward"
                trend_pct = abs((next_month_pred - current_rev) / current_rev * 100)
                
                insight = f"""
**Revenue Trend:** {trend} trend expected with {trend_pct:.1f}% change next month.

**Risk Assessment:** Business classified as **{risk_data} Risk**.

**Recommendation:** 
- {'✅ Maintain current strategy - stable growth.' if risk_data == 'Low' else '⚠️ Monitor metrics closely.' if risk_data == 'Medium' else '❌ Take corrective action - revenue decline detected.'}
                """
                st.markdown(insight)
    
    except Exception as e:
        st.error(f'❌ Failed to process file: {e}')

else:
    st.info('👈 Upload a CSV file to get started with forecasting and risk analysis')
