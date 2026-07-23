# Claim 1 — Theorem 2 sample complexity

**Status: VERIFIED.**

The tested finite class contains the true stochastic Bernoulli policy.
State-independent policies certify TVC with zero modulus and constant dynamics
certify global P-EIISS. Behavior cloning is the exact Bernoulli log-loss MLE,
not training MSE.

Across `n=64,...,65536` and 256 deterministic seeds, the total-variation
error exponent is `-0.499193`; its bootstrap 95% interval is
`[-0.515379,-0.482295]`, containing `-1/2` and excluding both zero and `-1`.
The independent quantization-floor exponent is `1.000000`. The squared
uniform log-loss deviation has `R²=0.998563` against `log|Pi|`.

Controls deliberately produce slope zero, slope `-1`, and a flat
single-policy class ratchet. Each would fail the registered `-1/2` or
`log|Pi|` gate.

Evidence: `evidence/claim_1/raw_results.json`,
`evidence/claim_1/raw_rate.csv`,
`evidence/claim_1/negative_controls.json`, and
`evidence/claim_1/independent_check.json`.
