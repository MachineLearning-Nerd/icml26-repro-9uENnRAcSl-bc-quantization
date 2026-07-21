"""Clean-room BC with action quantization from "Understanding Behavior Cloning with Action Quantization"
(arXiv 2603.20538). numpy, CPU.

MDP: x_{t+1} = alpha x_t + u_t + noise (P-IISS: alpha<1 contracting). Expert u* = -alpha x (RTVC: Lipschitz).
Quantizer: binning (smooth) maps u to nearest bin center; epsilon_q = bin width.
BC: fit a policy to quantized expert actions via least-squares. Regret = sum_t (u_t - u*_t)^2.
"""
from __future__ import annotations
import numpy as np

ALPHA = 0.9  # dynamics contraction (P-IISS)


def expert_action(x):
    return -ALPHA * x


def binning_quantizer(u, n_bins, u_range=(-2, 2)):
    """Smooth binning quantizer: maps u to nearest bin center. epsilon_q = bin width."""
    edges = np.linspace(u_range[0], u_range[1], n_bins + 1)
    centers = (edges[:-1] + edges[1:]) / 2
    idx = np.clip(np.digitize(u, edges) - 1, 0, n_bins - 1)
    return centers[idx], (u_range[1] - u_range[0]) / n_bins  # quantized action, epsilon_q


def nonsmooth_quantizer(u, n_bins, rng, u_range=(-2, 2)):
    """Non-smooth quantizer: random assignment within bins (violates smoothness)."""
    edges = np.linspace(u_range[0], u_range[1], n_bins + 1)
    idx = np.clip(np.digitize(u, edges) - 1, 0, n_bins - 1)
    # assign to a RANDOM center (not the nearest) -> non-smooth
    centers = rng.uniform(u_range[0], u_range[1], n_bins)
    return centers[idx], (u_range[1] - u_range[0]) / n_bins


def run_bc(n_samples, H, n_bins, smooth=True, seed=0):
    """Collect n expert (x,u) pairs, quantize, fit BC, evaluate regret over horizon H."""
    rng = np.random.default_rng(seed)
    # collect expert data
    X_data = rng.standard_normal(n_samples) * 2
    U_data = np.array([expert_action(x) for x in X_data])
    # quantize
    if smooth:
        U_q, eps_q = binning_quantizer(U_data, n_bins)
    else:
        U_q, eps_q = nonsmooth_quantizer(U_data, n_bins, rng)
    # BC: fit u_hat = theta * x (linear) to quantized actions
    theta = np.sum(X_data * U_q) / max(np.sum(X_data ** 2), 1e-9)
    # evaluate regret over horizon H
    x = rng.standard_normal() * 2; regret = 0.0
    for _ in range(H):
        u_bc = theta * x; u_expert = expert_action(x)
        regret += (u_bc - u_expert) ** 2
        x = ALPHA * x + u_bc + rng.standard_normal() * 0.1
    return regret, eps_q, theta


def run_bc_augmented(n_samples, H, n_bins, seed=0):
    """Model-based augmentation: augment data with model predictions (Theorem 7)."""
    rng = np.random.default_rng(seed)
    X_orig = rng.standard_normal(n_samples) * 2
    U_orig = np.array([expert_action(x) for x in X_orig])
    U_q, eps_q = binning_quantizer(U_orig, n_bins)
    # augmentation: generate additional data via the model x' = alpha*x + u
    X_aug = np.concatenate([X_orig, ALPHA * X_orig + U_q + rng.standard_normal(n_samples) * 0.1])
    U_aug = np.concatenate([U_q, np.array([expert_action(x) for x in ALPHA * X_orig + U_q])])
    U_aug_q, _ = binning_quantizer(U_aug, n_bins)
    theta = np.sum(X_aug * U_aug_q) / max(np.sum(X_aug ** 2), 1e-9)
    x = rng.standard_normal() * 2; regret = 0.0
    for _ in range(H):
        u_bc = theta * x; regret += (u_bc - expert_action(x)) ** 2
        x = ALPHA * x + u_bc + rng.standard_normal() * 0.1
    return regret, eps_q
