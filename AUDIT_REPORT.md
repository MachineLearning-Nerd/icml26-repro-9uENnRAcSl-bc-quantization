# Claim-by-claim audit report

## Conclusion

The repository evolved from a small six-boolean prototype into a committed
finite-contract audit. The strongest defensible result is:

```text
C1 VERIFIED_SCOPED
C2 VERIFIED_SCOPED
C3 VERIFIED_SCOPED
C4 VERIFIED_SCOPED
C5 VERIFIED_SCOPED_WITH_DISPLAYED_CONSTANT_GAP
C6 FALSIFIED_AS_LITERAL_EMPIRICAL_CLAIM
OVERALL MIXED_RESULTS
STRICT_PUBLICATION_GATE NOT_READY
```

The C6 source finding does not reject the paper's theoretical Proposition 5 or
Theorem 6. It rejects only the historical repository wording that attributed an
empirical comparison to the paper.

## C1 — Sample complexity and quantization floor

The producer uses an exact state-independent Bernoulli log-loss MLE with a
geometric sample-size sweep from 64 to 65,536 and 256 deterministic seeds. The
rate slope is `-0.499193` with bootstrap 95% interval
`[-0.515379, -0.482295]`; the independent quantization-floor exponent is one,
and the finite policy-class squared deviation has `R^2 = 0.998563`. A flat
zero-effect control and an injected `n^-1` control behave as registered.

This is strong evidence for the declared construction and rate, but it does
not prove Theorem 2 for every policy class, MDP, confidence level, or hidden
constant.

## C2 — Stable dynamics and RTVC

The exact rational recurrence uses `alpha=1/2` for the stable construction and
`alpha=2` as an unstable negative control. The stable fit has polynomial slope
about `1.069` with `R^2` about `0.999`, while the unstable fit has exponential
slope about `log(2)` with `R^2` about `0.999995`. The RTVC enumeration covers
11,000 pairs with zero violations and the independent epsilon fit has exponent
one.

The result verifies the registered examples and the contrast, not the full
Theorem 3 quantifier over all admissible dynamics and policy classes.

## C3 — Non-smooth learning quantizer

The audit uses the paper's scalar stable dynamics and arctangent expert, but
computes actual expert-distribution probabilities by inverting the monotone
recursion at every trigger-interval endpoint. Gaussian-tail truncation and
inverse residuals are certified. The epsilon sweep uses a horizon growing as
`|log(epsilon_q)|^2`, so it satisfies the theorem's `omega(|log epsilon_q|)`
requirement; the expert-error exponent is about `0.99`, and the deployment
regret has a positive linear-horizon floor. A smooth-binning control vanishes.

The printed numerical parameter example does not satisfy one strict inequality;
the audit discloses and replaces it with a parameter tuple satisfying the stated
conditions. This is a scoped construction result, not a universal theorem
proof.

## C4 — Model-based augmentation

The producer executes the learned policy on an auxiliary learned-model rollout,
copies the resulting actions into a separately evolved real environment, and
checks the stated stability certificate. It also measures finite log-loss MLE
error over all five registered axes: horizon, sample size, quantization error,
policy-class size, and transition-model-class size. Quadrature refinement
converges, direct rollouts stay below the certificate, and a broken-realizability
control is positive.

This establishes an operational finite audit of the registered construction. It
does not establish Theorem 7 for arbitrary model classes or environments.

## C5 — Information-theoretic lower bounds

Theorem 8 is checked with exact rational one-sample/product affinities,
Hellinger identities, Le Cam lower bounds, and the paper's bin-collision
construction. Theorem 9 is checked with exact finite binomial enumeration and a
second upper-tail implementation; the additive quantization threshold and
probability threshold are recorded.

The audit also records a real displayed-constant gap in the source's `3/(5
sqrt(n))` route to probability `1/8`. A separate rational constant preserves the
rate and passes the threshold. The gap is a presentation/constant issue, not a
falsification of the existential lower-bound rates, and it prevents an
unqualified `VERIFIED` label.

## C6 — RTVC contrast versus empirical attribution

The independent checker verifies the theoretical contrast: binning satisfies the
registered thresholded transport condition across 16 epsilon/resolution cells,
the learned piecewise quantizer has persistent jumps, and the stochastic
Gaussian categorical-TV calculation respects data processing. The broken-width
control fails as intended.

The source itself presents Proposition 5 and Theorem 6 as theory and says the
practical preference for binning is suggested by the theory, while citing an
external empirical observation. Therefore the historical repository sentence
“empirically, binning quantizers are shown…” is marked
`FALSIFIED_AS_LITERAL_EMPIRICAL_CLAIM`. The theoretical evidence remains useful
and is labeled separately.
