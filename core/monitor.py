"""Live regime monitoring — probabilities, alerts, and forward projection."""

import numpy as np
import pandas as pd
from hmmlearn.hmm import GaussianHMM

from core.features import engineer_features, get_feature_columns, fit_scaler
from core.models import interpret_regimes


def train_full_model(
    df: pd.DataFrame,
    feature_config: dict,
    model_config: dict,
) -> dict:
    """Train a single HMM on all available data and return monitoring state."""
    featured = engineer_features(df, feature_config)
    feature_cols = get_feature_columns(featured)
    X = featured[feature_cols].values
    dates = featured.index
    log_ret = featured["log_return"].values if "log_return" in featured.columns else np.zeros(len(featured))
    close = featured["Close"].values if "Close" in featured.columns else np.zeros(len(featured))
    n_states = model_config.get("n_states", 3)

    if model_config.get("scaling", True):
        scaler = fit_scaler(X)
        X_scaled = scaler.transform(X)
    else:
        scaler = None
        X_scaled = X

    model = GaussianHMM(
        n_components=n_states,
        covariance_type=model_config.get("covariance_type", "full"),
        n_iter=model_config.get("n_iter", 200),
        tol=model_config.get("tol", 1e-4),
        random_state=model_config.get("random_seed", 42),
    )
    model.fit(X_scaled)

    states = model.predict(X_scaled)
    probabilities = model.predict_proba(X_scaled)
    labels = interpret_regimes(log_ret, states, n_states)

    return {
        "model": model,
        "scaler": scaler,
        "feature_cols": feature_cols,
        "dates": [str(d.date()) for d in dates],
        "close": close.tolist(),
        "log_return": log_ret.tolist(),
        "states": states.tolist(),
        "probabilities": probabilities.tolist(),
        "labels": labels,
        "n_states": n_states,
        "transmat": model.transmat_.tolist(),
    }


def detect_alerts(
    probabilities: list,
    states: list,
    dates: list,
    labels: dict,
    alert_threshold: float = 0.6,
    lookback: int = 5,
) -> list[dict]:
    """Detect regime transition alerts where current regime confidence drops."""
    probs = np.array(probabilities)
    alerts = []
    for i in range(lookback, len(states)):
        current_state = states[i]
        current_prob = probs[i, current_state]

        if current_prob < alert_threshold:
            # Find the most likely alternative state
            alt_probs = probs[i].copy()
            alt_probs[current_state] = 0
            alt_state = int(np.argmax(alt_probs))
            alt_prob = float(alt_probs[alt_state])

            # Check if this is a trend (probability declining over lookback)
            recent_probs = [probs[j, current_state] for j in range(i - lookback, i + 1)]
            declining = recent_probs[-1] < recent_probs[0]

            alerts.append({
                "date": dates[i],
                "current_regime": labels.get(current_state, labels.get(str(current_state), f"State {current_state}")),
                "confidence": float(current_prob),
                "alternative_regime": labels.get(alt_state, labels.get(str(alt_state), f"State {alt_state}")),
                "alt_probability": alt_prob,
                "declining": declining,
                "severity": "High" if current_prob < 0.4 else "Medium" if current_prob < 0.5 else "Low",
            })
    return alerts


def project_forward(
    transmat: list,
    current_probs: list,
    labels: dict,
    n_days: int = 30,
) -> pd.DataFrame:
    """Project regime probabilities N days forward using the transition matrix."""
    T = np.array(transmat)
    p = np.array(current_probs)
    rows = [{"day": 0, **{labels.get(i, labels.get(str(i), f"State {i}")): float(p[i]) for i in range(len(p))}}]

    for d in range(1, n_days + 1):
        p = p @ T
        rows.append({"day": d, **{labels.get(i, labels.get(str(i), f"State {i}")): float(p[i]) for i in range(len(p))}})

    return pd.DataFrame(rows)
