# Features & Configuration Guide

This document provides a comprehensive reference for every configurable parameter in the Regime-Aware Forecasting app. It is intended to help users — from first-time explorers to experienced quant researchers — understand what each setting does, why it matters, and what happens when you change it.

---

## Table of Contents

1. [Feature Configuration](#1-feature-configuration)
2. [Model Configuration](#2-model-configuration)
3. [Walk-Forward Validation Setup](#3-walk-forward-validation-setup)
4. [Practical Guidance](#4-practical-guidance)

---

## 1. Feature Configuration

Features are numerical signals engineered from raw price and volume data. They are the inputs to the regime detection model. The quality and relevance of features directly determine whether the model can distinguish meaningful market regimes from noise.

**Key Principles:**

- Every feature uses only past data. No future information leaks into any calculation.
- Features are computed before the walk-forward loop begins. Scaling (standardization) happens inside each fold, fit only on the training window.
- More features give the model richer information but increase the risk of overfitting and slow down computation.
- Fewer, well-chosen features often produce more stable and interpretable regimes.

### 1.1 Return Features

Returns measure the rate of price change and are the most fundamental input for any regime model.

| Feature | Default | What It Does | Increasing / Enabling | Decreasing / Disabling |
|---------|---------|--------------|----------------------|----------------------|
| **Log Returns** | On | Computes `ln(Close_t / Close_{t-1})`. Log returns are additive across time and approximately normally distributed, making them the standard choice for statistical models. | Recommended to keep enabled. Log returns are the primary signal that distinguishes bull (positive mean) from bear (negative mean) regimes. | Disabling removes the most direct measure of price direction. Only disable if you want the model to focus purely on volatility or volume features. |
| **Simple Returns** | On | Computes `(Close_t - Close_{t-1}) / Close_{t-1}`. Percentage change in price. More intuitive than log returns but less mathematically convenient. | Provides an additional return perspective. Useful when combined with log returns for richer representation. | Disabling has minimal impact if log returns are still enabled, since they are highly correlated. Disable to reduce feature redundancy. |

### 1.2 Volatility Features

Volatility features capture the magnitude of price fluctuations. They are critical for regime detection because market regimes are primarily defined by shifts in volatility.

| Feature | Default | What It Does | Increasing Window Size | Decreasing Window Size |
|---------|---------|--------------|----------------------|----------------------|
| **Rolling Volatility (5d)** | On | Standard deviation of log returns over the last 5 trading days. Captures very short-term volatility bursts such as earnings reactions or sudden selloffs. | N/A (window is fixed at 5). To add longer windows, use the multi-select. | N/A. Disabling removes the short-term volatility signal. The model loses sensitivity to rapid volatility spikes. |
| **Rolling Volatility (10d)** | On | Standard deviation over 10 days. Captures intra-month volatility trends, smoothing out single-day noise. | N/A. | Disabling removes the medium-short-term volatility view. |
| **Rolling Volatility (20d)** | On | Standard deviation over 20 days (~1 trading month). The most commonly used volatility window in quantitative finance. Balances responsiveness with stability. | Adding longer windows (30, 60) captures multi-month volatility trends and structural regime shifts. Useful for detecting prolonged stress periods like 2008 or 2020. | Disabling removes the standard monthly volatility measure. Not recommended unless you are intentionally restricting the feature set. |

**How to use the Volatility Windows selector:**

Select one or more window sizes from `[5, 10, 20, 30, 60]`. Each creates a separate feature column. Selecting all five gives the model a multi-scale view of volatility — from weekly to quarterly. Selecting only `[20]` gives a single, stable volatility measure with less noise but less granularity.

### 1.3 Rolling Statistics

| Feature | Default | What It Does | Increasing Window | Decreasing Window |
|---------|---------|--------------|-------------------|-------------------|
| **Rolling Mean Return (5d)** | On | Average log return over the last 5 days. Captures short-term trend direction. | Longer windows (10, 20) smooth out noise and capture broader trend direction. A 20-day rolling mean reflects roughly one month of market sentiment. | Shorter windows react faster to reversals but are noisier. A 5-day mean can flip positive/negative on a single volatile day. |
| **Rolling Mean Return (20d)** | On | Average log return over 20 days. Reflects the prevailing trend over the past month. Useful for distinguishing trending vs mean-reverting regimes. | Adding 30 or 60-day windows captures structural trends across quarters. | Removing longer windows makes the model more reactive to short-term moves, potentially causing more frequent regime switches. |

### 1.4 Drawdown Features

Drawdown measures how far the current price has fallen from its peak. It captures the pain of being invested — a signal that correlates strongly with investor behavior and regime shifts.

| Feature | Default | What It Does | Effect of Enabling | Effect of Disabling |
|---------|---------|--------------|-------------------|-------------------|
| **Drawdown** | On | `(Close - Running Max Close) / Running Max Close`. Always zero or negative. Deep drawdowns indicate stress or bear markets. | Gives the model a direct measure of loss severity. Helps distinguish between mild pullbacks (transition regime) and deep corrections (stress regime). | Removes loss-severity information. The model can still detect high-volatility periods via volatility features but cannot distinguish between volatile rallies and volatile selloffs as effectively. |
| **Rolling Max Drawdown (20d)** | On | The worst (most negative) drawdown observed over the last 20 trading days. Captures the severity of the recent worst-case loss. | Highlights the trailing worst-case scenario. Useful for identifying regime transitions where drawdowns are worsening even if current volatility appears moderate. | Removes trailing worst-case information. The model relies more on current-snapshot features. |

### 1.5 Range and Volume Features

| Feature | Default | What It Does | Effect of Enabling | Effect of Disabling |
|---------|---------|--------------|-------------------|-------------------|
| **ATR Range** | On | `(High - Low) / Close`. Normalized intraday price range. A proxy for intraday volatility that captures information not present in close-to-close returns (e.g., large intraday swings that close flat). | Adds intraday volatility information. Particularly useful during regimes where the market is volatile intraday but closes near unchanged (common in transition periods). | Removes intraday range signal. The model relies solely on close-to-close measures. |
| **Volume Change** | On | Percentage change in daily trading volume. Volume spikes often accompany regime transitions — capitulation selloffs, breakout rallies, or panic buying. | Adds a non-price signal. Volume behavior differs across regimes: low volume in calm markets, volume surges during stress. | Removes volume information. The model becomes purely price-based. Consider disabling if volume data quality is poor. |

### 1.6 Standardized and Momentum Features

| Feature | Default | What It Does | Increasing Lookback | Decreasing Lookback |
|---------|---------|--------------|-------------------|-------------------|
| **Z-Scored Return (20d)** | On | `(log_return - 20d_mean) / 20d_std`. Standardizes today's return relative to its recent history. A z-score of +3 means today's return is 3 standard deviations above the recent average — an extreme move. | N/A (fixed at 20d). | Disabling removes the context-adjusted return signal. Raw returns alone cannot distinguish between a 1% move in a calm market (unusual) and a 1% move in a volatile market (normal). |
| **Momentum (10d)** | On | `Close_t / Close_{t-10} - 1`. Total return over the last 10 trading days. Captures short-term price momentum. | Longer lookbacks (20d, 30d) capture medium-term trends. 20-day momentum approximates one-month total return. | Shorter lookbacks are noisier but faster to react. 10-day momentum can capture the start of trend reversals before 20-day momentum does. |
| **Momentum (20d)** | On | Total return over 20 days. The standard momentum measure in factor-based strategies. | Adding 30 or 60-day windows captures multi-month trends relevant to structural regime identification. | Removing reduces the model's ability to distinguish trending from mean-reverting market phases. |
| **Realized Volatility (20d)** | On | `sqrt(sum of squared log returns over 20 days)`. A non-parametric volatility estimator that weights large moves more heavily than rolling standard deviation. More sensitive to tail events. | N/A (fixed at 20d). | Disabling removes the tail-sensitive volatility measure. Rolling std dev may underweight extreme days in a 20-day window. |

### 1.7 Technical Indicators

| Feature | Default | What It Does | Effect of Enabling | Effect of Disabling |
|---------|---------|--------------|-------------------|-------------------|
| **RSI (14d)** | On | Relative Strength Index: measures the ratio of recent gains to recent losses on a 0-100 scale. Below 30 = oversold, above 70 = overbought. Captures momentum exhaustion. | Adds a bounded momentum signal that helps identify regime extremes. RSI tends to stay elevated (60-80) in bull regimes and depressed (20-40) in stress regimes. | Removes the overbought/oversold signal. Momentum features partially compensate but lack the bounded scaling. |
| **MACD Signal** | On | Moving Average Convergence Divergence histogram: difference between the MACD line (12-day EMA minus 26-day EMA) and its 9-day signal line. Captures trend momentum shifts. | Adds a trend-following signal that detects changes in momentum direction. MACD histogram crossing zero often coincides with regime transitions. | Removes the trend-momentum crossover signal. Other momentum features partially compensate. |
| **Rolling Skewness (20d)** | On | Skewness of log returns over 20 days. Measures the asymmetry of the return distribution. Negative skew (common in stress regimes) means large negative returns are more frequent than large positive ones. | Adds distributional shape information beyond mean and variance. Helps distinguish between symmetric volatility (transition) and left-skewed volatility (stress/crash). | Removes distribution asymmetry information. Mean and variance features cannot capture tail direction. |
| **Rolling Kurtosis (20d)** | On | Kurtosis of log returns over 20 days. Measures the heaviness of distribution tails. High kurtosis means extreme moves (positive or negative) are more frequent than a normal distribution would predict. | Adds tail-fatness information. High kurtosis regimes correspond to periods of frequent surprises — both up and down. | Removes tail-risk information. Consider disabling if kurtosis estimates are noisy due to short window size. |

---

## 2. Model Configuration

The model configuration controls the Gaussian Hidden Markov Model that learns to identify latent market regimes from the feature data.

### 2.1 Core Parameters

| Parameter | Default | Range | What It Does | Increasing | Decreasing |
|-----------|---------|-------|--------------|-----------|------------|
| **Number of Hidden States** | 3 | 2 - 6 | The number of distinct market regimes the model will try to identify. This is the most important hyperparameter. | More states = finer regime distinctions (e.g., mild bull, strong bull, transition, mild stress, crash). However, more states require more data to estimate reliably and are harder to interpret. Above 4 states, regimes often become unstable across folds. | Fewer states = coarser but more stable regimes. **2 states** gives a clean bull/bear split. **3 states** adds a transition regime. 2-3 states is recommended for most use cases. |
| **Covariance Type** | full | full, diag, tied, spherical | Controls how the model represents the spread/correlation of features within each state. | **full**: Each state has its own full covariance matrix (features can be correlated differently per regime). Most flexible but requires the most data. Best for rich feature sets. | **diag**: Features are assumed independent within each state. Fewer parameters, more stable with limited data. **tied**: All states share one covariance matrix; only means differ. **spherical**: Each state has a single variance (all features equally variable). Use with very few data points. |
| **Max Iterations** | 200 | 10 - 1000 | Maximum number of EM (Expectation-Maximization) algorithm iterations for fitting. | Higher values give the optimizer more time to converge. Rarely needed above 200 for daily market data. Set to 500+ only if you see convergence warnings. | Lower values speed up fitting but risk stopping before convergence. Below 50, the model may produce poor regime assignments. |
| **Convergence Tolerance** | 1e-4 | 1e-8 - 1e-1 | The algorithm stops when the log-likelihood improvement between iterations falls below this threshold. | Tighter tolerance (e.g., 1e-6) demands more precise convergence. Marginally better fit but slower. | Looser tolerance (e.g., 1e-2) stops earlier. Faster but the model may not have fully converged. Use for quick exploratory runs. |
| **Random Seed** | 42 | 0 - 99999 | Initializes the random number generator for reproducible results. The HMM uses random initialization for state parameters. | Changing the seed produces different initial conditions, which may lead to different local optima and different regime assignments. Use multiple seeds to test stability. | N/A. Keep fixed for reproducibility; vary to test robustness. |
| **Scale Features** | On | On / Off | When enabled, features are standardized (zero mean, unit variance) using a StandardScaler fit only on the training data of each fold. | **On** (recommended): Ensures all features contribute equally regardless of their natural scale. Volatility (small numbers like 0.01) and RSI (numbers like 30-70) would otherwise dominate the model differently. | **Off**: Use only if features are already on comparable scales or if you intentionally want some features to dominate. Not recommended for most cases. |

### 2.2 How State Count Affects Results

| States | Typical Interpretation | Best For | Risk |
|--------|----------------------|----------|------|
| 2 | Bull vs Bear | Simple risk-on/risk-off classification. Clear signal, easy to act on. | May miss important nuances like transition periods or volatility-without-direction. |
| 3 | Bull / Transition / Stress | Most balanced choice. Captures the key market phases without overcomplicating. | Transition state can sometimes be unstable across folds if the boundary between regimes is gradual. |
| 4 | Low Vol Bull / High Vol Bull / Mild Stress / Crash | Finer distinctions within bull and bear phases. Useful for strategies that differentiate between calm uptrends and volatile rallies. | Requires more data to reliably estimate 4 distinct states. Some states may merge or become sparse. |
| 5-6 | Highly granular regime decomposition | Research and exploration. Academic analysis of market microstructure. | High risk of overfitting. States may not be stable or interpretable. Not recommended for production use. |

---

## 3. Walk-Forward Validation Setup

Walk-forward validation is the methodology that makes this app more than a curve-fitting exercise. It simulates how the model would have performed if deployed in real time, by repeatedly fitting on past data and testing on unseen future data.

### 3.1 Why Walk-Forward Validation Matters

A model that fits historical data well may simply be memorizing patterns rather than learning generalizable regime structure. Walk-forward validation addresses this by:

- Never allowing the model to see future data during training
- Fitting scaling/normalization only on each training window
- Producing multiple out-of-sample test periods that can be compared for consistency
- Revealing whether detected regimes are stable properties of the market or artifacts of a particular time period

### 3.2 Parameters

| Parameter | Default | Range | What It Does | Increasing | Decreasing |
|-----------|---------|-------|--------------|-----------|------------|
| **Window Mode** | Expanding | Expanding / Rolling | Determines how the training window grows over time. | **Expanding**: The training window starts at a fixed point and grows each step. More training data over time, which generally improves estimates but may dilute recent patterns with old data. | **Rolling**: The training window is a fixed size that slides forward. Always uses the most recent N days. Better for adapting to structural changes in the market but uses less data overall. |
| **Train Window (days)** | 504 | 100 - 5000 | Number of trading days in the training set for each fold. 504 days is approximately 2 years. | Longer training windows give the model more data to estimate parameters, producing more stable regimes. However, very long windows (e.g., 2000+ days) may include outdated market conditions that no longer apply. | Shorter windows (e.g., 252 = 1 year) make the model more adaptive to recent conditions but provide less data for estimation. Below 252 days, HMM parameter estimates become unreliable, especially with many features. |
| **Test Window (days)** | 63 | 10 - 504 | Number of trading days in the test set for each fold. 63 days is approximately one calendar quarter. | Longer test windows give more out-of-sample data per fold for evaluation but produce fewer total folds. A 252-day test window (1 year) gives robust per-fold statistics but may only yield 3-4 folds total. | Shorter test windows (e.g., 21 = 1 month) produce more folds for consistency checking but each fold has limited data for reliable per-regime statistics. |
| **Step Size (days)** | 63 | 1 - 252 | How far to advance the window between consecutive folds. Controls the overlap between test periods. | Larger step sizes (e.g., 126 = half year) produce fewer, non-overlapping folds. Faster to compute and each fold is independent. | Smaller step sizes (e.g., 21 = monthly) produce more folds with overlapping test periods. More data points for consistency analysis but folds are not fully independent. Step size of 1 gives maximum granularity but is very slow. |
| **Min Observations** | 252 | 50 - 1000 | Minimum number of data points required in the training window before a fold is included. Prevents fitting on insufficient data. | Higher minimums ensure each fold has enough data for reliable estimation. Set to at least `n_features * 20` as a rule of thumb. | Lower minimums allow folds with less training data. May produce unreliable regime assignments in early folds. |
| **Refit Every N Steps** | 1 | 1 - 20 | How often the model is re-estimated. A value of 1 means refit every fold (most rigorous). Higher values reuse the same model across multiple folds. | Higher values (e.g., 4) reuse the model for 4 consecutive test windows before refitting. Faster and shows how well a model persists, but misses adaptation to new data. | A value of 1 (default) refits every fold. Most computationally expensive but ensures the model always uses the latest available training data. Recommended for thorough analysis. |

### 3.3 Common Configurations

| Configuration | Train | Test | Step | Mode | Folds (7yr data) | Use Case |
|--------------|-------|------|------|------|---------|----------|
| **Quick exploration** | 504 | 63 | 126 | Expanding | ~10 | Fast first look. Good for testing parameter sensitivity. |
| **Standard analysis** | 504 | 63 | 63 | Expanding | ~20 | Balanced thoroughness and speed. Recommended default. |
| **High-resolution** | 504 | 21 | 21 | Expanding | ~60 | Many folds for consistency analysis. Slow but comprehensive. |
| **Adaptive** | 504 | 63 | 63 | Rolling | ~20 | Captures recent regime shifts. Better if market structure has changed significantly. |
| **Long-term stable** | 1008 | 126 | 126 | Expanding | ~8 | Uses 4 years of training data per fold. Very stable regime estimates but few folds. |

---

## 4. Practical Guidance

### 4.1 Starting Point

For a first run with daily data (e.g. SPY, QQQ, BTC-USD, or any liquid asset, 2018-2025):

- **Features**: Keep all defaults enabled
- **Model**: 3 states, full covariance, scaling on
- **Walk-Forward**: Expanding, 504/63/63

This produces approximately 20 folds with 3 interpretable regimes (Bull, Transition, Stress) and runs in under 2 minutes.

### 4.2 If Regimes Are Unstable Across Folds

The robustness summary shows "Regimes are unstable" when regime characteristics (mean return, volatility) vary significantly from fold to fold. To fix this:

1. **Reduce the number of states** from 3 to 2
2. **Reduce the number of features** — keep only log returns, volatility (20d), and drawdown
3. **Increase the training window** to 756 (3 years) or 1008 (4 years)
4. **Switch covariance type** from "full" to "diag" (fewer parameters to estimate)

### 4.3 If Regimes Are Not Distinct

The state separation score is low when regimes overlap in feature space. To improve separation:

1. **Add more volatility windows** — include 5, 10, 20, 30, 60
2. **Enable drawdown and rolling max drawdown** — these strongly differentiate stress from non-stress
3. **Try 2 states** instead of 3 — with fewer states, the model can find clearer boundaries
4. **Check if scaling is enabled** — without scaling, features on different scales can dominate and blur distinctions

### 4.4 If the Analysis Is Too Slow

1. **Increase step size** from 63 to 126 (halves the number of folds)
2. **Reduce features** — 5-7 well-chosen features are often enough
3. **Use a shorter date range** — 5 years instead of 15
4. **Set refit_every to 2-4** — reuses the model across multiple folds
5. **Switch covariance type** to "diag" (fewer parameters, faster fitting)

### 4.5 Feature Selection Strategy

A recommended minimal feature set for stable regime detection:

| Feature | Why |
|---------|-----|
| Log returns | Core directional signal |
| Rolling volatility (20d) | Standard regime separator |
| Drawdown | Loss severity distinguishes stress from pullback |
| Z-scored return | Context-adjusted extremity |
| Momentum (20d) | Trend persistence |

This 5-feature set typically produces stable 2-3 state models with clear economic interpretation.
