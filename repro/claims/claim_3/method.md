# Claim 3 method

Use the paper's scalar dynamics, arctangent expert, and all three pieces of its
adversarial quantizer, with a valid parameter tuple. The raw-expert recursion
is strictly increasing. At every time, invert that recursion at each trigger
interval endpoint and evaluate the corresponding standard-Gaussian preimage
mass. Combine these actual expert-distribution masses with interval-wise
quantization-error suprema; record root residuals and Gaussian-tail truncation
bounds.

Sweep eight geometrically decreasing epsilon values with
`H=ceil(64*|log(epsilon_q)|^2)`, so `H/|log(epsilon_q)|` increases rather than
remaining constant. Independently sweep horizon in the paper's analytic
Gaussian-CDF deployment lower bound. Require an expert-error exponent near
one, linear regret growth with a nonzero per-step floor, and a smooth-binning
negative control whose per-step regret vanishes linearly.
