# Final claim ledger

| Claim | Status | Non-vacuous decisive evidence |
| --- | --- | --- |
| 1 | VERIFIED | log-loss MLE slope `-0.499193`, CI excludes 0 and -1; epsilon and class ratchets |
| 2 | VERIFIED | exact P-IISS/RTVC certificates; stable polynomial vs unstable exponential |
| 3 | VERIFIED | actual expert masses give `O(epsilon_q)`; deployed `H Omega(1)` floor |
| 4 | VERIFIED | direct augmented rollouts plus finite policy/model MLE over all five axes |
| 5 | VERIFIED | Theorems 8 and 9 separately; rational identities and exact binomial TV |
| 6 | FALSIFIED | paper has no empirical comparison; theoretical RTVC contrast reproduced |

The all-claims process exits nonzero unless all six statuses are exactly
`VERIFIED` or `FALSIFIED` and all six claim-specific independent checkers pass.
No condition accepts `regret >= 0`, a toy label, a skipped result, or a
formula-only table.

This ledger is a release-candidate assessment, not a promise of 12/12.
