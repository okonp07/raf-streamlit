"""Regime evaluation metrics."""

import numpy as np
import pandas as pd


def state_occupancy(states: np.ndarray, n_states: int) -> dict[int, float]:
    counts = np.bincount(states.astype(int), minlength=n_states)
    return {int(s): round(float(counts[s]) / len(states), 4) for s in range(n_states)}


def average_regime_duration(states: np.ndarray, n_states: int) -> dict[int, float]:
    durations: dict[int, list[int]] = {s: [] for s in range(n_states)}
    current, count = int(states[0]), 1
    for s in states[1:]:
        s = int(s)
        if s == current:
            count += 1
        else:
            durations[current].append(count)
            current, count = s, 1
    durations[current].append(count)
    return {s: round(float(np.mean(d)), 2) if d else 0.0 for s, d in durations.items()}


def regime_persistence(states: np.ndarray) -> float:
    if len(states) < 2:
        return 1.0
    return round(float(np.sum(states[1:] == states[:-1])) / (len(states) - 1), 4)


def per_regime_stats(returns: np.ndarray, states: np.ndarray, n_states: int) -> list[dict]:
    results = []
    for s in range(n_states):
        r = returns[states == s]
        if len(r) == 0:
            results.append({"state": s, "count": 0})
            continue
        cum = np.cumsum(r)
        running_max = np.maximum.accumulate(cum)
        dd = cum - running_max
        results.append({
            "state": s,
            "count": int(len(r)),
            "mean_return": round(float(np.mean(r)), 6),
            "std_return": round(float(np.std(r)), 6),
            "sharpe": round(float(np.mean(r) / np.std(r) * np.sqrt(252)) if np.std(r) > 0 else 0, 4),
            "max_drawdown": round(float(np.min(dd)), 6),
            "positive_pct": round(float(np.mean(r > 0)), 4),
        })
    return results


def state_separation_score(features: np.ndarray, states: np.ndarray, n_states: int) -> float:
    if features.ndim == 1:
        features = features.reshape(-1, 1)
    grand_mean = features.mean(axis=0)
    between, within = 0.0, 0.0
    for s in range(n_states):
        mask = states == s
        if mask.sum() < 2:
            continue
        cluster = features[mask]
        centroid = cluster.mean(axis=0)
        between += mask.sum() * np.sum((centroid - grand_mean) ** 2)
        within += np.sum((cluster - centroid) ** 2)
    return round(float(between / within) if within > 0 else 0.0, 4)


def robustness_summary(fold_results: list[dict], n_states: int) -> dict:
    per_state_means: dict[int, list] = {s: [] for s in range(n_states)}
    per_state_vols: dict[int, list] = {s: [] for s in range(n_states)}
    for fold in fold_results:
        for stat in fold.get("regime_stats", []):
            s = stat["state"]
            if stat.get("count", 0) > 0:
                per_state_means[s].append(stat.get("mean_return", 0))
                per_state_vols[s].append(stat.get("std_return", 0))

    consistency = {}
    for s in range(n_states):
        means, vols = per_state_means[s], per_state_vols[s]
        consistency[s] = {
            "mean_return_cv": round(float(np.std(means) / np.abs(np.mean(means))) if means and np.mean(means) != 0 else 999, 4),
            "vol_cv": round(float(np.std(vols) / np.mean(vols)) if vols and np.mean(vols) > 0 else 999, 4),
            "n_folds_present": len(means),
        }

    stable = sum(1 for s in range(n_states) if consistency[s]["mean_return_cv"] < 2.0 and consistency[s]["vol_cv"] < 1.0)
    persistences = [f.get("test_persistence", 0) for f in fold_results]
    avg_p = float(np.mean(persistences)) if persistences else 0

    lines = []
    if stable / n_states >= 0.8:
        lines.append("Regimes are stable across folds.")
    elif stable / n_states >= 0.5:
        lines.append("Some regimes are stable; others vary across folds.")
    else:
        lines.append("Regimes are unstable — consider fewer states.")
    if avg_p > 0.9:
        lines.append("High persistence suggests meaningful state structure.")
    elif avg_p > 0.7:
        lines.append("Moderate persistence.")
    else:
        lines.append("Low persistence — assignments may be noisy.")

    return {
        "n_folds": len(fold_results),
        "n_states": n_states,
        "stable_regimes": stable,
        "regime_consistency": consistency,
        "avg_test_persistence": round(avg_p, 4),
        "interpretation": " ".join(lines),
    }
