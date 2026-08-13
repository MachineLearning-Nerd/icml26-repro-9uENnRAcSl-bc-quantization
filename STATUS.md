# Repository status

| Area | Status | Evidence |
|---|---|---|
| Paper identity | Verified | arXiv `2603.20538v1`, OpenReview `9uENnRAcSl`, Haoqun Cao and Tengyang Xie |
| Source pin | Present in claim contracts | ar5iv source hash `a1517e403f96e5c0c3529bbf8fcf3d8fad29b3149f164added02036f3318f0e1` |
| Finite evidence package | `PASSED` | six claim contracts, six independent checkers, raw outputs, manifests, and provenance |
| C1 sample complexity | `VERIFIED_SCOPED` | genuine log-loss MLE, `n^-1/2` slope, epsilon floor, class-size ratchet, controls |
| C2 stability/horizon | `VERIFIED_SCOPED` | exact stable recurrence, RTVC enumeration, unstable exponential control |
| C3 non-smooth quantizer | `VERIFIED_SCOPED` | exact preimage masses, certified tails, `H=omega(|log epsilon_q|)`, linear deployment floor |
| C4 model augmentation | `VERIFIED_SCOPED` | direct rollouts, converged quadrature, five-axis operational sweep, broken-realizability control |
| C5 lower bounds | `VERIFIED_SCOPED_WITH_DISPLAYED_CONSTANT_GAP` | exact rational Theorem 8/9 identities and independent binomial-TV enumeration |
| C6 literal empirical attribution | `FALSIFIED_AS_LITERAL_CLAIM` | source audit shows the paper gives theory, not an empirical quantizer comparison |
| C6 theoretical RTVC contrast | `VERIFIED_SCOPED` | Definition-4 transport, binning control, learned jump, categorical-TV audit |
| Paper-level theorem verification | `NOT_ESTABLISHED` | finite contracts cannot discharge universal/asymptotic quantifiers |
| Strict publication gate | `NOT_READY` | `GATE_READY.md`, `publication_gate.json` |

## Important evidence boundary

The current release snapshot under
`repro/release_snapshot/evidence/` is later and more rigorous than the root
prototype output. The root `outputs/verify_run.log` reports four passing checks
after two early failures; it is retained as historical evidence. The release
snapshot records C1–C5 as passing their finite contracts and C6 as a deliberate
source-level falsification of the historical empirical wording.

## C5 source deviation

Theorem 9's displayed proof route uses a `3/(5 sqrt(n))` choice and a reduction
that does not itself yield the displayed `1/8` event probability from its
`TV <= 7/8` line. The audit records this gap rather than hiding it. A separate
exact rational choice preserves the claimed rate and clears the `1/8` threshold;
the unspecified universal constant means this is not treated as a theorem
counterexample.

## Required work before a strict gate

1. Add proof-level or theorem-wide verification beyond finite constructions.
2. Expand the audited parameter families and quantify the remaining constants.
3. Resolve the C5 displayed-constant presentation in the source audit or paper.
4. Keep C6 labeled as a theoretical contrast unless independent empirical data
   are supplied by a separate study.
