from __future__ import annotations

import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

from .common import ARTIFACT_ROOT, linear_fit, loglog_fit, write_json


def _load_fraction(record: dict[str, Any]) -> Fraction:
    return Fraction(record["numerator"], record["denominator"])


def _recompute(alpha: Fraction, perturbation: Fraction, horizon: int) -> Fraction:
    difference = Fraction(0)
    cumulative = Fraction(0)
    for _ in range(horizon):
        difference = alpha * difference + perturbation
        cumulative += abs(difference)
    return cumulative


def check_claim_2(raw_path: Path | None = None) -> dict[str, Any]:
    claim_dir = ARTIFACT_ROOT / "claim_2"
    if raw_path is None:
        raw_path = claim_dir / "raw_results.json"
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    sweep = raw["horizon_sweep"]
    perturbation = _load_fraction(sweep["perturbation"])
    horizons = sweep["horizons"]
    stable_values = [
        _load_fraction(item)
        for item in sweep["stable"]["cumulative_state_difference"]
    ]
    unstable_values = [
        _load_fraction(item)
        for item in sweep["unstable_negative_control"][
            "cumulative_state_difference"
        ]
    ]
    stable_exact = [
        _recompute(Fraction(1, 2), perturbation, horizon)
        for horizon in horizons
    ]
    unstable_exact = [
        _recompute(Fraction(2), perturbation, horizon)
        for horizon in horizons
    ]
    stable_poly = loglog_fit(horizons, [float(value) for value in stable_values])
    stable_exp = linear_fit(
        horizons, np.log([float(value) for value in stable_values])
    )
    unstable_poly = loglog_fit(
        horizons, [float(value) for value in unstable_values]
    )
    unstable_exp = linear_fit(
        horizons, np.log([float(value) for value in unstable_values])
    )
    epsilon = raw["epsilon_sweep"]
    epsilon_fit = loglog_fit(
        [_load_fraction(item) for item in epsilon["epsilon_q"]],
        [
            _load_fraction(item)
            for item in epsilon["cumulative_state_difference"]
        ],
    )
    checks = {
        "stable_exact_recurrence": stable_values == stable_exact,
        "unstable_exact_recurrence": unstable_values == unstable_exact,
        "stable_model_selection": (
            0.90 <= stable_poly["slope"] <= 1.10
            and stable_poly["residual_sum_squares"]
            < stable_exp["residual_sum_squares"] * 0.10
        ),
        "unstable_model_selection": (
            abs(unstable_exp["slope"] - math.log(2.0)) <= 0.01
            and unstable_exp["residual_sum_squares"]
            < unstable_poly["residual_sum_squares"] * 0.01
        ),
        "epsilon_linear": abs(epsilon_fit["slope"] - 1.0) <= 1e-6,
        "rtvc_pair_accounting": (
            raw["rtvc_certificate"]["total_state_pairs"]
            == sum(
                row["grid_resolution"] * (row["grid_resolution"] - 1) // 2
                for row in raw["rtvc_certificate"]["grid_results"]
            )
        ),
        "rtvc_zero_violations": (
            raw["rtvc_certificate"]["total_violations"] == 0
        ),
        "piiss_gain_bounded": (
            _load_fraction(
                raw["piiss_certificate"]["stable"]["maximum_enumerated_gain"]
            )
            <= Fraction(2)
        ),
        "unstable_gain_identity": all(
            _load_fraction(row["gain"]) == 2 ** row["horizon"] - 1
            for row in raw["piiss_certificate"]["unstable_negative_control"][
                "gains"
            ]
        ),
    }
    result = {
        "claim": 2,
        "checker": "independent rational recurrence and model recomputation",
        "checks": checks,
        "stable_polynomial_fit": stable_poly,
        "unstable_exponential_fit": unstable_exp,
        "epsilon_fit": epsilon_fit,
        "passed": bool(all(checks.values())),
    }
    write_json(claim_dir / "independent_check.json", result)
    if not result["passed"]:
        raise AssertionError(f"Claim 2 independent check failed: {checks}")
    return result
