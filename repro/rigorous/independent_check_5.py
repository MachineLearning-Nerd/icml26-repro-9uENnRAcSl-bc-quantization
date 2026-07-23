from __future__ import annotations

import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any

from .common import ARTIFACT_ROOT, write_json


def _load(record: dict[str, Any]) -> Fraction:
    return Fraction(record["numerator"], record["denominator"])


def _binomial_tv_by_upper_tail(
    n: int, p_numerator: int, denominator: int
) -> Fraction:
    q_numerator = denominator - p_numerator
    common = denominator**n
    difference = 0
    for k in range(n // 2 + 1, n + 1):
        p_mass = (
            math.comb(n, k)
            * p_numerator**k
            * q_numerator ** (n - k)
        )
        q_mass = (
            math.comb(n, k)
            * q_numerator**k
            * p_numerator ** (n - k)
        )
        difference += p_mass - q_mass
    return Fraction(difference, common)


def check_claim_5(raw_path: Path | None = None) -> dict[str, Any]:
    claim_dir = ARTIFACT_ROOT / "claim_5"
    if raw_path is None:
        raw_path = claim_dir / "raw_results.json"
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    t8_rows = raw["theorem_8_statistical"]["rows"]
    t8_exact = []
    for row in t8_rows:
        delta = _load(row["delta"])
        affinity = _load(row["one_sample_affinity"])
        product_affinity = _load(row["product_affinity"])
        exact_tv = _load(row["exact_product_tv"])
        t8_exact.append(
            affinity == 1 - delta
            and _load(row["hellinger_squared"]) == 2 * delta
            and product_affinity == affinity ** row["n"]
            and exact_tv == 1 - product_affinity
            and _load(row["le_cam_lower"])
            == delta * row["horizon"] * (1 - exact_tv) / 4
        )

    unique_t9: dict[int, dict[str, Any]] = {}
    for row in raw["theorem_9_statistical"]["rows"]:
        unique_t9.setdefault(row["n"], row)
    t9_recomputed = {}
    t9_checks = []
    for n, row in unique_t9.items():
        denominator = row["p"]["denominator"]
        numerator = row["p"]["numerator"]
        tv = _binomial_tv_by_upper_tail(n, numerator, denominator)
        t9_recomputed[str(n)] = _load_fraction_for_json(tv)
        delta = _load(row["delta"])
        bound_squared = 1 - (1 - 4 * delta * delta) ** n
        t9_checks.append(
            tv == _load(row["exact_binomial_tv"])
            and tv * tv <= bound_squared
            and (1 - tv) / 4 >= Fraction(1, 8)
        )

    collision_checks = [
        row["q_0_equals_q_epsilon"]
        and row["q_1_minus_epsilon_equals_q_1"]
        and _load(row["paper_four_instance_lower"])
        == Fraction(row["horizon"]) * _load(row["epsilon_q"]) / 4
        for row in raw["theorem_8_quantization"]["rows"]
    ]
    additive_checks = [
        _load(row["combined_threshold"])
        == _load(row["statistical_threshold"])
        + _load(row["quantization_threshold"])
        for row in raw["theorem_9_quantization"]["rows"]
    ]
    checks = {
        "theorem_8_rational_identities": all(t8_exact),
        "theorem_8_collision_constants": all(collision_checks),
        "theorem_8_broken_control": all(
            not row["q_0_equals_q_epsilon"]
            for row in raw["theorem_8_quantization"][
                "broken_bin_width_negative_control"
            ]
        ),
        "theorem_9_independent_upper_tail_enumeration": all(t9_checks),
        "theorem_9_additive_threshold": all(additive_checks),
        "legacy_not_counterexample": (
            raw["legacy_contradiction"]["observed_regret"]
            < raw["legacy_contradiction"]["displayed_floor"]
            and not raw["legacy_contradiction"][
                "valid_assumption_counterexample"
            ]
        ),
        "no_vacuous_acceptance": (
            not raw["non_vacuity_control"]["accepted_as_evidence"]
        ),
    }
    result = {
        "claim": 5,
        "checker": (
            "independent exact-rational identities and binomial upper-tail TV"
        ),
        "checks": checks,
        "recomputed_theorem_9_tv": t9_recomputed,
        "passed": bool(all(checks.values())),
    }
    write_json(claim_dir / "independent_check.json", result)
    if not result["passed"]:
        raise AssertionError(f"Claim 5 independent check failed: {checks}")
    return result


def _load_fraction_for_json(value: Fraction) -> dict[str, Any]:
    return {
        "numerator": value.numerator,
        "denominator": value.denominator,
        "decimal": float(value),
    }
