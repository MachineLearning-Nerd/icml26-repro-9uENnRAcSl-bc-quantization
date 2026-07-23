# Claim 1 source audit

Primary source: ar5iv HTML for arXiv `2603.20538`, retrieved
`2026-07-23T03:47:05Z`, SHA-256
`a1517e403f96e5c0c3529bbf8fcf3d8fad29b3149f164added02036f3318f0e1`.

Theorem 2 is anchored at `#Thmtheorem2`. Its scope is:

- `q#pi*` is stochastic;
- every policy in the finite class is TV-continuous with a linear modulus;
- realizability: `q#pi*` belongs to the policy class;
- the expert trajectory distribution is globally P-EIISS;
- with probability at least `1-delta`, regret is bounded up to a universal
  constant by `H sqrt(log(|Pi| delta^-1)/n) + H^2 epsilon_q`.

The statistical `n^-1/2` exponent is also the stochastic lower-bound exponent
in Theorem 9. The experiment directly tests genuine log-loss estimation in
total variation, the exponent and confidence interval, an independent
quantization floor, and a finite-class `log|Pi|` ratchet. General constants and
the theorem proof are source-audited rather than inferred from a toy MSE.
