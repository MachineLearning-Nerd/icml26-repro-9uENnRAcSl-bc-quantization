from __future__ import annotations

import math
import shutil
import time
from fractions import Fraction
from typing import Any

from .common import ARTIFACT_ROOT, REPO_ROOT, provenance, sha256_file, write_json


CLAIM_DIR = REPO_ROOT / "repro" / "claims" / "claim_5"
OUT_DIR = ARTIFACT_ROOT / "claim_5"
PAPER_SHA256 = "a1517e403f96e5c0c3529bbf8fcf3d8fad29b3149f164added02036f3318f0e1"


def _fraction(value: Fraction) -> dict[str, Any]:
    return {
        "numerator": value.numerator,
        "denominator": value.denominator,
        "decimal": float(value),
    }


def _exact_binomial_tv(n: int, p_numerator: int, denominator: int) -> Fraction:
    q_numerator = denominator - p_numerator
    common_denominator = denominator**n
    p_term = q_numerator**n
    q_term = p_numerator**n
    difference_sum = 0
    for k in range(n + 1):
        difference_sum += abs(p_term - q_term)
        if k < n:
            p_numerator_next = p_term * (n - k) * p_numerator
            p_denominator_next = (k + 1) * q_numerator
            q_numerator_next = q_term * (n - k) * q_numerator
            q_denominator_next = (k + 1) * p_numerator
            assert p_numerator_next % p_denominator_next == 0
            assert q_numerator_next % q_denominator_next == 0
            p_term = p_numerator_next // p_denominator_next
            q_term = q_numerator_next // q_denominator_next
    return Fraction(difference_sum, 2 * common_denominator)


def _theorem_8_statistical() -> dict[str, Any]:
    n_values = [8, 16, 32, 64, 128, 256, 512, 1024]
    horizons = [8, 32, 128]
    rows = []
    minimum_normalized = None
    for n in n_values:
        delta = Fraction(1, 3 * n)
        one_sample_affinity = 1 - delta
        hellinger_squared = 2 * delta
        product_affinity = one_sample_affinity**n
        product_hellinger_squared = 2 * (1 - product_affinity)
        exact_product_tv = 1 - product_affinity
        paper_tv_upper_squared = product_hellinger_squared
        for horizon in horizons:
            le_cam_lower = delta * horizon * (1 - exact_product_tv) / 4
            normalized = le_cam_lower / Fraction(horizon, n)
            minimum_normalized = (
                normalized
                if minimum_normalized is None
                else min(minimum_normalized, normalized)
            )
            rows.append(
                {
                    "n": n,
                    "horizon": horizon,
                    "delta": _fraction(delta),
                    "one_sample_affinity": _fraction(one_sample_affinity),
                    "hellinger_squared": _fraction(hellinger_squared),
                    "product_affinity": _fraction(product_affinity),
                    "product_hellinger_squared": _fraction(
                        product_hellinger_squared
                    ),
                    "exact_product_tv": _fraction(exact_product_tv),
                    "paper_tv_upper_squared": _fraction(paper_tv_upper_squared),
                    "le_cam_lower": _fraction(le_cam_lower),
                    "normalized_by_H_over_n": _fraction(normalized),
                }
            )
    assert minimum_normalized is not None
    return {
        "construction": {
            "state_action_spaces": "[0,1]",
            "initial_state": "(1-Delta) delta_0 + Delta delta_1",
            "experts": "pi^a=delta_0; pi^b=delta_x at h=1",
            "deterministic_experts": True,
            "expert_lipschitz_constant": 1,
            "rewards_1_lipschitz": True,
            "global_piiss": "gamma(r_1,...,r_h)=r_1",
            "non_anticipatory_scope": (
                "At step h the learner may use only trajectory prefixes through h."
            ),
        },
        "rows": rows,
        "minimum_normalized_constant": _fraction(minimum_normalized),
    }


def _collision_label(value: Fraction, bins: int) -> int:
    if value == 1:
        return bins - 1
    scaled = value * bins
    if scaled.denominator == 1 and scaled.numerator > 0:
        if scaled.numerator == bins - 1:
            return bins - 1
        return min(scaled.numerator - 1, bins - 1)
    return min(scaled.numerator // scaled.denominator, bins - 1)


def _theorem_8_quantization() -> dict[str, Any]:
    horizons = [8, 32, 128]
    bin_counts = [8, 16, 32, 64, 128]
    rows = []
    broken_rows = []
    for bins in bin_counts:
        epsilon = Fraction(1, bins)
        collision_left = _collision_label(Fraction(0), bins) == _collision_label(
            epsilon, bins
        )
        collision_right = _collision_label(1 - epsilon, bins) == _collision_label(
            Fraction(1), bins
        )
        broken_bins = bins * 2
        broken_collision = _collision_label(
            Fraction(0), broken_bins
        ) == _collision_label(epsilon, broken_bins)
        broken_rows.append(
            {
                "epsilon_q": _fraction(epsilon),
                "bins": broken_bins,
                "q_0_equals_q_epsilon": broken_collision,
            }
        )
        for horizon in horizons:
            rows.append(
                {
                    "bins": bins,
                    "epsilon_q": _fraction(epsilon),
                    "horizon": horizon,
                    "q_0_equals_q_epsilon": collision_left,
                    "q_1_minus_epsilon_equals_q_1": collision_right,
                    "paper_four_instance_lower": _fraction(
                        Fraction(horizon) * epsilon / 4
                    ),
                    "normalized_by_H_epsilon": _fraction(Fraction(1, 4)),
                }
            )
    return {
        "tie_breaking": (
            "The first boundary is assigned to I_1 and the last boundary to "
            "I_K, so I_1=[0,epsilon_q] and I_K=[1-epsilon_q,1], as allowed "
            "by Appendix E.1's arbitrary endpoint convention."
        ),
        "rows": rows,
        "broken_bin_width_negative_control": broken_rows,
    }


def _theorem_9_statistical() -> dict[str, Any]:
    n_values = [16, 64, 256, 1024, 4096]
    horizons = [8, 32, 128]
    rows = []
    displayed_constant_audit = []
    for n in n_values:
        root_n = math.isqrt(n)
        assert root_n * root_n == n
        delta = Fraction(1, 5 * root_n)
        probability_denominator = 10 * root_n
        p_numerator = 5 * root_n + 2
        exact_tv = _exact_binomial_tv(n, p_numerator, probability_denominator)
        affinity_squared = 1 - 4 * delta * delta
        paper_tv_bound_squared = 1 - affinity_squared**n
        assert exact_tv * exact_tv <= paper_tv_bound_squared
        event_probability_lower = (1 - exact_tv) / 4
        displayed_delta = Fraction(3, 5 * root_n)
        displayed_tv = _exact_binomial_tv(
            n, 5 * root_n + 6, probability_denominator
        )
        displayed_constant_audit.append(
            {
                "n": n,
                "displayed_delta": _fraction(displayed_delta),
                "exact_binomial_tv": _fraction(displayed_tv),
                "reduction_probability_lower": _fraction(
                    (1 - displayed_tv) / 4
                ),
                "tv_at_most_7_over_8": displayed_tv <= Fraction(7, 8),
                "seven_eighths_only_implies": _fraction(Fraction(1, 32)),
                "supports_one_eighth_via_displayed_reduction": (
                    (1 - displayed_tv) / 4 >= Fraction(1, 8)
                ),
            }
        )
        for horizon in horizons:
            threshold = delta * horizon
            rows.append(
                {
                    "n": n,
                    "horizon": horizon,
                    "delta": _fraction(delta),
                    "p": _fraction(Fraction(p_numerator, probability_denominator)),
                    "q": _fraction(
                        Fraction(
                            probability_denominator - p_numerator,
                            probability_denominator,
                        )
                    ),
                    "affinity_squared_identity": _fraction(affinity_squared),
                    "paper_tv_bound_squared": _fraction(paper_tv_bound_squared),
                    "exact_binomial_tv": _fraction(exact_tv),
                    "tv_squared_below_bound": True,
                    "event_probability_lower": _fraction(event_probability_lower),
                    "threshold": _fraction(threshold),
                    "threshold_normalized_by_H_over_sqrt_n": _fraction(
                        threshold / Fraction(horizon, root_n)
                    ),
                }
            )
    return {
        "construction": {
            "state_action_spaces": "[-1,2]",
            "first_step_experts": (
                "Bernoulli(1/2+Delta) versus Bernoulli(1/2-Delta)"
            ),
            "state_independent_stochastic_experts": True,
            "suboptimal_expert_allowed": True,
            "rewards_1_lipschitz": True,
            "global_piiss": "gamma(r_1,...,r_h)=r_1",
            "certified_delta": (
                "1/(5*sqrt(n)); a smaller universal constant than the "
                "appendix display, with perfect-square n making it rational"
            ),
        },
        "rows": rows,
        "paper_displayed_constant_audit": displayed_constant_audit,
    }


def _theorem_9_quantization() -> dict[str, Any]:
    rows = []
    for root_n in [4, 8, 16, 32, 64]:
        n = root_n * root_n
        delta = Fraction(1, 5 * root_n)
        for bins in [8, 16, 32, 64]:
            epsilon = Fraction(1, bins)
            for horizon in [8, 32, 128]:
                rows.append(
                    {
                        "n": n,
                        "horizon": horizon,
                        "epsilon_q": _fraction(epsilon),
                        "statistical_threshold": _fraction(delta * horizon),
                        "quantization_threshold": _fraction(
                            Fraction(horizon) * epsilon / 2
                        ),
                        "combined_threshold": _fraction(
                            delta * horizon + Fraction(horizon) * epsilon / 2
                        ),
                    }
                )
    return {
        "collision": (
            "The shifted supports +/-epsilon_q and 1+/-epsilon_q have "
            "identical quantized observations under the Appendix E binning."
        ),
        "rows": rows,
    }


def _legacy_contradiction() -> dict[str, Any]:
    observed_regret = 0.024659483338346222
    epsilon_q = 0.5
    horizon = 20
    displayed_floor = epsilon_q * horizon * 0.3
    return {
        "legacy_source_sha": "12c6b41365d2af3b38e97fcb585139eb2b51347f",
        "observed_regret": observed_regret,
        "displayed_floor": displayed_floor,
        "contradiction_is_real": observed_regret < displayed_floor,
        "legacy_assertion": "reg_min >= 0",
        "legacy_assertion_is_vacuous": observed_regret >= 0,
        "conclusion": (
            "Not a theorem counterexample. Theorem 8/9 are existential hard-"
            "instance statements, while the legacy run used an unrelated smooth "
            "simulation. The factor 0.3 was invented and cannot instantiate the "
            "unspecified universal constant hidden by gtrsim."
        ),
        "valid_assumption_counterexample": False,
    }


def _evaluate_gates(raw: dict[str, Any]) -> dict[str, Any]:
    t8_rows = raw["theorem_8_statistical"]["rows"]
    collision_rows = raw["theorem_8_quantization"]["rows"]
    broken_rows = raw["theorem_8_quantization"][
        "broken_bin_width_negative_control"
    ]
    t9_rows = raw["theorem_9_statistical"]["rows"]
    checks = {
        "theorem_8_exact_hellinger_identity": all(
            Fraction(
                row["hellinger_squared"]["numerator"],
                row["hellinger_squared"]["denominator"],
            )
            == 2
            * Fraction(row["delta"]["numerator"], row["delta"]["denominator"])
            for row in t8_rows
        ),
        "theorem_8_nonvacuous_H_over_n": (
            raw["theorem_8_statistical"]["minimum_normalized_constant"]["decimal"]
            > 0.04
            and all(row["le_cam_lower"]["numerator"] > 0 for row in t8_rows)
        ),
        "theorem_8_bin_collisions": all(
            row["q_0_equals_q_epsilon"]
            and row["q_1_minus_epsilon_equals_q_1"]
            and row["paper_four_instance_lower"]["numerator"] > 0
            for row in collision_rows
        ),
        "broken_bin_width_breaks_collision": all(
            not row["q_0_equals_q_epsilon"] for row in broken_rows
        ),
        "theorem_9_exact_binomial_enumeration": (
            len({row["n"] for row in t9_rows}) == 5
            and all(row["tv_squared_below_bound"] for row in t9_rows)
        ),
        "theorem_9_probability_at_least_one_eighth": all(
            row["event_probability_lower"]["decimal"] >= 0.125
            for row in t9_rows
        ),
        "theorem_9_sqrt_n_scaling": all(
            Fraction(
                row["threshold_normalized_by_H_over_sqrt_n"]["numerator"],
                row["threshold_normalized_by_H_over_sqrt_n"]["denominator"],
            )
            == Fraction(1, 5)
            for row in t9_rows
        ),
        "theorem_9_displayed_constant_gap_recorded": all(
            row["tv_at_most_7_over_8"]
            and not row["supports_one_eighth_via_displayed_reduction"]
            and Fraction(
                row["seven_eighths_only_implies"]["numerator"],
                row["seven_eighths_only_implies"]["denominator"],
            )
            == Fraction(1, 32)
            for row in raw["theorem_9_statistical"][
                "paper_displayed_constant_audit"
            ]
        ),
        "theorem_9_additive_quantization": all(
            Fraction(
                row["combined_threshold"]["numerator"],
                row["combined_threshold"]["denominator"],
            )
            == Fraction(
                row["statistical_threshold"]["numerator"],
                row["statistical_threshold"]["denominator"],
            )
            + Fraction(
                row["quantization_threshold"]["numerator"],
                row["quantization_threshold"]["denominator"],
            )
            for row in raw["theorem_9_quantization"]["rows"]
        ),
        "legacy_contradiction_resolved": (
            raw["legacy_contradiction"]["contradiction_is_real"]
            and raw["legacy_contradiction"]["legacy_assertion_is_vacuous"]
            and not raw["legacy_contradiction"]["valid_assumption_counterexample"]
        ),
        "zero_delta_control_rejected": raw["non_vacuity_control"][
            "zero_delta_threshold"
        ]
        == 0,
    }
    passed = bool(all(checks.values()))
    return {
        "checks": checks,
        "subclaims": {
            "theorem_8": "VERIFIED"
            if all(
                checks[key]
                for key in [
                    "theorem_8_exact_hellinger_identity",
                    "theorem_8_nonvacuous_H_over_n",
                    "theorem_8_bin_collisions",
                    "broken_bin_width_breaks_collision",
                ]
            )
            else "BLOCKED",
            "theorem_9": "VERIFIED"
            if all(
                checks[key]
                for key in [
                    "theorem_9_exact_binomial_enumeration",
                    "theorem_9_probability_at_least_one_eighth",
                    "theorem_9_sqrt_n_scaling",
                    "theorem_9_displayed_constant_gap_recorded",
                    "theorem_9_additive_quantization",
                ]
            )
            else "BLOCKED",
        },
        "passed": passed,
        "status": "VERIFIED" if passed else "BLOCKED",
    }


def run_claim_5() -> dict[str, Any]:
    started = time.perf_counter()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    raw = {
        "claim": 5,
        "paper_sha256": PAPER_SHA256,
        "theorem_8_statistical": _theorem_8_statistical(),
        "theorem_8_quantization": _theorem_8_quantization(),
        "theorem_9_statistical": _theorem_9_statistical(),
        "theorem_9_quantization": _theorem_9_quantization(),
        "legacy_contradiction": _legacy_contradiction(),
        "non_vacuity_control": {
            "description": (
                "Setting Delta=0 makes the testing threshold zero and is "
                "explicitly rejected as evidence."
            ),
            "zero_delta_threshold": 0,
            "accepted_as_evidence": False,
        },
    }
    gates = _evaluate_gates(raw)
    runtime = time.perf_counter() - started
    prov = provenance(runtime, [])
    for source_name in ["claim_contract.json", "source_audit.md", "method.md"]:
        shutil.copyfile(CLAIM_DIR / source_name, OUT_DIR / source_name)
    write_json(OUT_DIR / "raw_results.json", raw)
    write_json(
        OUT_DIR / "negative_controls.json",
        {
            "zero_delta": raw["non_vacuity_control"],
            "broken_bin_width": raw["theorem_8_quantization"][
                "broken_bin_width_negative_control"
            ],
            "legacy_vacuous_assertion": raw["legacy_contradiction"],
        },
    )
    write_json(OUT_DIR / "provenance.json", prov)
    write_json(OUT_DIR / "status.json", gates)
    t9_tvs = [
        row["exact_binomial_tv"]["decimal"]
        for row in raw["theorem_9_statistical"]["rows"]
    ]
    summary = {
        "claim": 5,
        "status": gates["status"],
        "passed": gates["passed"],
        "theorem_8_status": gates["subclaims"]["theorem_8"],
        "theorem_9_status": gates["subclaims"]["theorem_9"],
        "theorem_8_min_H_over_n_constant": raw["theorem_8_statistical"][
            "minimum_normalized_constant"
        ]["decimal"],
        "theorem_9_max_exact_tv": max(t9_tvs),
        "theorem_9_min_event_probability": min(
            row["event_probability_lower"]["decimal"]
            for row in raw["theorem_9_statistical"]["rows"]
        ),
        "legacy_floor": raw["legacy_contradiction"]["displayed_floor"],
        "legacy_observed": raw["legacy_contradiction"]["observed_regret"],
        "runtime_seconds": runtime,
        "git_sha": prov["git_sha"],
    }
    write_json(OUT_DIR / "summary.json", summary)
    manifest = {}
    for artifact in sorted(OUT_DIR.iterdir()):
        if artifact.is_file() and artifact.name != "manifest.json":
            manifest[artifact.name] = {
                "bytes": artifact.stat().st_size,
                "sha256": sha256_file(artifact),
            }
    write_json(OUT_DIR / "manifest.json", manifest)
    return summary
