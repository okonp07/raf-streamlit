"""Regime evaluation metrics."""

import numpy as np
import pandas as pd


def _state_runs(states: list[int]) -> list[tuple[int, int, int, int]]:
    if not states:
        return []

    runs: list[tuple[int, int, int, int]] = []
    current = int(states[0])
    start = 0
    for idx in range(1, len(states)):
        state = int(states[idx])
        if state != current:
            runs.append((current, start, idx - 1, idx - start))
            current = state
            start = idx
    runs.append((current, start, len(states) - 1, len(states) - start))
    return runs


def smooth_state_sequence(states: np.ndarray, min_duration: int = 1) -> np.ndarray:
    """Merge short regime runs into neighboring states to reduce visual flicker."""
    arr = np.array(states, dtype=int)
    if len(arr) == 0 or min_duration <= 1:
        return arr.copy()

    smoothed = arr.tolist()
    while True:
        runs = _state_runs(smoothed)
        changed = False

        for idx, (state, start, end, length) in enumerate(runs):
            if length >= min_duration:
                continue

            prev_run = runs[idx - 1] if idx > 0 else None
            next_run = runs[idx + 1] if idx + 1 < len(runs) else None
            prev_state = prev_run[0] if prev_run else None
            next_state = next_run[0] if next_run else None

            if prev_state == next_state and prev_state is not None:
                replacement = prev_state
            elif prev_state is None:
                replacement = next_state
            elif next_state is None:
                replacement = prev_state
            else:
                replacement = prev_state if prev_run[3] >= next_run[3] else next_state

            if replacement is not None and replacement != state:
                smoothed[start:end + 1] = [replacement] * length
                changed = True
                break

        if not changed:
            return np.array(smoothed, dtype=int)


def smooth_state_timeline(states: list[int | None], min_duration: int = 1) -> list[int | None]:
    """Apply state smoothing separately to each contiguous non-null block."""
    if min_duration <= 1:
        return list(states)

    smoothed = list(states)
    idx = 0
    while idx < len(smoothed):
        while idx < len(smoothed) and smoothed[idx] is None:
            idx += 1
        block_start = idx
        while idx < len(smoothed) and smoothed[idx] is not None:
            idx += 1
        block_end = idx

        if block_end > block_start:
            block = np.array(smoothed[block_start:block_end], dtype=int)
            smoothed[block_start:block_end] = smooth_state_sequence(block, min_duration).tolist()

    return smoothed


def average_regime_duration_timeline(states: list[int | None]) -> dict[int, float]:
    durations: dict[int, list[int]] = {}
    current = None
    count = 0

    for value in states:
        if value is None:
            if current is not None and count > 0:
                durations.setdefault(int(current), []).append(count)
            current = None
            count = 0
            continue

        state = int(value)
        if current is None:
            current = state
            count = 1
        elif state == current:
            count += 1
        else:
            durations.setdefault(int(current), []).append(count)
            current = state
            count = 1

    if current is not None and count > 0:
        durations.setdefault(int(current), []).append(count)

    return {
        state: round(float(np.mean(lengths)), 2)
        for state, lengths in durations.items()
        if lengths
    }


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


def forward_regime_diagnostics(
    close: list[float],
    timeline_states: list[int | None],
    labels: dict,
    horizons: tuple[int, ...] = (7, 14, 30),
    drawdown_horizon: int = 30,
    drawdown_threshold: float = -0.10,
) -> list[dict]:
    """Evaluate whether regimes separate cleanly on forward returns and risk."""
    prices = np.asarray(close, dtype=float)
    n = len(prices)
    if n == 0:
        return []

    valid_states = sorted({int(state) for state in timeline_states if state is not None})
    avg_durations = average_regime_duration_timeline(timeline_states)
    rows: list[dict] = []

    for state in valid_states:
        state_indices = [idx for idx, value in enumerate(timeline_states) if value == state]
        if not state_indices:
            continue

        row = {
            "state": state,
            "label": labels.get(state, labels.get(str(state), f"State {state}")),
            "count": len(state_indices),
            "avg_duration": avg_durations.get(state, 0.0),
        }

        for horizon in horizons:
            values = [
                (prices[idx + horizon] / prices[idx]) - 1.0
                for idx in state_indices
                if idx + horizon < n
            ]
            row[f"avg_fwd_return_{horizon}"] = round(float(np.mean(values)), 4) if values else None

        vol_values = []
        dd_values = []
        dd_hits = []
        for idx in state_indices:
            if idx + drawdown_horizon >= n:
                continue

            window = prices[idx:idx + drawdown_horizon + 1]
            log_returns = np.diff(np.log(window))
            if len(log_returns) > 1:
                vol_values.append(float(np.std(log_returns) * np.sqrt(252)))

            forward_path = (window[1:] / window[0]) - 1.0
            if len(forward_path) > 0:
                max_dd = float(np.min(forward_path))
                dd_values.append(max_dd)
                dd_hits.append(1.0 if max_dd <= drawdown_threshold else 0.0)

        row["avg_forward_realized_vol_30d"] = round(float(np.mean(vol_values)), 4) if vol_values else None
        row["avg_forward_max_drawdown_30d"] = round(float(np.mean(dd_values)), 4) if dd_values else None
        row["drawdown_hit_rate_30d"] = round(float(np.mean(dd_hits)), 4) if dd_hits else None
        rows.append(row)

    return rows


def summarize_forward_validation(diagnostics: list[dict]) -> str:
    """Summarize whether forward regime separation looks economically sensible."""
    if not diagnostics:
        return "Forward validation is unavailable because there were not enough scored dates."

    bull = next((row for row in diagnostics if "bull" in row["label"].lower()), None)
    bear = next((row for row in diagnostics if "bear" in row["label"].lower()), None)
    if not bull or not bear:
        return "Forward validation is partially available, but the regimes do not map neatly onto bull and bear buckets."

    bull_ret = bull.get("avg_fwd_return_30")
    bear_ret = bear.get("avg_fwd_return_30")
    bull_dd = bull.get("drawdown_hit_rate_30d")
    bear_dd = bear.get("drawdown_hit_rate_30d")
    bull_vol = bull.get("avg_forward_realized_vol_30d")
    bear_vol = bear.get("avg_forward_realized_vol_30d")
    drift_note = (
        " On strong upward-drift assets, even the bear regime can still average a positive forward return; the useful split is relative return strength, volatility, and drawdown risk."
        if bull_ret is not None and bear_ret is not None and bull_ret > 0 and bear_ret > 0
        else ""
    )

    if None in {bull_ret, bear_ret, bull_dd, bear_dd, bull_vol, bear_vol}:
        return "Forward validation is partially available, but some forward windows are too short to score every regime cleanly."

    if bull_ret > bear_ret and bull_dd < bear_dd and bull_vol < bear_vol:
        return (
            "Forward validation looks directionally sensible: the bull regime leads to stronger returns with lower forward risk than the bear regime."
            f"{drift_note}"
        )
    if bull_ret > bear_ret and bull_dd < bear_dd:
        return (
            "Forward validation is promising, but the volatility split is not yet as clean as the return and drawdown split."
            f"{drift_note}"
        )
    return (
        "Forward validation is mixed. The overlay may still be overreacting locally, so inspect the smoothing setting and the regime definitions before trusting it."
        f"{drift_note}"
    )
