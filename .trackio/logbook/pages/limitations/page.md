# Limitations

This is a theorem-mechanism reproduction, not a proof assistant
formalization. Universal hidden constants and general concentration arguments
are source-audited; finite constructions directly test the rates and
assumptions they expose.

Claim 3 verifies the deterministic half of Theorem 6. It does not claim a
separate reproduction of the theorem's stochastic-dynamics construction.
Numerical integration is paired with monotone-preimage and stability
certificates, nested refinements, residuals, and tail bounds.

Claim 4's full statistical/quantization dependence is tested on a product MDP:
the non-smooth scalar system supplies the quantization component and a finite
Bernoulli policy/model problem supplies genuine log-loss MLE regret. This
isolates all theorem terms without pretending that formula evaluation is an
experiment.

Claim 6 is not labeled VERIFIED because its literal word “empirically” is
unsupported by this paper. Falsification applies only to that wording; the
paper's theoretical RTVC contrast is reproduced.

Passing these gates supports release readiness. It does not guarantee any
external judge score.

Seeded NumPy distribution summaries are not claimed to be bitwise identical
across CPU architectures. The release preserves one immutable raw snapshot,
regenerates the same schemas and shapes, publishes both SHA-256 sets, and
requires all rate intervals, exact identities, residual comparisons,
quadrature tolerances, and negative controls to pass independently.
