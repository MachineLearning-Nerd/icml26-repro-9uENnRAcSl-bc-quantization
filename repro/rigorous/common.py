from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_ROOT = REPO_ROOT / ".openresearch" / "artifacts"
FIXED_COMMAND = "uv run --frozen python repro/src/verify_bc.py"


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, allow_nan=False) + "\n"


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_json(data), encoding="utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_sha() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True
    ).strip()


def provenance(runtime_seconds: float, seeds: Iterable[int]) -> dict[str, Any]:
    return {
        "command": FIXED_COMMAND,
        "git_sha": git_sha(),
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "cpu_count": os.cpu_count(),
        "runtime_seconds": runtime_seconds,
        "seeds": list(seeds),
        "hardware_policy": "CPU only; GPU use prohibited",
    }


def linear_fit(x: Iterable[float], y: Iterable[float]) -> dict[str, float]:
    x_arr = np.asarray(list(x), dtype=float)
    y_arr = np.asarray(list(y), dtype=float)
    slope, intercept = np.polyfit(x_arr, y_arr, 1)
    fitted = intercept + slope * x_arr
    residual = float(np.sum((y_arr - fitted) ** 2))
    total = float(np.sum((y_arr - np.mean(y_arr)) ** 2))
    r2 = 1.0 if total == 0.0 and residual == 0.0 else 1.0 - residual / total
    return {
        "slope": float(slope),
        "intercept": float(intercept),
        "residual_sum_squares": residual,
        "r2": float(r2),
    }


def loglog_fit(x: Iterable[float], y: Iterable[float]) -> dict[str, float]:
    x_arr = np.asarray(list(x), dtype=float)
    y_arr = np.asarray(list(y), dtype=float)
    if np.any(x_arr <= 0) or np.any(y_arr <= 0):
        raise ValueError("log-log inputs must be positive")
    return linear_fit(np.log(x_arr), np.log(y_arr))


def bootstrap_mean_curve_slope(
    x_values: np.ndarray,
    errors: np.ndarray,
    *,
    seed: int,
    replicates: int,
) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    slopes = np.empty(replicates, dtype=float)
    seed_count = errors.shape[0]
    log_x = np.log(x_values.astype(float))
    for index in range(replicates):
        sampled = rng.integers(0, seed_count, size=seed_count)
        curve = errors[sampled].mean(axis=0)
        slopes[index] = np.polyfit(log_x, np.log(curve), 1)[0]
    return {
        "replicates": replicates,
        "seed": seed,
        "ci95": [
            float(np.quantile(slopes, 0.025)),
            float(np.quantile(slopes, 0.975)),
        ],
        "median": float(np.median(slopes)),
    }


def finite_or_raise(values: np.ndarray, name: str) -> None:
    if not np.all(np.isfinite(values)):
        raise AssertionError(f"{name} contains a non-finite value")


def safe_log_loss(count: int, n: int, probability: float) -> float:
    p = min(max(probability, 1e-15), 1.0 - 1e-15)
    return -(count * math.log(p) + (n - count) * math.log1p(-p))
