# Claim 5 method

## Theorem 8

Transcribe the Appendix E.1 two-instance construction. For eight `n` values
and three horizons, use exact `Fraction` arithmetic for `Delta=1/(3n)`,
single-sample affinity, product affinity, squared Hellinger distance, exact
product TV, and the Le Cam lower bound. Require its ratio to `H/n` to remain
strictly positive.

Implement the paper's endpoint tie-breaking for uniform bins. Verify exactly
that `0` collides with `epsilon_q` and `1-epsilon_q` collides with `1` over
five bin widths and three horizons. The registered broken-width control uses
twice as many bins and must destroy the first collision.

## Theorem 9

Choose five perfect-square sample sizes so a certified
`Delta=1/(5 sqrt(n))` is rational. Enumerate every count in the two binomial
product laws using integer numerators over a common denominator. Check
`TV^2 <= 1-(1-4 Delta^2)^n` exactly and require the induced event-probability
lower bound to be at least `1/8`. Sweep three horizons and verify the exact
`1/5` coefficient of `H/sqrt(n)`. Separately enumerate the appendix's
displayed `3/5` choice and record that its stated reduction does not prove
`1/8`; no result from that audit is silently promoted to PASS.

Apply the Appendix E.2 support shifts and verify the combined threshold is
the exact sum of its statistical and quantization components.

An independent checker recomputes each product TV from the upper tail rather
than the producer's half-L1 enumeration. `Delta=0` is explicitly marked
inadmissible evidence.

## Legacy contradiction

Re-evaluate the original source at Git
`12c6b41365d2af3b38e97fcb585139eb2b51347f`. It printed a floor of `3.0`
and observed regret `0.024659...`, yet accepted only `reg_min >= 0`.
The audit records the numerical contradiction and the vacuous predicate. It
is not a theorem counterexample because the simulation is not the existential
hard instance and the legacy factor `0.3` was not supplied by the theorem.
