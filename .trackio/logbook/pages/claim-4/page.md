# Claim 4 — Theorem 7 model augmentation

**Status: VERIFIED.**

The same RTVC-violating Claim 3 construction is used; RTVC is not assumed.
An exact model rolls the learned policy on an auxiliary raw-expert state,
copies those actions to a separately evolved real state, and evaluates reward
on the real state. Three nested Gaussian-quantile resolutions give maximum
refinement difference `1.66e-6`; every rollout is below an independent
P-EIISS certificate.

Augmented regret per horizon has epsilon exponent `0.986286`, while ordinary
feedback retains a `0.725704` floor. The finite component is genuine
Bernoulli log-loss MLE for both policy and model classes over 128 seeds, with
`n` exponent `-0.499830`.

All 81 combinations of `H`, `n`, `epsilon_q`, `|Pi|`, and `|M|` are
operational product-MDP regret sums, not formula evaluations. The complete
Theorem 7 scale includes `log|M|`; the largest observed/scale ratio is
`0.974855`. A fixed model bias is the broken-realizability control and does
not vanish with `n` or `epsilon_q`.

Evidence: `evidence/claim_4/raw_results.json` and
`evidence/claim_4/independent_check.json`.
