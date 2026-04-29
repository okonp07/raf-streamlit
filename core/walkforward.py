"""Walk-forward validation engine."""

import time

import numpy as np
import pandas as pd

from core.features import fit_scaler, get_feature_columns
from core.metrics import (
    forward_regime_diagnostics,
    per_regime_stats,
    regime_persistence,
    robustness_summary,
    smooth_state_sequence,
    smooth_state_timeline,
    state_occupancy,
    state_separation_score,
    summarize_forward_validation,
)
from core.models import (
    canonical_order_from_profiles,
    fit_hmm,
    interpret_regimes,
    labels_from_profiles,
    summarize_state_profiles,
)
from core.phases import PHASE_DESCRIPTIONS, infer_market_phases


def generate_folds(
    n_samples: int,
    train_window: int,
    test_window: int,
    step_size: int,
    mode: str,
    min_obs: int,
) -> list[tuple]:
    folds = []
    cursor = 0
    while True:
        train_start = 0 if mode == "expanding" else max(0, cursor)
        train_end = cursor + train_window
        test_start = train_end
        test_end = test_start + test_window
        if test_end > n_samples:
            break
        if (train_end - train_start) < min_obs:
            cursor += step_size
            continue
        folds.append((train_start, train_end, test_start, test_end))
        cursor += step_size
    return folds


def _canonicalize_states(
    train_states: np.ndarray,
    test_states: np.ndarray,
    transmat: list[list[float]],
    train_returns: np.ndarray,
    n_states: int,
) -> tuple[np.ndarray, np.ndarray, list[list[float]]]:
    profiles = summarize_state_profiles(train_returns, train_states, n_states)
    order = canonical_order_from_profiles(profiles)
    remap = np.empty(n_states, dtype=int)
    for new_id, old_id in enumerate(order):
        remap[old_id] = new_id

    canonical_train = remap[train_states]
    canonical_test = remap[test_states]
    canonical_transmat = np.array(transmat)[order, :][:, order].tolist()
    return canonical_train, canonical_test, canonical_transmat


def run_walkforward(
    featured_df: pd.DataFrame,
    model_config: dict,
    wf_config: dict,
    progress_bar=None,
) -> dict:
    t0 = time.time()
    feature_cols = get_feature_columns(featured_df)
    if model_config.get("feature_subset"):
        feature_cols = [c for c in model_config["feature_subset"] if c in feature_cols]
    if not feature_cols:
        raise ValueError("No active features available for modelling.")

    feature_matrix = featured_df[feature_cols].values
    dates = featured_df.index
    log_ret = (
        featured_df["log_return"].values
        if "log_return" in featured_df.columns
        else np.zeros(len(featured_df))
    )
    close = (
        featured_df["Close"].values
        if "Close" in featured_df.columns
        else np.zeros(len(featured_df))
    )
    n_states = model_config.get("n_states", 3)
    min_regime_duration = int(model_config.get("min_regime_duration", 5))

    folds_idx = generate_folds(
        len(feature_matrix),
        wf_config.get("train_window", 504),
        wf_config.get("test_window", 63),
        wf_config.get("step_size", 63),
        wf_config.get("mode", "expanding"),
        wf_config.get("min_observations", 252),
    )
    if not folds_idx:
        raise ValueError("No valid folds. Try reducing window sizes.")

    fold_results = []
    oos_state_by_date: dict[str, int] = {}
    oos_return_by_date: dict[str, float] = {}

    for i, (tr_s, tr_e, te_s, te_e) in enumerate(folds_idx):
        if progress_bar:
            progress_bar.progress(
                (i + 1) / len(folds_idx),
                text=f"Fold {i + 1}/{len(folds_idx)}",
            )

        train_X = feature_matrix[tr_s:tr_e]
        test_X = feature_matrix[te_s:te_e]
        train_ret = log_ret[tr_s:tr_e]
        test_ret = log_ret[te_s:te_e]

        if model_config.get("scaling", True):
            scaler = fit_scaler(train_X)
            train_X_s = scaler.transform(train_X)
            test_X_s = scaler.transform(test_X)
        else:
            train_X_s, test_X_s = train_X, test_X

        try:
            result = fit_hmm(
                train_X_s,
                test_X_s,
                n_states=n_states,
                covariance_type=model_config.get("covariance_type", "diag"),
                n_iter=model_config.get("n_iter", 200),
                tol=model_config.get("tol", 1e-4),
                random_seed=model_config.get("random_seed", 42),
            )
        except Exception:
            continue

        train_states, test_states, transmat = _canonicalize_states(
            result["train_states"],
            result["test_states"],
            result["transmat"],
            train_ret,
            n_states,
        )
        if min_regime_duration > 1:
            smoothed_test_states = smooth_state_sequence(test_states, min_regime_duration)
        else:
            smoothed_test_states = test_states.copy()

        labels = interpret_regimes(train_ret, train_states, n_states)
        test_dates = [str(d.date()) for d in dates[te_s:te_e]]
        warnings = []
        smoothed_points = int(np.sum(smoothed_test_states != test_states))
        if smoothed_points:
            warnings.append(
                f"Minimum regime duration smoothing merged {smoothed_points} short-run assignments using a {min_regime_duration}-step threshold."
            )

        overlapping_dates = 0
        for dt, state, ret in zip(test_dates, smoothed_test_states, test_ret):
            if dt in oos_state_by_date:
                overlapping_dates += 1
                continue
            oos_state_by_date[dt] = int(state)
            oos_return_by_date[dt] = float(ret)
        if overlapping_dates:
            warnings.append(
                "Overlapping test windows detected. Overview charts retain the earliest out-of-sample state per date."
            )

        fold_results.append(
            {
                "fold_id": i,
                "train_start": str(dates[tr_s].date()),
                "train_end": str(dates[tr_e - 1].date()),
                "test_start": str(dates[te_s].date()),
                "test_end": str(dates[te_e - 1].date()),
                "train_states": train_states.tolist(),
                "test_states": smoothed_test_states.tolist(),
                "train_dates": [str(d.date()) for d in dates[tr_s:tr_e]],
                "test_dates": test_dates,
                "regime_labels": labels,
                "transition_matrix": transmat,
                "train_occupancy": state_occupancy(train_states, n_states),
                "test_occupancy": state_occupancy(smoothed_test_states, n_states),
                "train_persistence": regime_persistence(train_states),
                "test_persistence": regime_persistence(smoothed_test_states),
                "regime_stats": per_regime_stats(train_ret, train_states, n_states),
                "test_regime_stats": per_regime_stats(test_ret, smoothed_test_states, n_states),
                "state_separation": state_separation_score(train_X_s, train_states, n_states),
                "log_likelihood": result["log_likelihood"],
                "aic": result["aic"],
                "bic": result["bic"],
                "warnings": warnings,
            }
        )

    if not fold_results:
        raise ValueError(
            "All walk-forward folds failed. Try fewer states, fewer features, or a longer price history."
        )

    duration = round(time.time() - t0, 2)
    robust = robustness_summary(fold_results, n_states)
    global_profiles = []
    for state_id in range(n_states):
        counts = []
        mean_parts = []
        vol_parts = []
        for fold in fold_results:
            for stat in fold["test_regime_stats"]:
                if stat["state"] == state_id and stat.get("count", 0) > 0:
                    counts.append(stat["count"])
                    mean_parts.append(stat["mean_return"])
                    vol_parts.append(stat["std_return"])
        total_count = int(sum(counts))
        weighted_mean = (
            float(np.average(mean_parts, weights=counts))
            if counts
            else 0.0
        )
        weighted_vol = (
            float(np.average(vol_parts, weights=counts))
            if counts
            else np.inf
        )
        global_profiles.append(
            {
                "state": state_id,
                "count": total_count,
                "mean": weighted_mean,
                "vol": weighted_vol,
            }
        )
    global_labels = labels_from_profiles(global_profiles)

    timeline_dates = [str(d.date()) for d in dates]
    timeline_close = close.tolist()
    timeline_states = [oos_state_by_date.get(dt) for dt in timeline_dates]
    timeline_states = smooth_state_timeline(timeline_states, min_regime_duration)
    timeline_phases = infer_market_phases(
        timeline_dates,
        timeline_close,
        timeline_states,
        global_labels,
    )
    oos_dates = [dt for dt in timeline_dates if dt in oos_state_by_date]
    oos_states = [state for state in timeline_states if state is not None]
    oos_returns = [oos_return_by_date[dt] for dt in oos_dates]
    oos_close = [px for dt, px in zip(timeline_dates, timeline_close) if dt in oos_state_by_date]
    oos_phases = [phase for phase in timeline_phases if phase is not None]
    coverage_pct = round((len(oos_dates) / len(timeline_dates)) * 100, 2) if timeline_dates else 0.0
    forward_validation = forward_regime_diagnostics(
        timeline_close,
        timeline_states,
        global_labels,
    )
    forward_validation_interpretation = summarize_forward_validation(forward_validation)

    return {
        "n_folds": len(fold_results),
        "n_states": n_states,
        "duration_secs": duration,
        "folds": fold_results,
        "robustness": robust,
        "forward_validation": forward_validation,
        "forward_validation_interpretation": forward_validation_interpretation,
        "regime_labels": global_labels,
        "phase_descriptions": PHASE_DESCRIPTIONS,
        "timeline_dates": timeline_dates,
        "timeline_close": timeline_close,
        "timeline_states": timeline_states,
        "timeline_phases": timeline_phases,
        "oos_dates": oos_dates,
        "oos_states": oos_states,
        "oos_close": oos_close,
        "oos_returns": oos_returns,
        "oos_phases": oos_phases,
        "coverage_pct": coverage_pct,
        "overlay_note": (
            "Colored segments show out-of-sample walk-forward predictions. "
            "Muted price segments provide historical context for dates that were not scored."
        ),
        "smoothing_note": (
            f"Displayed regimes use a minimum-duration smoothing threshold of {min_regime_duration} modeled steps."
            if min_regime_duration > 1
            else "Displayed regimes are unsmoothed."
        ),
        "phase_note": (
            "Market phases are derived from the HMM regime plus trailing drawdown and momentum context. "
            "They are intended to line up more closely with intuitive cycle language without using future data."
        ),
    }
