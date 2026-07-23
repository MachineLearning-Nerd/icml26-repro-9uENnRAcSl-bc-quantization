# Claim 2 method

Use the scalar shared-noise dynamics
`x_(h+1) = alpha x_h + u_h`. The raw expert action is the left endpoint of a
uniform bin and the deployed action is its midpoint, so the perturbation is
exactly `epsilon_q/2`. The quantized expert is deterministic and belongs to a
finite class of state-independent deterministic label policies.

For `alpha=1/2`, exact rational arithmetic gives
`sup_h |delta x_h| <= 2 max_t |delta u_t|`, certifying global P-IISS with a
max-form modulus. All signed perturbation sequences through horizon 12 are
also exhaustively enumerated. Because every policy is state-independent,
the same deterministic label couples every state pair and the RTVC modulus is
zero; more than 10,000 grid pairs are enumerated as an audit.

Sweep `H = 4, 8, ..., 128`. Fit both a power model and an exponential model to
the cumulative propagation error and publish slopes and log-space residuals.
Repeat with `alpha=2`: its constant-input gain is exactly `2^H-1`, so it
violates any horizon-independent P-IISS modulus and must select the
exponential model. This is the registered negative control.

At fixed `H=32`, sweep seven rational bin widths from `1/64` through `1/4096`.
The exact recurrence must yield epsilon exponent one. A separate checker
recomputes every recurrence from the raw rational numerators and denominators.
