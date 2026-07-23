# Claim 2 — Theorem 3 P-IISS, RTVC, and horizon

**Status: VERIFIED.**

For stable scalar dynamics with `alpha=1/2`, exact rational recurrence and
exhaustive signed-input enumeration certify a horizon-independent P-IISS
gain. The deterministic state-independent quantized policy has zero RTVC
violations over 11,000 pairs.

The stable horizon sweep selects polynomial growth: fitted power
`1.069273`, `R²=0.999055`. The `alpha=2` negative control violates P-IISS and
selects exponential growth with semilog slope `0.693908`, matching `log 2`,
and `R²=0.999995`. An independent epsilon sweep has exponent `1.000000`.
Polynomial versus exponential conclusions use published residuals, not visual
inspection.

Evidence: `evidence/claim_2/raw_results.json`,
`evidence/claim_2/negative_controls.json`, and
`evidence/claim_2/independent_check.json`.
