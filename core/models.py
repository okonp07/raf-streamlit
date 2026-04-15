"""Regime detection models and interpretation."""

import numpy as np
from hmmlearn.hmm import GaussianHMM


def fit_hmm(
    train_X: np.ndarray, test_X: np.ndarray,
    n_states: int = 3, covariance_type: str = "full",
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


def interpret_regimes(returns: np.ndarray, states: np.ndarray, n_states: int) -> dict[int, str]:
    stats = []
    for s in range(n_states):
        r = returns[states == s]
        stats.append({"state": s, "mean": float(np.mean(r)) if len(r) else 0, "vol": float(np.std(r)) if len(r) else 999})

    sorted_by_vol = sorted(stats, key=lambda x: x["vol"])
    labels = {}

    if n_states == 2:
        low, high = sorted_by_vol
        labels[low["state"]] = "Bull / Low Vol" if low["mean"] >= 0 else "Calm / Negative"
        labels[high["state"]] = "Stress / High Vol" if high["mean"] < 0 else "Volatile / Positive"
    elif n_states == 3:
        low, mid, high = sorted_by_vol
        labels[low["state"]] = "Bull / Low Vol" if low["mean"] >= 0 else "Calm / Mild Decline"
        labels[mid["state"]] = "Transition / Moderate"
        labels[high["state"]] = "Stress / High Vol" if high["mean"] < 0 else "Volatile / Recovery"
    else:
        for i, stat in enumerate(sorted_by_vol):
            pct = i / (n_states - 1) if n_states > 1 else 0
            if pct < 0.33:
                labels[stat["state"]] = "Low Vol" if stat["mean"] >= 0 else "Calm"
            elif pct < 0.66:
                labels[stat["state"]] = "Moderate"
            else:
                labels[stat["state"]] = "Stress / High Vol" if stat["mean"] < 0 else "Volatile"
    return labels
