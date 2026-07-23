# Claim 5 — Theorems 8 and 9 lower bounds

**Status: VERIFIED separately for Theorem 8 and Theorem 9.**

Theorem 8 is checked with exact rational Hellinger affinity, product
affinity, TV, and Le Cam identities. Its minimum certified coefficient
relative to `H/n` is `0.059286`. Uniform-bin endpoint collisions reproduce
the additive `H epsilon_q` term; changing the bin width destroys the required
collision.

Theorem 9 uses exact finite binomial enumeration. The independently
recomputed maximum TV is `0.310828`, and the minimum certified event
probability is `0.172293`, above `1/8`. The paper's displayed `3/5` constant
does not itself prove its stated `1/8` after the shown reduction; a rational
`1/5` construction preserves the quantified rate and clears the threshold.

The legacy `3.0` versus `0.024659` contradiction is not a counterexample:
that simulation is not the theorem's existential hard instance and the old
script accepted only `reg_min >= 0`. The vacuous assertion is recorded as
rejected evidence.

Evidence: `evidence/claim_5/raw_results.json`,
`evidence/claim_5/negative_controls.json`, and
`evidence/claim_5/independent_check.json`.
