# Regime-Aware Forecasting

SPY market regime detection using Gaussian HMM with walk-forward validation.

## Deploy on Streamlit Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Set **Main file path** to `app.py`
5. Click Deploy

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## How It Works

1. **Data Ingestion** — Fetches OHLCV data from Yahoo Finance
2. **Feature Engineering** — 19 regime-relevant features (volatility, momentum, RSI, etc.)
3. **Regime Detection** — Gaussian HMM identifies latent market states
4. **Walk-Forward Validation** — Chronological train/test splits, no data leakage
5. **Results** — Interactive charts, per-fold analysis, export to CSV/JSON
