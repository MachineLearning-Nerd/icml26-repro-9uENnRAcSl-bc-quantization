# Claim 2 source audit

Source: Theorem 3 at ar5iv anchor `Thmtheorem3`, retrieved 2026-07-23
from the paper whose SHA-256 is
`a1517e403f96e5c0c3529bbf8fcf3d8fad29b3149f164added02036f3318f0e1`.

The theorem assumes that `q#pi*` is deterministic; `q` is the uniform binning
quantizer from Equation 3; every policy in the finite class is
`k epsilon_q`-RTVC with modulus `kappa`; the quantized expert is realizable;
and the expert trajectory law is globally P-IISS with a max-form modulus
`gamma((r_t)) = gamma(max_t r_t)`.

With probability at least `1-delta`, the theorem bounds regret by the sum of

1. `H log(|Pi| delta^-1) / n`,
2. `H^2 kappa(gamma((k+1) epsilon_q))`, and
3. `H [gamma((k+1) epsilon_q) + (k+1) epsilon_q]`,

up to universal constants.

The experiment directly tests the stability mechanism, deterministic RTVC,
the broad-horizon distinction between stable and unstable dynamics, and the
independent epsilon dependence. The universal MLE concentration statement and
its exact hidden constant are proof-audited, not inferred from the propagation
observable. The observable is deliberately identified as state propagation:
bounded reward regret itself cannot grow faster than `H`.
