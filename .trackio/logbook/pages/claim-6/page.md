# Claim 6 — binning, learned quantizers, and RTVC

**Status: FALSIFIED as literally worded; theoretical contrast reproduced.**

The paper does not empirically compare the two quantizers. Proposition 5 and
Theorem 6 are theoretical, the prose says “our theory suggests,” and the
empirical observation is attributed to Pertsch et al. The exact judge claim's
empirical attribution is therefore false.

The theoretical mechanism is independently tested. Across four epsilon values
and four resolutions, 69,347,488 deterministic pairs within the RTVC radius
are evaluated using Definition 4's thresholded optimal-transport cost.
Valid midpoint binning has zero violations. A width that violates the declared
quantizer-error assumption produces 6,718,944 violations.

The actual Theorem 6 learned boundary retains minimum jump `0.946908` and
deterministic TV/relaxed-OT cost one as spacing shrinks. For stochastic
Gaussian experts, quantized categorical TV is computed from every bin's CDF
mass and obeys data processing; the maximum 8-sigma/10-sigma refinement
difference is `1.65e-17`.

Evidence: `evidence/claim_6/raw_results.json` and
`evidence/claim_6/independent_check.json`.
