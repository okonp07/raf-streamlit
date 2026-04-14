"""Walk-forward validation engine."""

import time
import numpy as np
import pandas as pd
import streamlit as st

from core.features import get_feature_columns, fit_scaler
from core.models import fit_hmm, interpret_regimes
from core.metrics import (
    state_occupancy, regime_persistence, per_regime_stats,
    state_separation_score, robustness_summary,
)


def generate_folds(n_samples: int, train_window: int, test_window: int,
                   step_size: int, mode: str, min_obs: int) -> list[tuple]:
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

    feature_matrix = featured_df[feature_cols].values
    dates = featured_df.index
    log_ret = featured_df["log_return"].values if "log_return" in featured_df.columns else np.zeros(len(featured_df))
    close = featured_df["Close"].values if "Close" in featured_df.columns else None
    n_states = model_config.get("n_states", 3)

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
    all_test_states = []
    all_test_dates = []
    refit_every = wf_config.get("refit_every", 1)

    for i, (tr_s, tr_e, te_s, te_e) in enumerate(folds_idx):
        if progress_bar:
            progress_bar.progress((i + 1) / len(folds_idx), text=f"Fold {i+1}/{len(folds_idx)}")

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
                train_X_s, test_X_s,
                n_states=n_states,
                covariance_type=model_config.get("covariance_type", "full"),
                n_iter=model_config.get("n_iter", 200),
                tol=model_config.get("tol", 1e-4),
                random_seed=model_config.get("random_seed", 42),
            )
        except Exception as e:
            continue

        train_states = result["train_states"]
        test_states = result["test_states"]
        labels = interpret_regimes(train_ret, train_states, n_states)

        fold_results.append({
            "fold_id": i,
            "train_start": str(dates[tr_s].date()),
            "train_end": str(dates[tr_e - 1].date()),
            "test_start": str(dates[te_s].date()),
            "test_end": str(dates[te_e - 1].date()),
            "train_states": train_states.tolist(),
            "test_states": test_states.tolist(),
            "train_dates": [str(d.date()) for d in dates[tr_s:tr_e]],
            "test_dates": [str(d.date()) for d in dates[te_s:te_e]],
            "regime_labels": labels,
            "transition_matrix": result["transmat"],
            "train_occupancy": state_occupancy(train_states, n_states),
            "test_occupancy": state_occupancy(test_states, n_states),
            "train_persistence": regime_persistence(train_states),
            "test_persistence": regime_persistence(test_states),
            "regime_stats": per_regime_stats(train_ret, train_states, n_states),
            "test_regime_stats": per_regime_stats(test_ret, test_states, n_states),
            "state_separation": state_separation_score(train_X_s, train_states, n_states),
            "log_likelihood": result["log_likelihood"],
            "aic": result["aic"],
            "bic": result["bic"],
        })

        all_test_states.extend(test_states.tolist())
        all_test_dates.extend([str(d.date()) for d in dates[te_s:te_e]])

    duration = round(time.time() - t0, 2)
    robust = robustness_summary(fold_results, n_states)
    global_labels = fold_results[-1]["regime_labels"] if fold_results else {}

    # Build chart data
    test_close = close[folds_idx[0][2]:folds_idx[-1][3]].tolist() if close is not None else []
    test_returns = log_ret[folds_idx[0][2]:folds_idx[-1][3]].tolist()

    return {
        "n_folds": len(fold_results),
        "n_states": n_states,
        "duration_secs": duration,
        "folds": fold_results,
        "robustness": robust,
        "regime_labels": global_labels,
        "all_test_dates": all_test_dates,
        "all_test_states": all_test_states,
        "test_close": test_close,
        "test_returns": test_returns,
    }
