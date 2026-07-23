# Claim 4 method

Use the same non-smooth construction. Roll the learned policy on the exact
auxiliary raw-expert state, copy its quantized actions into a separately
evolved real state, and evaluate the paper's reward on that real state.
Publish nested Gaussian-quantile quadratures and compare every rollout with an
independent P-EIISS bound computed from exact expert preimage masses.

For the statistical term, fit every member of finite Bernoulli policy and
transition classes by exact log-loss MLE over 128 deterministic seeds. The
maximum policy TV error plus maximum transition-model TV error is the
per-step bounded-reward regret of that component. Take the product of this
finite-class component and the non-smooth scalar quantization system, adding
their bounded rewards. This makes all 81 `H x n x epsilon_q x |Pi|=|M|`
points operational sums of measured regrets, while the complete theorem
expression is retained only as the comparison scale. A fixed transition-model
bias is the broken-realizability control.
