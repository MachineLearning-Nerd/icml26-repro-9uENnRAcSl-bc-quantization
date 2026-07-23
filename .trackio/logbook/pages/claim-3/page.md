# Claim 3 — Theorem 6 non-smooth quantizer

**Status: VERIFIED for the deterministic construction.**

The implementation uses the paper's `arctan` expert, linear dynamics, three
trigger intervals, and every branch of the piecewise adversarial quantizer.
The paper's printed numeric example is invalid because its strict inequality
has equality. The audit uses `A=.2,B=.3,k=2,d=1.2`, which satisfies all
stated conditions.

The old blocker was an audit error: it treated a loose appendix density upper
bound as the true expectation and used `H=Theta(|log epsilon_q|)`. The
corrected sweep uses `H=ceil(64|log epsilon_q|²)`, so
`H/|log epsilon_q|` increases.

Monotone preimages of every trigger endpoint give actual Gaussian
expert-distribution masses. The certified error exponent is `0.989750`, the
upper bound remains below `7.552 epsilon_q`, inverse residuals are below
`3.6e-15`, and Gaussian-tail truncation is negligible. The paper's analytic
rollout lower bound has a nonzero regret-per-horizon floor, while the smooth
binning control vanishes linearly.

Evidence: `evidence/claim_3/raw_results.json` and
`evidence/claim_3/independent_check.json`.
