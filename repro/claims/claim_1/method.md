# Claim 1 method

## Statistical term

Use a state-independent stochastic expert `Bernoulli(0.37)` on the discrete
quantized action alphabet `{0,1}`. The behavior-cloning estimator is the exact
Bernoulli negative-log-likelihood MLE. State independence certifies TVC with
zero modulus; constant dynamics certify global P-EIISS with zero modulus; the
true policy is in the class.

Sweep `n = 64, 256, ..., 65536` with 256 deterministic seeds. Fit the exponent
of mean total-variation error `|p_hat-p|` and compute a 3,000-replicate
bootstrap confidence interval. The registered gate requires the interval to
contain `-1/2` and exclude both `0` and `-1`.

## Quantization term

Independently use `U ~ Uniform[0,1]`, reward `r(u)=u`, and a uniform
left-endpoint quantizer. This gives the exact non-vacuous identity
`E[U-q(U)] = epsilon_q/2`. Sweep seven bin widths and verify linear scaling.

## Finite policy classes

Construct nested, enumerable Bernoulli policy classes over 64 contexts. Every
class contains the true `Bernoulli(0.5)` policy plus context-dependent
distractors. Compute actual empirical and population log losses and measure the
uniform deviation. The squared deviation must be linear in `log|Pi|`; a
single-policy control must remove that dependence.

## Falsifiers

- Reusing only the smallest sample size must produce exponent zero.
- An injected `1/n` curve must produce exponent `-1`, and therefore fail the
  `-1/2` gate.
- A class with no maximum over competing policies must have zero
  `log|Pi|` slope.

All raw arrays, CSV data, provenance, gates, negative controls, and independent
checker output are written beneath `.openresearch/artifacts/claim_1/`.
