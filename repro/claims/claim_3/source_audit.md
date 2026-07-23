# Claim 3 source audit

Theorem 6 uses `pi*(x)=arctan(x)`, `f(x,u)=Ax+Bu`, three exceptional
intervals, and the displayed piecewise learned quantizer. Its printed numeric
example violates its own condition `k/2>B/(1-lambda)`; the verifier uses
`A=.2,B=.3,k=2,d=1.2`, which satisfies every stated inequality.

The deterministic statement quantifies an average in-distribution
quantization error under the raw expert trajectory and an `H*Omega(1)`
deployment regret. Its proof requires `H=omega(|log epsilon_q|)`. A prior
audit incorrectly substituted the proof's loose pointwise density bound for
the actual expert-distribution probability and used only
`H=Theta(|log epsilon_q|)`; neither is accepted here.
