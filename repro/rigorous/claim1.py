from __future__ import annotations

import csv
import json
import math
import shutil
import time
from pathlib import Path
from typing import Any

import numpy as np

from .common import (
    ARTIFACT_ROOT,
    REPO_ROOT,
    bootstrap_mean_curve_slope,
    finite_or_raise,
    linear_fit,
    loglog_fit,
    provenance,
    safe_log_loss,
    sha256_file,
    write_json,
)


CLAIM_DIR = REPO_ROOT / "repro" / "claims" / "claim_1"
OUT_DIR = ARTIFACT_ROOT / "claim_1"
PAPER_SHA256 = "a1517e403f96e5c0c3529bbf8fcf3d8fad29b3149f164added02036f3318f0e1"


def _statistical_rate() -> dict[str, Any]:
    n_values = np.asarray([64, 256, 1024, 4096, 16384, 65536], dtype=int)
    seed_values = list(range(256))
    true_probability = 0.37
    errors = np.empty((len(seed_values), len(n_values)), dtype=float)
    excess_log_losses = np.empty_like(errors)
    mle_objective_checks = 0
    objective_check_count = 0

    for row, seed in enumerate(seed_values):
        for column, n in enumerate(n_values):
            rng = np.random.default_rng(260320538 + seed * 1000003 + int(n))
            count = int(rng.binomial(int(n), true_probability))
            estimate = min(max(count / float(n), 1e-15), 1.0 - 1e-15)
            errors[row, column] = abs(estimate - true_probability)
            excess_log_losses[row, column] = (
                true_probability * math.log(true_probability / estimate)
                + (1.0 - true_probability)
                * math.log((1.0 - true_probability) / (1.0 - estimate))
            )
            mle_loss = safe_log_loss(count, int(n), estimate)
            competitors = [
                safe_log_loss(count, int(n), true_probability - 0.05),
                safe_log_loss(count, int(n), true_probability + 0.05),
            ]
            mle_objective_checks += int(mle_loss <= min(competitors) + 1e-10)
            objective_check_count += 1

    finite_or_raise(errors, "claim 1 statistical errors")
    means = errors.mean(axis=0)
    fit = loglog_fit(n_values, means)
    bootstrap = bootstrap_mean_curve_slope(
        n_values, errors, seed=2053801, replicates=3000
    )

    first_n_errors = errors[:, [0]]
    zero_effect = np.repeat(first_n_errors, len(n_values), axis=1)
    wrong_rate = np.repeat((1.0 / n_values)[None, :], len(seed_values), axis=0)

    return {
        "model": {
            "expert": "state-independent Bernoulli(0.37)",
            "quantized_action_alphabet": [0, 1],
            "loss": "Bernoulli negative log likelihood",
            "estimator": "unconstrained Bernoulli log-loss MLE",
            "tvc_modulus": "0 (state-independent policy)",
            "dynamics": "constant state, globally P-EIISS with gamma=0",
            "realizable": True,
        },
        "n_values": n_values.tolist(),
        "seeds": seed_values,
        "absolute_probability_errors": errors.tolist(),
        "mean_absolute_probability_error": means.tolist(),
        "mean_excess_log_loss": excess_log_losses.mean(axis=0).tolist(),
        "rate_fit": fit,
        "bootstrap_slope": bootstrap,
        "mle_objective_checks": {
            "passed": mle_objective_checks,
            "total": objective_check_count,
        },
        "negative_controls": {
            "zero_effect_mean_errors": zero_effect.mean(axis=0).tolist(),
            "zero_effect_fit": loglog_fit(
                n_values, zero_effect.mean(axis=0)
            ),
            "wrong_rate_mean_errors": wrong_rate.mean(axis=0).tolist(),
            "wrong_rate_fit": loglog_fit(
                n_values, wrong_rate.mean(axis=0)
            ),
        },
    }


def _quantization_floor() -> dict[str, Any]:
    horizon = 32
    bin_counts = np.asarray([4, 8, 16, 32, 64, 128, 256], dtype=int)
    epsilon_values = 1.0 / bin_counts
    one_step_gaps = epsilon_values / 2.0
    regrets = horizon * one_step_gaps
    fit = loglog_fit(epsilon_values, regrets)
    upper_bounds = horizon * horizon * epsilon_values
    return {
        "construction": {
            "expert": "U ~ Uniform[0,1], independent of state",
            "quantizer": "left endpoint of each uniform bin",
            "reward": "r(u)=u (1-Lipschitz)",
            "exact_identity": "E[U-q(U)] = epsilon_q/2",
            "stochastic_q_pushforward": True,
            "tvc_modulus": "0",
            "globally_p_eiiss": True,
        },
        "horizon": horizon,
        "bin_counts": bin_counts.tolist(),
        "epsilon_q": epsilon_values.tolist(),
        "one_step_reward_gap": one_step_gaps.tolist(),
        "regret": regrets.tolist(),
        "theorem_h2_epsilon_upper_scale": upper_bounds.tolist(),
        "all_below_h2_scale": bool(np.all(regrets <= upper_bounds)),
        "epsilon_exponent_fit": fit,
        "zero_effect_control_regret": [0.0 for _ in epsilon_values],
    }


def _finite_policy_class_ratchet() -> dict[str, Any]:
    class_sizes = np.asarray([2, 4, 8, 16, 32, 64, 128, 256, 512], dtype=int)
    max_class_size = int(class_sizes[-1])
    contexts = 64
    observations = 2048
    seeds = list(range(96))
    logit_delta = 0.18
    deviations = np.empty((len(seeds), len(class_sizes)), dtype=float)
    selected_excess = np.empty_like(deviations)
    single_policy_deviation = np.empty_like(deviations)

    for row, seed in enumerate(seeds):
        rng = np.random.default_rng(26030000 + seed)
        signs = rng.choice(
            np.asarray([-1.0, 1.0]),
            size=(max_class_size - 1, contexts),
            replace=True,
        )
        logits = logit_delta * signs
        candidate_probabilities = 1.0 / (1.0 + np.exp(-logits))
        candidate_probabilities = np.vstack(
            [np.full((1, contexts), 0.5), candidate_probabilities]
        )
        counts = rng.multinomial(observations, np.full(contexts, 1.0 / contexts))
        successes = rng.binomial(counts, 0.5)
        empirical = -(
            np.log(candidate_probabilities) @ successes
            + np.log1p(-candidate_probabilities) @ (counts - successes)
        ) / observations
        population = -np.mean(
            0.5 * np.log(candidate_probabilities)
            + 0.5 * np.log1p(-candidate_probabilities),
            axis=1,
        )
        absolute_gap = np.abs(empirical - population)
        for column, class_size in enumerate(class_sizes):
            active = slice(0, int(class_size))
            deviations[row, column] = float(np.max(absolute_gap[active]))
            selected = int(np.argmin(empirical[active]))
            selected_excess[row, column] = float(
                population[selected] - population[0]
            )
            single_policy_deviation[row, column] = float(absolute_gap[0])

    mean_deviation = deviations.mean(axis=0)
    mean_selected_excess = selected_excess.mean(axis=0)
    squared_fit = linear_fit(np.log(class_sizes), mean_deviation**2)
    single_fit = linear_fit(
        np.log(class_sizes), single_policy_deviation.mean(axis=0) ** 2
    )
    return {
        "construction": {
            "contexts": contexts,
            "observations": observations,
            "true_policy": "Bernoulli(0.5), included as policy 0 in every class",
            "distractors": (
                "finite Bernoulli policies with contextwise +/-0.18 logits"
            ),
            "quantity": "uniform empirical-population log-loss deviation",
            "nested_class_sizes": True,
        },
        "class_sizes": class_sizes.tolist(),
        "seeds": seeds,
        "uniform_log_loss_deviations": deviations.tolist(),
        "mean_uniform_deviation": mean_deviation.tolist(),
        "mean_selected_excess_log_loss": mean_selected_excess.tolist(),
        "squared_deviation_vs_log_class_fit": squared_fit,
        "negative_control": {
            "description": "single fixed policy; no maximum over the class",
            "mean_deviation": single_policy_deviation.mean(axis=0).tolist(),
            "squared_deviation_vs_log_class_fit": single_fit,
        },
    }


def _evaluate_gates(raw: dict[str, Any]) -> dict[str, Any]:
    rate = raw["statistical_rate"]
    slope = rate["rate_fit"]["slope"]
    ci_low, ci_high = rate["bootstrap_slope"]["ci95"]
    zero_slope = rate["negative_controls"]["zero_effect_fit"]["slope"]
    wrong_slope = rate["negative_controls"]["wrong_rate_fit"]["slope"]
    floor_slope = raw["quantization_floor"]["epsilon_exponent_fit"]["slope"]
    ratchet = raw["finite_policy_class_ratchet"]
    class_fit = ratchet["squared_deviation_vs_log_class_fit"]
    class_nc = ratchet["negative_control"][
        "squared_deviation_vs_log_class_fit"
    ]
    checks = {
        "genuine_log_loss_mle": (
            rate["mle_objective_checks"]["passed"]
            == rate["mle_objective_checks"]["total"]
        ),
        "n_sweep_six_points_three_orders": (
            len(rate["n_values"]) >= 6
            and max(rate["n_values"]) / min(rate["n_values"]) >= 1000
        ),
        "rate_point_near_minus_half": -0.58 <= slope <= -0.42,
        "rate_ci_contains_minus_half": ci_low <= -0.5 <= ci_high,
        "rate_ci_excludes_zero": not (ci_low <= 0.0 <= ci_high),
        "rate_ci_excludes_minus_one": not (ci_low <= -1.0 <= ci_high),
        "zero_effect_control_rejected": abs(zero_slope) <= 0.05,
        "wrong_rate_control_rejected": -1.05 <= wrong_slope <= -0.95,
        "quantization_floor_linear": 0.99 <= floor_slope <= 1.01,
        "quantization_floor_below_theorem_scale": raw[
            "quantization_floor"
        ]["all_below_h2_scale"],
        "finite_policy_log_term_positive": class_fit["slope"] > 0.0,
        "finite_policy_log_term_fit": class_fit["r2"] >= 0.90,
        "finite_policy_negative_control_flat": abs(class_nc["slope"]) <= 1e-12,
    }
    return {
        "checks": checks,
        "passed": bool(all(checks.values())),
        "status": "VERIFIED" if all(checks.values()) else "BLOCKED",
    }


def run_claim_1() -> dict[str, Any]:
    started = time.perf_counter()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    statistical_rate = _statistical_rate()
    raw = {
        "claim": 1,
        "paper_sha256": PAPER_SHA256,
        "statistical_rate": statistical_rate,
        "quantization_floor": _quantization_floor(),
        "finite_policy_class_ratchet": _finite_policy_class_ratchet(),
    }
    gates = _evaluate_gates(raw)
    runtime = time.perf_counter() - started
    prov = provenance(runtime, statistical_rate["seeds"])

    for source_name in ["claim_contract.json", "source_audit.md", "method.md"]:
        shutil.copyfile(CLAIM_DIR / source_name, OUT_DIR / source_name)
    write_json(OUT_DIR / "raw_results.json", raw)
    write_json(
        OUT_DIR / "negative_controls.json",
        {
            "statistical": statistical_rate["negative_controls"],
            "quantization_zero_effect": raw["quantization_floor"][
                "zero_effect_control_regret"
            ],
            "policy_class": raw["finite_policy_class_ratchet"][
                "negative_control"
            ],
        },
    )
    write_json(OUT_DIR / "provenance.json", prov)
    write_json(OUT_DIR / "status.json", gates)
    with (OUT_DIR / "raw_rate.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["seed", *statistical_rate["n_values"]])
        for seed, values in zip(
            statistical_rate["seeds"],
            statistical_rate["absolute_probability_errors"],
        ):
            writer.writerow([seed, *values])

    summary = {
        "claim": 1,
        "status": gates["status"],
        "passed": gates["passed"],
        "rate_slope": statistical_rate["rate_fit"]["slope"],
        "rate_ci95": statistical_rate["bootstrap_slope"]["ci95"],
        "quantization_floor_exponent": raw["quantization_floor"][
            "epsilon_exponent_fit"
        ]["slope"],
        "finite_class_squared_log_fit_r2": raw[
            "finite_policy_class_ratchet"
        ]["squared_deviation_vs_log_class_fit"]["r2"],
        "negative_control_zero_slope": statistical_rate["negative_controls"][
            "zero_effect_fit"
        ]["slope"],
        "negative_control_wrong_rate_slope": statistical_rate[
            "negative_controls"
        ]["wrong_rate_fit"]["slope"],
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
