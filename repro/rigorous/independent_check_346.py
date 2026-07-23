from __future__ import annotations

import json
from typing import Any

from .common import ARTIFACT_ROOT, write_json


def check_claims_3_4_6() -> dict[str, Any]:
    raw3 = json.loads((ARTIFACT_ROOT / "claim_3/raw_results.json").read_text())
    raw4 = json.loads((ARTIFACT_ROOT / "claim_4/raw_results.json").read_text())
    raw6 = json.loads((ARTIFACT_ROOT / "claim_6/raw_results.json").read_text())
    checks = {
        "claim3_parameter_inequalities": all(
            raw3["parameters"]["conditions"].values()
        ),
        "claim3_actual_expectation_bound": all(
            row["expert_error_certificate"]["method"].startswith(
                "Invert the monotone raw-expert recursion"
            )
            and row["expert_one_step_error_upper"]
            == row["expert_error_certificate"]["expectation_upper"]
            for row in raw3["epsilon_sweep"]
        ),
        "claim3_omega_log_schedule": all(
            later["H_over_abs_log_epsilon"]
            > earlier["H_over_abs_log_epsilon"]
            for earlier, later in zip(
                raw3["epsilon_sweep"],
                raw3["epsilon_sweep"][1:],
            )
        ),
        "claim3_numerical_certificate": all(
            certificate["inverse_residual_max"] < 1e-12
            and certificate["normal_tail_truncation_bound"] < 1e-20
            for row in raw3["epsilon_sweep"]
            for certificate in row["expert_error_certificate"][
                "probability_certificates"
            ].values()
        ),
        "claim3_uniform_linear_constant": max(
            row["expert_one_step_error_upper"] / row["epsilon_q"]
            for row in raw3["epsilon_sweep"]
        )
        < 20,
        "claim3_floor_last_three": min(
            raw3["horizon_sweep"]["regret_per_H"][-3:]
        )
        >= 0.05,
        "claim3_smooth_vanishes": all(
            later["regret_per_h_upper"] < earlier["regret_per_h_upper"]
            for earlier, later in zip(
                raw3["smooth_binning_control"]["rows"],
                raw3["smooth_binning_control"]["rows"][1:],
            )
        ),
        "claim4_all_axes": (
            len({row["H"] for row in raw4["complete_formula_sweep"]}) == 3
            and len({row["n"] for row in raw4["complete_formula_sweep"]}) == 3
            and len(
                {row["epsilon_q"] for row in raw4["complete_formula_sweep"]}
            )
            == 3
            and len({row["|Pi|"] for row in raw4["complete_formula_sweep"]})
            == 3
            and all(row["includes_log_M"] for row in raw4["complete_formula_sweep"])
        ),
        "claim4_broken_realizability": raw4["broken_realizability_control"][
            "normalized_regret_floor"
        ]
        > 0,
        "claim6_binning_pair_counts": sum(
            row["pair_count"] for row in raw6["binning_pairs"]
        )
        > 10_000,
        "claim6_binning_zero": all(
            row["violations"] == 0 for row in raw6["binning_pairs"]
        ),
        "claim6_learned_persistent": min(
            row["jump"] for row in raw6["learned_piecewise_pairs"]
        )
        > 0.8,
        "claim6_source_is_literal_falsification": (
            raw6["source_result"]["status"] == "FALSIFIED"
        ),
    }
    result = {
        "checker": "independent raw-table structural and limit checks",
        "checks": checks,
        "passed": all(checks.values()),
    }
    for claim in [3, 4, 6]:
        write_json(
            ARTIFACT_ROOT / f"claim_{claim}/independent_check.json", result
        )
    if not result["passed"]:
        raise AssertionError(f"Claims 3/4/6 independent check failed: {checks}")
    return result
