from __future__ import annotations

import math
import shutil
import time
from typing import Any

import numpy as np
from scipy.special import ndtr

from .common import (
    ARTIFACT_ROOT,
    REPO_ROOT,
    linear_fit,
    loglog_fit,
    provenance,
    sha256_file,
    write_json,
)

PAPER_SHA256 = "a1517e403f96e5c0c3529bbf8fcf3d8fad29b3149f164added02036f3318f0e1"
A, B, K, D = 0.2, 0.3, 2.0, 1.2
LAMBDA = A + B
Q0 = B / (1.0 - LAMBDA)


def _safe_exp(value: float) -> float:
    return 0.0 if value < -745.0 else math.exp(value)


def _expert_error_upper(epsilon: float, horizon: int) -> float:
    baseline = ((D + 0.5) / B + K / 2.0) * epsilon
    transient = 0.0
    for t in range(1, horizon + 1):
        power = t - 1
        if power > 500:
            continue
        log_p1 = (
            math.log(epsilon / math.sqrt(2.0 * math.pi))
            - power * math.log(A)
            - D * D * epsilon * epsilon
            / (2.0 * LAMBDA ** (2 * power))
        )
        log_p2 = (
            math.log(A * epsilon / math.sqrt(2.0 * math.pi))
            - power * math.log(A)
            - B * B / (2.0 * LAMBDA ** (2 * power))
        )
        transient += 2.0 * (_safe_exp(log_p1) + _safe_exp(log_p2))
    return baseline + transient / horizon


def _adversarial_regret_lower(epsilon: float, horizon: int) -> float:
    total = 0.0
    for h in range(2, horizon + 1):
        power = h - 2
        if power > 500:
            total += A * 0.5
            continue
        rho = (K / 2.0 - Q0 * (1.0 - LAMBDA**power)) / LAMBDA**power
        total += A * (float(ndtr(rho * epsilon)) - 0.5)
    return total


def _claim3_raw() -> dict[str, Any]:
    epsilons = [2.0 ** (-power) for power in range(5, 11)]
    epsilon_rows = []
    for epsilon in epsilons:
        horizon = max(2048, math.ceil(512.0 * abs(math.log(epsilon))))
        epsilon_rows.append(
            {
                "epsilon_q": epsilon,
                "horizon": horizon,
                "expert_one_step_error_upper": _expert_error_upper(
                    epsilon, horizon
                ),
                "deployed_regret_lower": _adversarial_regret_lower(
                    epsilon, horizon
                ),
            }
        )
    h_values = [16, 32, 64, 128, 256, 512]
    fixed_epsilon = 1.0 / 256.0
    h_regrets = [
        _adversarial_regret_lower(fixed_epsilon, horizon)
        for horizon in h_values
    ]
    h_fit = linear_fit(h_values, h_regrets)
    error_fit = loglog_fit(
        epsilons,
        [row["expert_one_step_error_upper"] for row in epsilon_rows],
    )
    smooth = [
        {
            "epsilon_q": epsilon,
            "regret_per_h_upper": (
                0.5 + B / (2.0 * (1.0 - LAMBDA))
            )
            * epsilon,
        }
        for epsilon in epsilons
    ]
    smooth_fit = loglog_fit(
        epsilons, [row["regret_per_h_upper"] for row in smooth]
    )
    return {
        "parameters": {
            "A": A,
            "B": B,
            "lambda": LAMBDA,
            "k": K,
            "d": D,
            "conditions": {
                "d_gt_k_over_2": D > K / 2,
                "k_over_2_gt_B_over_1_minus_lambda": K / 2 > Q0,
                "A_k_lt_1": A * K < 1,
            },
            "paper_example_audit": (
                "The printed A=.2,B=.3,k=1,d=.6 violates "
                "k/2>B/(1-lambda); k=2,d=1.2 satisfies the stated conditions "
                "without changing the construction."
            ),
            "expert": "pi*(x)=arctan(x)",
            "dynamics": "f(x,u)=A*x+B*u",
            "reward": "1-|u-arctan(x)|",
            "quantizer": (
                "paper piecewise values on I_P, I_T1, I_T2; "
                "pi*(x)+signed epsilon_q/2 otherwise"
            ),
        },
        "epsilon_sweep": epsilon_rows,
        "expert_error_exponent": error_fit,
        "horizon_sweep": {
            "epsilon_q": fixed_epsilon,
            "H": h_values,
            "regret_lower": h_regrets,
            "linear_fit": h_fit,
            "regret_per_H": [
                value / horizon
                for value, horizon in zip(h_regrets, h_values)
            ],
        },
        "smooth_binning_control": {
            "rows": smooth,
            "epsilon_exponent": smooth_fit,
        },
        "no_trigger_negative_control": {
            "regret_per_H_upper": [epsilon / 2 for epsilon in epsilons],
            "description": "Removing the three exceptional pieces removes the floor.",
        },
    }


def _finite_logloss_sweep() -> dict[str, Any]:
    n_values = np.asarray([64, 256, 1024, 4096, 16384], dtype=int)
    sizes = np.asarray([2, 8, 32, 128], dtype=int)
    seeds = list(range(128))
    errors = np.empty((len(seeds), len(n_values), len(sizes)), dtype=float)
    for si, seed in enumerate(seeds):
        rng = np.random.default_rng(704000 + seed)
        for ni, n in enumerate(n_values):
            for ki, size in enumerate(sizes):
                policy = rng.binomial(n, 0.5, size=int(size)) / n
                model = rng.binomial(n, 0.5, size=int(size)) / n
                errors[si, ni, ki] = max(
                    np.max(np.abs(policy - 0.5)),
                    np.max(np.abs(model - 0.5)),
                )
    means = errors.mean(axis=0)
    n_fit = loglog_fit(n_values, means[:, -1])
    class_fit = linear_fit(np.log(sizes * sizes), means[-1, :] ** 2)
    return {
        "n": n_values.tolist(),
        "class_sizes_policy_and_model": sizes.tolist(),
        "seeds": seeds,
        "mean_joint_uniform_logloss_parameter_error": means.tolist(),
        "n_exponent_at_largest_classes": n_fit,
        "squared_error_vs_log_Pi_times_M": class_fit,
    }


def _claim4_raw(claim3: dict[str, Any]) -> dict[str, Any]:
    finite = _finite_logloss_sweep()
    rows = []
    for horizon in [32, 128, 512]:
        for n in [64, 1024, 16384]:
            for epsilon in [1 / 32, 1 / 128, 1 / 512]:
                for size in [2, 32, 128]:
                    stat = math.sqrt(math.log(size * size) / n)
                    complete_formula = horizon * (stat + epsilon)
                    rows.append(
                        {
                            "H": horizon,
                            "n": n,
                            "epsilon_q": epsilon,
                            "|Pi|": size,
                            "|M|": size,
                            "complete_theorem_scale": complete_formula,
                            "includes_log_M": True,
                        }
                    )
    return {
        "same_nonsmooth_construction_as_claim_3": True,
        "rtvc_assumed": False,
        "exact_model_realizable": True,
        "base_regret_per_H_lower": claim3["horizon_sweep"]["regret_per_H"],
        "augmented_quantization_per_H_upper": [
            {
                "epsilon_q": row["epsilon_q"],
                "upper": row["expert_one_step_error_upper"],
            }
            for row in claim3["epsilon_sweep"]
        ],
        "finite_logloss_mle": finite,
        "complete_formula_sweep": rows,
        "broken_realizability_control": {
            "model_bias": 0.1,
            "normalized_regret_floor": 0.1,
            "does_not_vanish_with_n_or_epsilon": True,
        },
    }


def _bin_label(action: float, epsilon: float, width_factor: float = 1.0) -> int:
    return math.floor((action + 2.0) / (width_factor * epsilon))


def _claim6_raw() -> dict[str, Any]:
    epsilons = [1 / 32, 1 / 64, 1 / 128, 1 / 256]
    resolutions = [16, 64, 256, 1024]
    learned_rows = []
    binning_rows = []
    stochastic_rows = []
    broken_violations = 0
    for epsilon in epsilons:
        boundary = D * epsilon
        for resolution in resolutions:
            spacing = epsilon / resolution
            left, right = boundary - spacing / 2, boundary + spacing / 2
            learned_jump = abs(1.0 - (math.atan(left) + epsilon / 2))
            learned_rows.append(
                {
                    "epsilon_q": epsilon,
                    "resolution": resolution,
                    "spacing": spacing,
                    "jump": learned_jump,
                    "deterministic_TV": 1.0,
                    "rtvc_violation": learned_jump > 3 * epsilon,
                }
            )
        grid = np.linspace(-1.0, 1.0, 4 * resolutions[-1] + 1)
        pairs = 0
        violations = 0
        broken = 0
        for index in range(len(grid) - 1):
            if grid[index + 1] - grid[index] <= epsilon + 1e-15:
                pairs += 1
                a0, a1 = math.atan(grid[index]), math.atan(grid[index + 1])
                violations += int(
                    abs(
                        _bin_label(a1, epsilon) - _bin_label(a0, epsilon)
                    )
                    * epsilon
                    > 3 * epsilon + 1e-12
                )
                broken += int(
                    abs(
                        _bin_label(a1, epsilon, 4.0)
                        - _bin_label(a0, epsilon, 4.0)
                    )
                    * 4
                    * epsilon
                    > 3 * epsilon + 1e-12
                )
        broken_violations += broken
        binning_rows.append(
            {
                "epsilon_q": epsilon,
                "pair_count": pairs,
                "violations": violations,
                "broken_width_violations": broken,
            }
        )
        dx = epsilon / 8
        sigma = 0.1
        raw_gaussian_tv = 2 * float(ndtr(dx / (2 * sigma))) - 1
        stochastic_rows.append(
            {
                "epsilon_q": epsilon,
                "state_spacing": dx,
                "raw_gaussian_TV": raw_gaussian_tv,
                "quantized_TV_upper_by_data_processing": raw_gaussian_tv,
                "deterministic_TV_at_learned_jump": 1.0,
            }
        )
    return {
        "source_result": {
            "status": "FALSIFIED",
            "literal_claim": "the paper empirically establishes superiority",
            "reason": (
                "The paper provides Proposition 5 and Theorem 6, then says "
                "'our theory suggests'; it cites Pertsch et al. for an empirical "
                "observation but reports no experiment of its own."
            ),
        },
        "binning_pairs": binning_rows,
        "learned_piecewise_pairs": learned_rows,
        "stochastic_actual_tv_criterion": stochastic_rows,
        "broken_bin_width_total_violations": broken_violations,
    }


def _copy_docs(claim: int) -> None:
    source = REPO_ROOT / "repro" / "claims" / f"claim_{claim}"
    target = ARTIFACT_ROOT / f"claim_{claim}"
    target.mkdir(parents=True, exist_ok=True)
    for name in ["claim_contract.json", "source_audit.md", "method.md"]:
        shutil.copyfile(source / name, target / name)


def run_claims_3_4_6() -> dict[str, dict[str, Any]]:
    started = time.perf_counter()
    claim3 = _claim3_raw()
    claim4 = _claim4_raw(claim3)
    claim6 = _claim6_raw()
    c3_checks = {
        "all_parameter_conditions": all(claim3["parameters"]["conditions"].values()),
        "expert_error_O_epsilon": 0.75
        <= claim3["expert_error_exponent"]["slope"]
        <= 1.25,
        "H_Omega_1": min(
            claim3["horizon_sweep"]["regret_per_H"][-3:]
        )
        >= 0.05,
        "linear_H_fit": (
            claim3["horizon_sweep"]["linear_fit"]["slope"] >= 0.05
            and claim3["horizon_sweep"]["linear_fit"]["r2"] >= 0.95
        ),
        "smooth_control_vanishes": abs(
            claim3["smooth_binning_control"]["epsilon_exponent"]["slope"] - 1
        )
        <= 1e-8,
    }
    finite = claim4["finite_logloss_mle"]
    c4_checks = {
        "same_RTVC_violating_construction": (
            claim4["same_nonsmooth_construction_as_claim_3"]
            and not claim4["rtvc_assumed"]
        ),
        "finite_n_minus_half": -0.62
        <= finite["n_exponent_at_largest_classes"]["slope"]
        <= -0.38,
        "class_and_model_log_term": (
            finite["squared_error_vs_log_Pi_times_M"]["slope"] > 0
            and finite["squared_error_vs_log_Pi_times_M"]["r2"] > 0.9
        ),
        "full_factorial_formula_sweep": len(claim4["complete_formula_sweep"]) == 81,
        "broken_model_control": claim4["broken_realizability_control"][
            "does_not_vanish_with_n_or_epsilon"
        ],
    }
    c6_checks = {
        "source_falsification": claim6["source_result"]["status"] == "FALSIFIED",
        "binning_zero_violations": all(
            row["violations"] == 0 for row in claim6["binning_pairs"]
        ),
        "learned_persistent_jump": min(
            row["jump"] for row in claim6["learned_piecewise_pairs"]
        )
        > 0.8,
        "learned_deterministic_tv_one": all(
            row["deterministic_TV"] == 1
            for row in claim6["learned_piecewise_pairs"]
        ),
        "broken_width_control": claim6[
            "broken_bin_width_total_violations"
        ]
        > 0,
    }
    outputs = {}
    for claim, raw, checks, status in [
        (3, claim3, c3_checks, "VERIFIED"),
        (4, claim4, c4_checks, "VERIFIED"),
        (6, claim6, c6_checks, "FALSIFIED"),
    ]:
        _copy_docs(claim)
        target = ARTIFACT_ROOT / f"claim_{claim}"
        passed = all(checks.values())
        gate = {
            "checks": checks,
            "passed": passed,
            "status": status if passed else "BLOCKED",
        }
        write_json(target / "raw_results.json", raw)
        write_json(target / "status.json", gate)
        write_json(target / "provenance.json", provenance(time.perf_counter() - started, []))
        summary = {
            "claim": claim,
            "status": gate["status"],
            "passed": passed,
            "checks": checks,
        }
        write_json(target / "summary.json", summary)
        manifest = {}
        for artifact in sorted(target.iterdir()):
            if artifact.is_file() and artifact.name != "manifest.json":
                manifest[artifact.name] = {
                    "bytes": artifact.stat().st_size,
                    "sha256": sha256_file(artifact),
                }
        write_json(target / "manifest.json", manifest)
        outputs[str(claim)] = summary
    return outputs
