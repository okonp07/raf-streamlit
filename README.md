# Regime-Aware Forecasting

A single Streamlit application for detecting latent market regimes in any `yfinance`-listed asset using Gaussian Hidden Markov Models, evaluating them with walk-forward validation, and presenting the results through a modern analytics interface.

## What The App Does

Financial markets move through phases such as bull expansion, transition, stress, and recovery. Those phases are not directly observed in raw price charts, so this app infers them from engineered price and volume features with a Gaussian HMM.

The app supports two complementary workflows:

- Walk-forward analysis for out-of-sample regime detection and robustness evaluation
- Full-history regime monitoring for current-state probabilities, alerts, and forward projections

The product direction in this branch is intentionally simple:

- one Streamlit app
- one in-process analytical pipeline
- no separate backend required for the interactive experience

## Core Workflow

### 1. Data Ingestion

The app pulls historical OHLCV data from Yahoo Finance with:

- ticker selection by category
- manual ticker entry
- configurable date range
- daily, weekly, or monthly intervals
- optional adjusted prices

Data fetches are cached through Streamlit for faster iteration.

### 2. Feature Engineering

The model works on a configurable feature set derived from OHLCV data, including:

- log returns
- simple returns
- rolling volatility
- rolling mean returns
- drawdown
- rolling max drawdown
- ATR-style range
- volume change
- z-scored returns
- momentum windows
- realised volatility
- RSI
- MACD histogram
- rolling skewness
- rolling kurtosis

All rolling features are built using past information only. Rows with incomplete warm-up windows are dropped after feature construction.

### 3. HMM Regime Detection

The app fits `hmmlearn`'s `GaussianHMM` to the engineered feature matrix. You can configure:

- number of hidden states from 2 to 6
- covariance structure
- optimisation tolerance
- maximum iterations
- random seed
- train-only feature scaling

After fitting, state IDs are canonicalised so the dashboard can keep a consistent colour assignment across folds.

The default covariance choice in this branch is `diag`, which is a better stability-first starting point for financial walk-forward windows. `full` remains available when you want a more flexible fit and have enough data to support it.

### 4. Walk-Forward Validation

The walk-forward engine:

1. creates chronological train and test splits
2. fits the model on each training window only
3. scores the unseen test window
4. advances through history using rolling or expanding windows

Configurable settings include:

- train window
- test window
- step size
- minimum observations
- refit frequency

### 5. Results Dashboard

The dashboard focuses on technically honest interpretation.

The main overlay chart now works like this:

- the full price series is shown as muted historical context
- only dates that were actually scored out of sample are colour-coded by regime
- a minimum-duration smoothing filter can merge one-off state flickers before the overlay is displayed
- the app reports the percentage coverage of modelled dates that received out-of-sample assignments
- a second market-phase overlay translates the HMM output into cycle language such as capitulation, repair, distribution, and bull expansion using trailing context only

Other dashboard views include:

- transition matrix
- state occupancy
- return distributions by regime
- cumulative drawdown
- fold timeline
- per-fold train and test regime statistics
- cross-fold robustness summary
- forward regime validation tables showing forward 7d, 14d, and 30d returns, realized volatility, drawdown hit rates, and average regime duration

### 6. Regime Monitor

The monitor page trains on all available history to support:

- current regime identification
- current market phase identification
- posterior regime probabilities
- current regime duration tracking
- current market phase duration tracking
- estimated progress through the current regime
- estimated progress through the current market phase
- model-implied likely end date for the active regime
- likely end date for the active market phase
- transition alerts when confidence weakens
- forward projections using the learned transition matrix
- regime gauges and probability charts

### 7. Export

The export page generates:

- fold metrics CSV
- state assignments CSV
- summary JSON
- markdown report

If you have also run the Regime Monitor, the JSON and markdown report include the current regime lifecycle summary as well.
If the phase layer has been generated, exports also include the model-derived market phase descriptions and the current market phase lifecycle summary.

All exports are produced directly from the active Streamlit session.

## Project Structure

```text
raf-streamlit/
├── app.py
├── pages/
│   ├── 1_Data_Ingestion.py
│   ├── 2_Feature_Config.py
│   ├── 3_Model_Config.py
│   ├── 4_Walk_Forward_Setup.py
│   ├── 5_Configuration_Guide.py
│   ├── 6_Run_Analysis.py
│   ├── 7_Results_Dashboard.py
│   ├── 8_Export.py
│   ├── 9_Regime_Monitor.py
│   └── 10_About.py
├── core/
│   ├── data.py
│   ├── features.py
│   ├── metrics.py
│   ├── models.py
│   ├── monitor.py
│   └── walkforward.py
├── components/
│   ├── charts.py
│   ├── design.py
│   └── theme.py
├── assets/
├── features.md
├── requirements.txt
└── README.md
```

## Running The App

```bash
git clone https://github.com/okonp07/raf-streamlit.git
cd raf-streamlit
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m streamlit run app.py
```

The app opens locally at `http://localhost:8501`.

If you already have a system-wide `streamlit` installed, prefer `python -m streamlit run app.py` from the activated `.venv` so the app uses the project dependencies, including `hmmlearn`.

## How To Use It

### Quick Start

1. Open the app
2. Fetch data on the Data Ingestion page
3. Keep the default feature, model, and walk-forward settings
4. Run the analysis
5. Review the corrected out-of-sample overlay in Results Dashboard
6. Export the report if needed

### Practical Tips

- Start with 2 or 3 states before exploring higher-complexity models
- Keep the default `diag` covariance until you have a reason to switch
- Use a shorter date range first if you want faster iteration
- Keep `step_size == test_window` if you want non-overlapping out-of-sample test blocks
- If regimes look unstable, reduce the feature set or simplify the covariance structure
- Use the Regime Monitor only after you are comfortable with the walk-forward configuration

## Methodological Notes

- Regime detection is unsupervised, so there is no ground-truth label set
- HMM state identities are permutation-invariant, which is why canonicalisation matters for fold-to-fold comparison
- The walk-forward overlay should be interpreted as out-of-sample scored segments layered on top of full historical price context
- On structurally upward-trending assets such as BTC, even stress regimes can still average positive forward returns; the more useful test is whether they remain weaker and riskier than bull regimes
- Results remain sensitive to feature choice, window design, and state count
- This tool supports research and analysis; it is not investment advice
