"""Regime detection models and interpretation."""

import numpy as np
from hmmlearn.hmm import GaussianHMM


def fit_hmm(
    train_X: np.ndarray, test_X: np.ndarray,
    n_states: int = 3, covariance_type: str = "diag",
    n_iter: int = 200, tol: float = 1e-4, random_seed: int = 42,
) -> dict:
    model = GaussianHMM(
        n_components=n_states, covariance_type=covariance_type,
        n_iter=n_iter, tol=tol, random_state=random_seed,
    )
    model.fit(train_X)
    train_states = model.predict(train_X)
    test_states = model.predict(test_X)

    ll = float(model.score(train_X))
    k = _n_params(n_states, train_X.shape[1], covariance_type)
    n = train_X.shape[0]
    aic = 2 * k - 2 * ll
    bic = k * np.log(n) - 2 * ll

    return {
        "model": model,
        "train_states": train_states,
        "test_states": test_states,
        "transmat": model.transmat_.tolist(),
        "log_likelihood": ll,
        "aic": aic,
        "bic": bic,
    }


def _n_params(n_states, n_features, cov_type):
    k = n_features
    n = n_states
    p = (n - 1) + n * (n - 1) + n * k
    if cov_type == "full":
        p += n * k * (k + 1) // 2
    elif cov_type == "diag":
        p += n * k
    elif cov_type == "spherical":
        p += n
    else:
        p += k * (k + 1) // 2
    return p


def summarize_state_profiles(
    returns: np.ndarray,
    states: np.ndarray,
    n_states: int,
) -> list[dict]:
    profiles = []
    for s in range(n_states):
        state_returns = returns[states == s]
        profiles.append(
            {
                "state": s,
                "count": int(len(state_returns)),
                "mean": float(np.mean(state_returns)) if len(state_returns) else 0.0,
                "vol": float(np.std(state_returns)) if len(state_returns) else np.inf,
            }
        )
    return profiles


def canonical_order_from_profiles(profiles: list[dict]) -> list[int]:
    states = [p["state"] for p in profiles]
    mean_desc = {
        state: rank
        for rank, state in enumerate(
            [p["state"] for p in sorted(profiles, key=lambda p: (p["mean"], -p["vol"]), reverse=True)]
        )
    }
    mean_asc = {
        state: rank
        for rank, state in enumerate(
            [p["state"] for p in sorted(profiles, key=lambda p: (p["mean"], p["vol"]))]
        )
    }
    vol_asc = {
        state: rank
        for rank, state in enumerate(
            [p["state"] for p in sorted(profiles, key=lambda p: (p["vol"], -p["mean"]))]
        )
    }
    vol_desc = {
        state: rank
        for rank, state in enumerate(
            [p["state"] for p in sorted(profiles, key=lambda p: (p["vol"], p["mean"]), reverse=True)]
        )
    }

    bull_state = min(states, key=lambda s: mean_desc[s] + vol_asc[s])
    remaining = [s for s in states if s != bull_state]
    stress_state = min(remaining, key=lambda s: mean_asc[s] + vol_desc[s])
    middle_states = [s for s in remaining if s != stress_state]

    if not middle_states:
        return [bull_state, stress_state]

    middle_states = sorted(
        middle_states,
        key=lambda s: (
            mean_asc[s] + vol_asc[s],
            mean_asc[s],
            vol_asc[s],
        ),
    )
    return [bull_state, *middle_states, stress_state]


def labels_from_profiles(profiles: list[dict]) -> dict[int, str]:
    n_states = len(profiles)
    order = canonical_order_from_profiles(profiles)
    by_state = {p["state"]: p for p in profiles}
    labels: dict[int, str] = {}

    bull_state = order[0]
    bull_profile = by_state[bull_state]
    labels[bull_state] = (
        "Bull / Expansion"
        if bull_profile["mean"] >= 0
        else "Defensive / Consolidation"
    )

    if n_states == 2:
        stress_state = order[1]
        stress_profile = by_state[stress_state]
        labels[stress_state] = (
            "Bear / Stress"
            if stress_profile["mean"] < 0
            else "Volatile / Recovery"
        )
        return labels

    stress_state = order[-1]
    stress_profile = by_state[stress_state]
    labels[stress_state] = (
        "Bear / Stress"
        if stress_profile["mean"] < 0
        else "Volatile / Recovery"
    )

    middle_states = order[1:-1]
    for idx, state in enumerate(middle_states):
        profile = by_state[state]
        if profile["mean"] < -0.00025:
            label = "Distribution / Drawdown"
        elif profile["mean"] > 0.00025:
            label = "Recovery / Transition"
        else:
            label = "Transition / Mixed"

        if len(middle_states) > 1:
            label = f"{label} {idx + 1}"
        labels[state] = label

    return labels


def interpret_regimes(returns: np.ndarray, states: np.ndarray, n_states: int) -> dict[int, str]:
    profiles = summarize_state_profiles(returns, states, n_states)
    return labels_from_profiles(profiles)
