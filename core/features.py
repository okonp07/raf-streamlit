"""Feature engineering pipeline — no look-ahead leakage."""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler


def engineer_features(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    out = df.copy()
    close = out["Close"]
    log_ret = np.log(close / close.shift(1))

    if config.get("log_returns", True):
        out["log_return"] = log_ret
    if config.get("simple_returns", True):
        out["simple_return"] = close.pct_change()

    for w in config.get("volatility_windows", [5, 10, 20]):
        out[f"volatility_{w}"] = log_ret.rolling(w, min_periods=w).std()

    for w in config.get("rolling_mean_windows", [5, 20]):
        out[f"rolling_mean_{w}"] = log_ret.rolling(w, min_periods=w).mean()

    if config.get("drawdown", True):
        cummax = close.cummax()
        out["drawdown"] = (close - cummax) / cummax

    if config.get("rolling_max_drawdown", True):
        dd = (close - close.cummax()) / close.cummax()
        out["rolling_max_dd_20"] = dd.rolling(20, min_periods=20).min()

    if config.get("atr_range", True):
        out["atr_range"] = (out["High"] - out["Low"]) / close

    if config.get("volume_change", True):
        out["volume_change"] = out["Volume"].pct_change()

    if config.get("z_scored_return", True):
        rm = log_ret.rolling(20, min_periods=20).mean()
        rs = log_ret.rolling(20, min_periods=20).std()
        out["z_return"] = (log_ret - rm) / rs.replace(0, np.nan)

    for w in config.get("momentum_windows", [10, 20]):
        out[f"momentum_{w}"] = close / close.shift(w) - 1

    if config.get("realized_vol", True):
        out["realized_vol_20"] = np.sqrt((log_ret**2).rolling(20, min_periods=20).sum())

    if config.get("rsi", True):
        delta = close.diff()
        gain = delta.clip(lower=0).rolling(14, min_periods=14).mean()
        loss = (-delta.clip(upper=0)).rolling(14, min_periods=14).mean()
        rs = gain / loss.replace(0, np.nan)
        out["rsi_14"] = 100 - (100 / (1 + rs))

    if config.get("macd", True):
        ema12 = close.ewm(span=12, adjust=False).mean()
        ema26 = close.ewm(span=26, adjust=False).mean()
        macd_line = ema12 - ema26
        out["macd_signal"] = macd_line - macd_line.ewm(span=9, adjust=False).mean()

    if config.get("rolling_skew", True):
        out["rolling_skew_20"] = log_ret.rolling(20, min_periods=20).skew()
    if config.get("rolling_kurtosis", True):
        out["rolling_kurtosis_20"] = log_ret.rolling(20, min_periods=20).kurt()

    out = out.dropna()
    return out


def get_feature_columns(df: pd.DataFrame) -> list[str]:
    ohlcv = {"Open", "High", "Low", "Close", "Volume", "Date"}
    return [c for c in df.columns if c not in ohlcv]


def fit_scaler(train: np.ndarray) -> StandardScaler:
    return StandardScaler().fit(train)
