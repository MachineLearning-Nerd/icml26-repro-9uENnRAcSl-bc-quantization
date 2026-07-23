from __future__ import annotations

import json
from typing import Any

from .common import ARTIFACT_ROOT, write_json


def _load(claim: int) -> dict[str, Any]:
    return json.loads(
        (ARTIFACT_ROOT / f"claim_{claim}/raw_results.json").read_text(
            encoding="utf-8"
        )
    )


def _finish(claim: int, checks: dict[str, bool], checker: str) -> dict[str, Any]:
    result = {
        "claim": claim,
        "checker": checker,
        "checks": checks,
        "passed": bool(all(checks.values())),
    }
    write_json(
        ARTIFACT_ROOT / f"claim_{claim}/independent_check.json", result
    )
    if not result["passed"]:
        raise AssertionError(
            f"Claim {claim} independent check failed: {checks}"
        )
    return result


def check_claim_3() -> dict[str, Any]:
    raw = _load(3)
    checks = {
        "parameter_inequalities": all(
            raw["parameters"]["conditions"].values()
        ),
        "actual_expectation_bound": all(
            row["expert_error_certificate"]["method"].startswith(
                "Invert the monotone raw-expert recursion"
            )
            and row["expert_one_step_error_upper"]
            == row["expert_error_certificate"]["expectation_upper"]
            for row in raw["epsilon_sweep"]
        ),
        "omega_log_schedule": all(
            later["H_over_abs_log_epsilon"]
            > earlier["H_over_abs_log_epsilon"]
            for earlier, later in zip(
                raw["epsilon_sweep"], raw["epsilon_sweep"][1:]
            )
        ),
        "numerical_certificate": all(
            certificate["inverse_residual_max"] < 1e-12
            and certificate["normal_tail_truncation_bound"] < 1e-20
            for row in raw["epsilon_sweep"]
            for certificate in row["expert_error_certificate"][
                "probability_certificates"
            ].values()
        ),
        "uniform_linear_constant": max(
            row["expert_one_step_error_upper"] / row["epsilon_q"]
            for row in raw["epsilon_sweep"]
        )
        < 20,
        "deployed_floor": min(
            raw["horizon_sweep"]["regret_per_H"][-3:]
        )
        >= 0.05,
        "smooth_control_vanishes": all(
            later["regret_per_h_upper"] < earlier["regret_per_h_upper"]
            for earlier, later in zip(
                raw["smooth_binning_control"]["rows"],
                raw["smooth_binning_control"]["rows"][1:],
            )
        ),
    }
    return _finish(
        3,
        checks,
        "independent raw-table preimage, asymptotic, and limit checks",
    )


def check_claim_4() -> dict[str, Any]:
    raw = _load(4)
    sweep = raw["complete_product_construction_sweep"]
    checks = {
        "all_axes": (
            len({row["H"] for row in sweep}) == 3
            and len({row["n"] for row in sweep}) == 3
            and len({row["epsilon_q"] for row in sweep}) == 3
            and len({row["|Pi|"] for row in sweep}) == 3
            and len({row["|M|"] for row in sweep}) == 3
            and all(row["includes_log_M"] for row in sweep)
        ),
        "not_formula_only": (
            "not a formula evaluation" in raw["product_construction"]
            and all(
                abs(
                    row["observed_product_MDP_regret"]
                    - row["observed_statistical_component"]
                    - row["observed_quantization_component"]
                )
                < 1e-10
                for row in sweep
            )
        ),
        "direct_rollout_convergence": max(
            row["last_refinement_difference"]
            for row in raw["direct_augmented_rollouts"]["factorial_rows"]
        )
        < 5e-3,
        "direct_rollout_certificate": all(
            row["augmented_below_certified_upper"]
            for row in raw["direct_augmented_rollouts"]["factorial_rows"]
        ),
        "finite_mle_confidence_intervals": all(
            row["ci95"][0]
            < row["mean_operational_TV_regret_per_step"]
            < row["ci95"][1]
            for row in raw["finite_logloss_mle"]["rows"]
        ),
        "broken_realizability": (
            raw["broken_realizability_control"]["normalized_regret_floor"] > 0
            and raw["broken_realizability_control"][
                "largest_n_smallest_epsilon_ratio_to_claimed_scale"
            ]
            > 1
        ),
    }
    return _finish(
        4,
        checks,
        "independent operational-sum, convergence, and class-axis checks",
    )


def check_claim_6() -> dict[str, Any]:
    raw = _load(6)
    checks = {
        "binning_pair_counts": sum(
            row["pair_count"] for row in raw["binning_pairs"]
        )
        > 10_000,
        "binning_zero_costs": all(
            row["relaxed_OT_cost_violations"] == 0
            for row in raw["binning_pairs"]
        ),
        "exhaustive_multiresolution_cells": (
            len(raw["binning_pairs"]) == 16
            and len(
                {
                    (row["epsilon_q"], row["resolution"])
                    for row in raw["binning_pairs"]
                }
            )
            == 16
            and min(row["pair_count"] for row in raw["binning_pairs"])
            > 1_000
        ),
        "learned_persistent_cost": (
            min(
                row["jump"] for row in raw["learned_piecewise_pairs"]
            )
            > 0.8
            and all(
                row["relaxed_OT_cost"] == 1
                for row in raw["learned_piecewise_pairs"]
            )
        ),
        "stochastic_actual_categorical_TV": all(
            0
            <= row["quantized_categorical_TV"]
            <= row["raw_gaussian_TV"] + 1e-12
            and row["tail_refinement_difference"] < 1e-12
            and row["tail_10"]["omitted_mass_upper"] < 1e-20
            for row in raw["stochastic_actual_tv_criterion"]
        ),
        "broken_width_negative_control": (
            raw["broken_bin_width_total_violations"] > 0
        ),
        "literal_source_falsification": (
            raw["source_result"]["status"] == "FALSIFIED"
        ),
    }
    return _finish(
        6,
        checks,
        "independent Definition-4 transport and categorical-TV checks",
    )


def check_claims_3_4_6() -> dict[str, Any]:
    """Compatibility aggregate; each claim is checked and written separately."""
    results = {
        "3": check_claim_3(),
        "4": check_claim_4(),
        "6": check_claim_6(),
    }
    return {
        "checker": "aggregate of three independent claim-specific checkers",
        "claims": results,
        "checks": {
            f"claim_{claim}": result["passed"]
            for claim, result in results.items()
        },
        "passed": all(result["passed"] for result in results.values()),
    }
