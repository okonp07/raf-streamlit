"""Model-driven market phase inference layered on top of HMM regimes."""

from __future__ import annotations

import numpy as np
import pandas as pd


PHASE_DESCRIPTIONS = {
    "Capitulation": "Forced selling or panic conditions near local lows, usually while the model is in a stress regime.",
    "Repair": "Recovery off the lows while trend damage is still being repaired and the model has not yet settled into a stable bull regime.",
    "Bull Expansion": "A healthier upside phase with supportive momentum, shallow drawdowns, and a more constructive underlying regime.",
    "Distribution": "A weakening or choppy phase where upside leadership fades and the market is vulnerable to either renewed repair or deeper stress.",
}

PHASE_ORDER = list(PHASE_DESCRIPTIONS.keys())


def _resolve_regime_label(labels: dict, state: int | None) -> str | None:
    if state is None:
        return None
    return labels.get(state, labels.get(str(state), f"State {state}"))


def _regime_bucket(label: str | None) -> str | None:
    if label is None:
        return None
    lower = label.lower()
    if "stress" in lower:
        return "stress"
    if lower.startswith("bull") or "low vol" in lower:
        return "bull"
    return "transition"


def infer_market_phases(
    dates: list[str],
    close: list[float],
    states: list[int | None],
    regime_labels: dict,
) -> list[str | None]:
    """Infer intuitive market phases without using future information."""
    if not dates or not close:
        return []

    n = min(len(dates), len(close), len(states) if states else len(close))
    idx = pd.to_datetime(dates[:n])
    price = pd.Series(np.asarray(close[:n], dtype=float), index=idx)
    state_list = list(states[:n]) if states else [None] * n

    ma20 = price.rolling(20, min_periods=1).mean()
    ma50 = price.rolling(50, min_periods=1).mean()
    ret10 = price.pct_change(10).fillna(0.0)
    ret20 = price.pct_change(20).fillna(0.0)
    ret60 = price.pct_change(60).fillna(0.0)
    drawdown = price / price.cummax() - 1.0
    low21 = price.rolling(21, min_periods=1).min()
    low63 = price.rolling(63, min_periods=1).min()
    bounce21 = price / low21 - 1.0
    bounce63 = price / low63 - 1.0

    phases: list[str | None] = []
    for i, state in enumerate(state_list):
        if state is None:
            phases.append(None)
            continue

        regime_label = _resolve_regime_label(regime_labels, int(state))
        bucket = _regime_bucket(regime_label)

        dd = float(drawdown.iat[i])
        r10 = float(ret10.iat[i])
        r20 = float(ret20.iat[i])
        r60 = float(ret60.iat[i])
        near_low = float(bounce21.iat[i]) <= 0.035
        rebound = float(bounce21.iat[i]) >= 0.05
        strong_rebound = float(bounce63.iat[i]) >= 0.12
        above20 = float(price.iat[i]) >= float(ma20.iat[i])
        above50 = float(price.iat[i]) >= float(ma50.iat[i])
        severe_damage = dd <= -0.12 or r20 <= -0.06
        weakening = (not above20) or r20 <= -0.03 or dd <= -0.08
        improving = above20 and r10 > 0 and r20 > -0.02
        strong_trend = above50 and r60 >= 0.05 and dd >= -0.08
        prev_phase = next((phase for phase in reversed(phases) if phase is not None), None)

        if bucket == "stress":
            if severe_damage or near_low:
                phase = "Capitulation"
            elif prev_phase in {"Capitulation", "Repair"} and rebound:
                phase = "Repair"
            else:
                phase = "Distribution"
        elif bucket == "bull":
            if strong_trend and (strong_rebound or prev_phase in {"Repair", "Bull Expansion", None}):
                phase = "Bull Expansion"
            elif weakening:
                phase = "Distribution"
            elif prev_phase == "Capitulation" or rebound:
                phase = "Repair"
            else:
                phase = "Bull Expansion"
        else:
            if prev_phase == "Capitulation" and (rebound or improving):
                phase = "Repair"
            elif near_low and severe_damage:
                phase = "Capitulation"
            elif improving or rebound:
                phase = "Repair"
            else:
                phase = "Distribution"

        phases.append(phase)

    return smooth_phases(phases)


def phase_occupancy(phases: list[str | None]) -> dict[str, float]:
    valid = [phase for phase in phases if phase is not None]
    if not valid:
        return {}
    total = len(valid)
    return {
        phase: round(valid.count(phase) / total, 4)
        for phase in PHASE_ORDER
        if phase in valid
    }


def _phase_runs(phases: list[str]) -> list[tuple[str, int, int, int]]:
    if not phases:
        return []

    runs: list[tuple[str, int, int, int]] = []
    current = phases[0]
    start = 0
    for idx in range(1, len(phases)):
        if phases[idx] != current:
            runs.append((current, start, idx - 1, idx - start))
            current = phases[idx]
            start = idx
    runs.append((current, start, len(phases) - 1, len(phases) - start))
    return runs


def _smooth_phase_block(phases: list[str], min_run: int) -> list[str]:
    smoothed = list(phases)
    while True:
        runs = _phase_runs(smoothed)
        changed = False

        for idx, (phase, start, end, length) in enumerate(runs):
            if length >= min_run:
                continue

            prev_run = runs[idx - 1] if idx > 0 else None
            next_run = runs[idx + 1] if idx + 1 < len(runs) else None
            prev_phase = prev_run[0] if prev_run else None
            next_phase = next_run[0] if next_run else None

            if prev_phase == next_phase and prev_phase is not None:
                replacement = prev_phase
            elif prev_phase is None:
                replacement = next_phase
            elif next_phase is None:
                replacement = prev_phase
            else:
                replacement = prev_phase if prev_run[3] >= next_run[3] else next_phase

            if replacement and replacement != phase:
                smoothed[start:end + 1] = [replacement] * length
                changed = True
                break

        if not changed:
            return smoothed


def smooth_phases(phases: list[str | None], min_run: int = 5) -> list[str | None]:
    """Reduce short phase flicker while preserving larger phase arcs."""
    smoothed = list(phases)
    idx = 0

    while idx < len(smoothed):
        while idx < len(smoothed) and smoothed[idx] is None:
            idx += 1

        block_start = idx
        while idx < len(smoothed) and smoothed[idx] is not None:
            idx += 1
        block_end = idx

        if block_end > block_start:
            block = [phase for phase in smoothed[block_start:block_end] if phase is not None]
            smoothed[block_start:block_end] = _smooth_phase_block(block, min_run)

    return smoothed


def summarize_current_phase(
    dates: list[str],
    phases: list[str | None],
) -> dict:
    valid = [(pd.to_datetime(dt), phase) for dt, phase in zip(dates, phases) if phase is not None]
    if not valid:
        return {}

    phase_dates = [dt for dt, _ in valid]
    phase_values = [phase for _, phase in valid]
    runs = _phase_runs(phase_values)
    current_phase, current_start_idx, _, run_length = runs[-1]
    run_start_date = phase_dates[current_start_idx]

    current_durations = [length for phase, _, _, length in runs if phase == current_phase]
    observed_average = float(np.mean(current_durations)) if current_durations else float(run_length)
    eligible = [duration for duration in current_durations if duration >= run_length]
    conditional_total = float(np.mean(eligible)) if eligible else observed_average
    blended_total = max(run_length, round((observed_average + conditional_total) / 2, 1))
    remaining_steps = max(0.0, blended_total - run_length)
    progress_ratio = min(1.0, run_length / blended_total) if blended_total > 0 else 0.0

    if len(phase_dates) >= 2:
        step_days = max(
            1,
            int(round(np.median(np.diff(np.array(phase_dates, dtype="datetime64[D]")).astype(int)))),
        )
    else:
        step_days = 1

    likely_end_date = (phase_dates[-1] + pd.Timedelta(days=int(round(remaining_steps * step_days)))).date()

    def empirical_end_probability(horizon: int) -> float:
        if not eligible:
            return 0.0
        ended = sum(duration <= run_length + horizon for duration in eligible)
        return round(ended / len(eligible), 4)

    return {
        "current_phase": current_phase,
        "current_phase_description": PHASE_DESCRIPTIONS.get(current_phase, ""),
        "current_run_length": int(run_length),
        "current_run_start": str(run_start_date.date()),
        "observed_average_duration": round(observed_average, 1),
        "conditional_total_duration": round(conditional_total, 1),
        "blended_total_duration": round(blended_total, 1),
        "estimated_remaining_steps": round(remaining_steps, 1),
        "progress_ratio": round(progress_ratio, 4),
        "likely_end_date": str(likely_end_date),
        "historical_runs": len(current_durations),
        "probability_end_10": empirical_end_probability(10),
        "probability_end_20": empirical_end_probability(20),
        "probability_end_30": empirical_end_probability(30),
    }
