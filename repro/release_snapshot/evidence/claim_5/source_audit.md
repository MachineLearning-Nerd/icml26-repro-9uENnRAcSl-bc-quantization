# Claim 5 source audit

Source: Theorems 8 and 9 and Appendix E of the pinned ar5iv paper, retrieved
2026-07-23, SHA-256
`a1517e403f96e5c0c3529bbf8fcf3d8fad29b3149f164added02036f3318f0e1`.

The paper restricts attention to non-anticipatory offline algorithms: the
component learned for step `h` may use trajectory prefixes only through `h`.

Theorem 8 quantifies over every such algorithm and asserts existence of an
instance with deterministic Lipschitz expert, deterministic `q#pi*`,
1-Lipschitz reward, global P-IISS modulus `gamma((r_k))=r_1`, and uniform
quantization error at most `epsilon_q`, for which expected regret is
`Omega(H(1/n+epsilon_q))`.

Appendix E.1 uses two initial-state/action instances with
`Delta=1/(3n)`. Their one-sample Hellinger affinity is `1-Delta`. A Le Cam
argument gives the statistical term. Four raw-expert instances that collide
under the same uniform binning observations give the quantization term.

Theorem 9 allows a suboptimal stochastic, state-independent expert. Appendix
E.2 uses Bernoulli parameters `1/2 +/- Delta`,
`Delta=3/(5 sqrt(n))`, and obtains an event of regret at least a universal
constant times `H(sqrt(1/n)+epsilon_q)` with probability at least `1/8`.

There is a constant-level gap in the displayed proof: after reducing the
probability to `(1-TV)/4`, the stated `TV <= 7/8` gives only `1/32`, not
`1/8`. This does not contradict the theorem because its threshold constant
`c` is unspecified. The verifier audits the displayed choice exactly and
separately certifies the same construction with
`Delta=1/(5 sqrt(n))`, which preserves the claimed rate and clears `1/8`.

Both are existential hard-instance statements. Neither asserts that every
smooth simulation has regret above the expression with constant one.
