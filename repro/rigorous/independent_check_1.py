from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np

from .common import ARTIFACT_ROOT, bootstrap_mean_curve_slope, linear_fit, loglog_fit, write_json


def check_claim_1(raw_path: Path | None = None) -> dict[str, Any]:
    claim_dir = ARTIFACT_ROOT / "claim_1"
    if raw_path is None:
        raw_path = claim_dir / "raw_results.json"
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    statistical = raw["statistical_rate"]
    n_values = np.asarray(statistical["n_values"], dtype=float)
    errors = np.asarray(statistical["absolute_probability_errors"], dtype=float)
    means = errors.mean(axis=0)
    rate_fit = loglog_fit(n_values, means)
    bootstrap = bootstrap_mean_curve_slope(
        n_values, errors, seed=91020538, replicates=2000
    )
    ci_low, ci_high = bootstrap["ci95"]

    floor = raw["quantization_floor"]
    floor_fit = loglog_fit(floor["epsilon_q"], floor["regret"])

    ratchet = raw["finite_policy_class_ratchet"]
    deviations = np.asarray(ratchet["uniform_log_loss_deviations"], dtype=float)
    class_fit = linear_fit(
        np.log(np.asarray(ratchet["class_sizes"], dtype=float)),
        deviations.mean(axis=0) ** 2,
    )
    nc_curve = np.asarray(
        ratchet["negative_control"]["mean_deviation"], dtype=float
    )
    class_nc_fit = linear_fit(
        np.log(np.asarray(ratchet["class_sizes"], dtype=float)),
        nc_curve**2,
    )

    controls = statistical["negative_controls"]
    zero_fit = loglog_fit(
        n_values, np.asarray(controls["zero_effect_mean_errors"], dtype=float)
    )
    wrong_fit = loglog_fit(
        n_values, np.asarray(controls["wrong_rate_mean_errors"], dtype=float)
    )
    checks = {
        "raw_shape": errors.shape == (256, 6),
        "all_errors_finite_nonnegative": bool(
            np.all(np.isfinite(errors)) and np.all(errors >= 0)
        ),
        "independent_rate_point": -0.58 <= rate_fit["slope"] <= -0.42,
        "independent_ci_contains_minus_half": ci_low <= -0.5 <= ci_high,
        "independent_ci_excludes_zero": not (ci_low <= 0.0 <= ci_high),
        "independent_ci_excludes_minus_one": not (ci_low <= -1.0 <= ci_high),
        "floor_identity": all(
            math.isclose(
                regret,
                floor["horizon"] * epsilon / 2.0,
                rel_tol=0.0,
                abs_tol=1e-14,
            )
            for epsilon, regret in zip(floor["epsilon_q"], floor["regret"])
        ),
        "floor_exponent": 0.99 <= floor_fit["slope"] <= 1.01,
        "finite_class_log_dependence": (
            class_fit["slope"] > 0.0 and class_fit["r2"] >= 0.90
        ),
        "zero_effect_control": abs(zero_fit["slope"]) <= 0.05,
        "wrong_rate_control": -1.05 <= wrong_fit["slope"] <= -0.95,
        "finite_class_control_flat": abs(class_nc_fit["slope"]) <= 1e-12,
    }
    result = {
        "claim": 1,
        "checker": "independent recomputation from raw arrays",
        "checks": checks,
        "rate_fit": rate_fit,
        "bootstrap": bootstrap,
        "floor_fit": floor_fit,
        "finite_class_fit": class_fit,
        "finite_class_negative_control_fit": class_nc_fit,
        "passed": bool(all(checks.values())),
    }
    write_json(claim_dir / "independent_check.json", result)
    if not result["passed"]:
        raise AssertionError(f"Claim 1 independent check failed: {checks}")
    return result
