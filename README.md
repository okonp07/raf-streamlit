# Regime-Aware Forecasting (RAF)

A Streamlit application for detecting latent market regimes in SPY (S&P 500 ETF) using Gaussian Hidden Markov Models, validated through a rigorous walk-forward testing framework.

---

## What This Project Does

Financial markets cycle through distinct behavioral phases: calm uptrends, volatile selloffs, sideways consolidation, and recovery periods. These phases are called **regimes**, and they are not directly observable — they must be inferred from price and volume data.

This app uses a **Gaussian Hidden Markov Model (HMM)** to identify these hidden regimes from engineered features like volatility, momentum, and drawdown. It then validates the model's robustness using **walk-forward validation** — a chronological backtesting method that prevents data leakage and simulates how the model would have performed in real time.

### Who Is This For?

- Quantitative analysts exploring regime-based strategies
- Finance students learning about HMMs and walk-forward testing
- Researchers studying market microstructure and volatility clustering
- Anyone curious about unsupervised learning applied to financial time series

---

## How It Works

### 1. Data Ingestion

The app fetches historical OHLCV (Open, High, Low, Close, Volume) data from Yahoo Finance via the `yfinance` library. You can configure:

- **Ticker symbol** (default: SPY)
- **Date range** (default: 2018-01-01 to 2025-01-01)
- **Interval** (daily, weekly, or monthly)

Data is cached for performance. Missing values are forward-filled with a 5-period limit.

### 2. Feature Engineering

Raw price data is transformed into 19 regime-relevant features. All features use **only past data** — no look-ahead leakage:

| Feature | Description |
|---------|-------------|
| Log return | ln(Close_t / Close_{t-1}) |
| Simple return | Percentage change in close price |
| Rolling volatility | Standard deviation of log returns (5, 10, 20-day windows) |
| Rolling mean return | Average log return over rolling windows |
| Drawdown | Current distance from running maximum |
| Rolling max drawdown | Worst drawdown over trailing 20 days |
| ATR range | Normalized intraday range: (High - Low) / Close |
| Volume change | Percentage change in volume |
| Z-scored return | Return standardized by its 20-day rolling mean and std |
| Momentum | Price change over 10 and 20-day lookbacks |
| Realized volatility | Square root of sum of squared returns (20-day) |
| RSI (14-day) | Relative Strength Index |
| MACD histogram | Difference between MACD line and signal line |
| Rolling skewness | 20-day rolling skew of returns |
| Rolling kurtosis | 20-day rolling kurtosis of returns |

All features can be toggled on or off from the Feature Config page.

### 3. Regime Detection (Gaussian HMM)

The app uses `hmmlearn`'s **GaussianHMM** to model the feature matrix as emissions from hidden states. Each state represents a distinct market regime characterized by its own mean vector and covariance structure.

**Configurable parameters:**

- **Number of states** (2-6, default 3) — e.g., Bull, Transition, Stress
- **Covariance type** — full, diagonal, tied, or spherical
- **Max iterations** and convergence tolerance
- **Random seed** for reproducibility
- **Feature scaling** — StandardScaler fit on training data only

After fitting, states are **not arbitrarily labeled**. Instead, the app examines each state's average return and volatility to assign descriptive labels like "Bull / Low Vol", "Transition / Moderate", or "Stress / High Vol".

### 4. Walk-Forward Validation

This is the core of the project. Unlike a simple train/test split, walk-forward validation:

1. Splits data into sequential train/test windows
2. Fits the model on the train window only
3. Predicts regimes on the unseen test window
4. Advances the window forward and repeats

**Two modes:**

- **Expanding window** — Training set grows each step (more data, but older)
- **Rolling window** — Fixed-size training window slides forward

**Key parameters:**

- Train window size (default: 504 days = ~2 years)
- Test window size (default: 63 days = ~1 quarter)
- Step size (default: 63 days)
- Minimum observations required

**Why this matters:** Walk-forward validation simulates real-world deployment. The model never sees future data during training, and scaling is always fit on the training window only. This gives honest estimates of out-of-sample regime detection quality.

### 5. Evaluation Metrics

Since regime detection is unsupervised (no ground truth labels), the app evaluates using:

| Metric | What it measures |
|--------|-----------------|
| State occupancy | Fraction of time spent in each regime |
| Regime persistence | How often the state stays the same day-to-day |
| Transition matrix | Probabilities of switching between regimes |
| State separation | How distinct the regimes are in feature space |
| Per-regime return stats | Mean return, volatility, Sharpe, max drawdown by regime |
| Log-likelihood, AIC, BIC | Model fit quality and complexity penalties |
| Cross-fold consistency | Whether regimes maintain similar characteristics across folds |
| Robustness summary | Overall assessment of model stability |

### 6. Results Dashboard

Interactive Plotly charts include:

- **Price with regime overlay** — SPY close price colored by detected regime
- **Transition probability heatmap** — How likely each regime switch is
- **State occupancy bar chart** — Time allocation across regimes
- **Return distributions by regime** — Histograms showing regime-specific return profiles
- **Cumulative drawdown chart** — Underwater equity curve
- **Fold timeline** — Visual map of all train/test windows
- **Per-fold detail** — Drill into any individual fold's statistics

### 7. Export

Download results in multiple formats:

- **Fold metrics CSV** — Persistence, separation, AIC/BIC per fold
- **State assignments CSV** — Date-level regime labels across all folds
- **Summary JSON** — Robustness metrics and regime labels
- **Markdown report** — Human-readable analysis summary

---

## Project Structure

```
raf-streamlit/
├── app.py                         # Home page
├── pages/
│   ├── 1_Data_Ingestion.py        # Fetch and preview market data
│   ├── 2_Feature_Config.py        # Toggle features on/off
│   ├── 3_Model_Config.py          # HMM parameters
│   ├── 4_Walk_Forward_Setup.py    # Validation engine settings
│   ├── 5_Run_Analysis.py          # Execute the pipeline
│   ├── 6_Results_Dashboard.py     # Charts, metrics, per-fold analysis
│   └── 7_Export.py                # Download CSV, JSON, report
├── core/
│   ├── data.py                    # yfinance data fetching with caching
│   ├── features.py                # Feature engineering pipeline
│   ├── models.py                  # HMM fitting and regime interpretation
│   ├── metrics.py                 # Evaluation metrics (occupancy, persistence, etc.)
│   └── walkforward.py             # Walk-forward validation engine
├── components/
│   └── charts.py                  # Plotly chart builders
├── .streamlit/
│   └── config.toml                # Streamlit theme configuration
├── requirements.txt               # Python dependencies
└── README.md
```

---

## Deploy on Streamlit Cloud (Free)

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Sign in with GitHub
4. Click **New app**
5. Select your repo, branch `main`, main file `app.py`
6. Click **Deploy**

Your app will be live at `https://your-app.streamlit.app` within minutes.

---

## Run Locally

```bash
# Clone the repo
git clone https://github.com/okonp07/raf-streamlit.git
cd raf-streamlit

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

Open http://localhost:8501 in your browser.

---

## How to Use the App

### Quick Start (5 minutes)

1. Open the app
2. Go to **Data Ingestion** — click **Fetch Data** (defaults are fine)
3. Skip to **Run Analysis** — click **Run Analysis**
4. Go to **Results Dashboard** — explore the charts
5. Go to **Export** — download the report

### Customized Run

1. **Data Ingestion** — Change ticker, date range, or interval
2. **Feature Config** — Disable features you don't want (e.g., turn off kurtosis)
3. **Model Config** — Try 2 states instead of 3, or change covariance to "diag"
4. **Walk-Forward Setup** — Use rolling instead of expanding, or change window sizes
5. **Run Analysis** — Execute with your custom settings
6. **Results Dashboard** — Compare regime characteristics
7. **Export** — Save everything for your research

### Tips

- **Fewer features** = faster and sometimes more stable regimes
- **2 states** gives a clear bull/bear split; **3 states** adds a transition regime
- **Rolling mode** is better for detecting regime changes in recent data
- **Larger step size** = fewer folds = faster run
- Start with a shorter date range (e.g., 2020-2025) for quick experimentation

---

## Dependencies

| Package | Purpose |
|---------|---------|
| streamlit | Web application framework |
| pandas | Data manipulation |
| numpy | Numerical computing |
| yfinance | Yahoo Finance data API (free) |
| plotly | Interactive charts |
| scikit-learn | Feature scaling (StandardScaler) |
| hmmlearn | Gaussian Hidden Markov Models |
| joblib | Caching utilities |

All dependencies are free and open source.

---

## Modeling Assumptions and Caveats

- **Unsupervised detection** — There is no ground truth for market regimes. Labels are inferred from observed statistics, not predefined
- **Gaussian emissions** — The HMM assumes features follow a Gaussian distribution within each state. Real market returns have fat tails, which the model may not fully capture
- **Stationarity** — The model assumes regime dynamics are stationary over time. In practice, market structure evolves
- **Feature selection matters** — Different features can lead to different regime assignments. The app lets you experiment with this
- **Not investment advice** — This is a research and educational tool. Regime detection results should not be used as the sole basis for trading decisions
- **Walk-forward reduces but does not eliminate overfitting** — Especially with many states and features relative to data length
- **yfinance data quality** — Free data may have occasional gaps or delays. The app handles common issues but is not a substitute for a professional data feed

---

## Suggested Next Steps

- Compare 2-state vs 3-state vs 4-state models on the same data
- Test different feature subsets to see which drive regime separation
- Try rolling vs expanding window modes
- Apply to other tickers (QQQ, IWM, GLD, TLT)
- Build regime-conditioned trading rules as a follow-up project
- Add macro features (VIX, yield curve, credit spreads) for richer state characterization
