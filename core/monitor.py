"""Live regime monitoring — probabilities, alerts, and forward projection."""

import numpy as np
import pandas as pd
from hmmlearn.hmm import GaussianHMM

from core.features import engineer_features, get_feature_columns, fit_scaler
from core.metrics import average_regime_duration, smooth_state_sequence
from core.models import (
    canonical_order_from_profiles,
    interpret_regimes,
    summarize_state_profiles,
)
from core.phases import PHASE_DESCRIPTIONS, infer_market_phases, summarize_current_phase


def _canonicalize_monitor_states(
    states: np.ndarray,
    probabilities: np.ndarray,
    transmat: np.ndarray,
    returns: np.ndarray,
    n_states: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    profiles = summarize_state_profiles(returns, states, n_states)
    order = canonical_order_from_profiles(profiles)
    remap = np.empty(n_states, dtype=int)
    for new_id, old_id in enumerate(order):
        remap[old_id] = new_id

    canonical_states = remap[states]
    canonical_probabilities = probabilities[:, order]
    canonical_transmat = transmat[order, :][:, order]
    return canonical_states, canonical_probabilities, canonical_transmat


def summarize_current_regime(
    dates: list[str],
    states: list[int],
    probabilities: list[list[float]],
    transmat: list[list[float]],
    labels: dict,
) -> dict:
    date_index = pd.to_datetime(dates)
    states_arr = np.array(states, dtype=int)
    probs_arr = np.array(probabilities)
    transmat_arr = np.array(transmat)

    current_state = int(states_arr[-1])
    current_label = labels.get(current_state, labels.get(str(current_state), f"State {current_state}"))
    current_confidence = float(probs_arr[-1, current_state])

    run_length = 1
    for idx in range(len(states_arr) - 2, -1, -1):
        if states_arr[idx] != current_state:
            break
        run_length += 1

    run_start_date = date_index[-run_length]
    durations = average_regime_duration(states_arr, len(transmat_arr))
    observed_average = float(durations.get(current_state, 0.0))
    self_transition = float(transmat_arr[current_state, current_state])
    expected_total = (
        float(1.0 / max(1e-6, (1.0 - self_transition)))
        if self_transition < 0.999999
        else float(run_length)
    )
    blended_total = max(run_length, round((observed_average + expected_total) / 2, 1))
    remaining_steps = max(0.0, blended_total - run_length)
    progress_ratio = min(1.0, run_length / blended_total) if blended_total > 0 else 0.0

    if len(date_index) >= 2:
        median_step_days = max(
            1,
            int(round(np.median(np.diff(date_index.values).astype("timedelta64[D]").astype(int)))),
        )
    else:
        median_step_days = 1

    likely_end_date = (date_index[-1] + pd.Timedelta(days=int(round(remaining_steps * median_step_days)))).date()
    probability_end_10 = 1.0 - (self_transition ** 10)
    probability_end_20 = 1.0 - (self_transition ** 20)
    probability_end_30 = 1.0 - (self_transition ** 30)

    return {
        "current_state": current_state,
        "current_label": current_label,
        "current_confidence": current_confidence,
        "current_run_length": int(run_length),
        "current_run_start": str(run_start_date.date()),
        "observed_average_duration": round(observed_average, 1),
        "expected_total_duration": round(expected_total, 1),
        "blended_total_duration": round(blended_total, 1),
        "estimated_remaining_steps": round(remaining_steps, 1),
        "progress_ratio": round(progress_ratio, 4),
        "likely_end_date": str(likely_end_date),
        "self_transition": round(self_transition, 4),
        "probability_end_10": round(probability_end_10, 4),
        "probability_end_20": round(probability_end_20, 4),
        "probability_end_30": round(probability_end_30, 4),
    }


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
    min_regime_duration = int(model_config.get("min_regime_duration", 5))

    if model_config.get("scaling", True):
        scaler = fit_scaler(X)
        X_scaled = scaler.transform(X)
    else:
        scaler = None
        X_scaled = X

    model = GaussianHMM(
        n_components=n_states,
        covariance_type=model_config.get("covariance_type", "diag"),
        n_iter=model_config.get("n_iter", 200),
        tol=model_config.get("tol", 1e-4),
        random_state=model_config.get("random_seed", 42),
    )
    model.fit(X_scaled)

    states = model.predict(X_scaled)
    probabilities = model.predict_proba(X_scaled)
    states, probabilities, canonical_transmat = _canonicalize_monitor_states(
        states,
        probabilities,
        model.transmat_,
        log_ret,
        n_states,
    )
    states = smooth_state_sequence(states, min_regime_duration) if min_regime_duration > 1 else states
    labels = interpret_regimes(log_ret, states, n_states)
    summary = summarize_current_regime(
        [str(d.date()) for d in dates],
        states.tolist(),
        probabilities.tolist(),
        canonical_transmat.tolist(),
        labels,
    )
    phases = infer_market_phases(
        [str(d.date()) for d in dates],
        close.tolist(),
        states.tolist(),
        labels,
    )
    phase_summary = summarize_current_phase(
        [str(d.date()) for d in dates],
        phases,
    )

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
        "phases": phases,
        "phase_descriptions": PHASE_DESCRIPTIONS,
        "n_states": n_states,
        "transmat": canonical_transmat.tolist(),
        "summary": summary,
        "phase_summary": phase_summary,
        "phase_note": (
            "Market phases are derived from the HMM regime plus trailing drawdown and momentum context, "
            "so they align better with intuitive cycle language without peeking into the future."
        ),
        "smoothing_note": (
            f"Displayed regimes use a minimum-duration smoothing threshold of {min_regime_duration} modeled steps."
            if min_regime_duration > 1
            else "Displayed regimes are unsmoothed."
        ),
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
