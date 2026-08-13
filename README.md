# Understanding Behavior Cloning with Action Quantization

This repository is the ICML 2026 reproduction audit for
[**Understanding Behavior Cloning with Action Quantization**](https://arxiv.org/abs/2603.20538)
by Haoqun Cao and Tengyang Xie.

Paper identifiers: [arXiv 2603.20538v1](https://arxiv.org/abs/2603.20538v1)
and [OpenReview 9uENnRAcSl](https://openreview.net/forum?id=9uENnRAcSl). The
repository is being cleaned up as
`MachineLearning-Nerd/icml26-behavior-cloning-action-quantization`; its legacy
name is `MachineLearning-Nerd/icml26-repro-9uENnRAcSl-bc-quantization`.

## Status at a glance

| Gate or result | Current status |
|---|---|
| Paper association | Verified against arXiv v1 and the pinned ar5iv source used by the contracts |
| Finite claim contracts | 6/6 release contracts pass with producer and independent-checker evidence |
| Scoped positive results | C1–C5 pass their declared finite contracts; C5 records a displayed-constant deviation |
| Scoped source finding | C6 theoretical RTVC contrast passes, but its historical empirical attribution is falsified |
| Paper-level universal/asymptotic verification | 0/6 strictly established by finite computation |
| Evidence release gate | `PASSED` for the finite evidence package |
| Strict publication gate | `NOT_READY` |
| Overall status | `MIXED_RESULTS` |

`VERIFIED` in the committed release snapshot means that the declared finite
contract, its producer, and its independent checker passed. It does not prove a
universal theorem, an asymptotic limit, or a high-probability statement outside
the tested construction. The strict publication gate remains closed for that
reason.

The root files `outputs/verdict.json` and `outputs/verify_run.log` are an older
four-of-six prototype run. The authoritative current evidence is the later
release snapshot under
[`repro/release_snapshot/evidence`](repro/release_snapshot/evidence), whose
claim ledger records five scoped passes and one literal-source falsification.

## What the paper does

The paper studies log-loss behavior cloning when continuous actions are
quantized into a finite alphabet. It analyzes the interaction of statistical
estimation error and quantization error in finite-horizon MDPs.

Its main results are:

1. For stochastic quantized experts, stable dynamics and TV-continuous policy
   classes give a regret rate of order
   `H * sqrt(log(|Pi| / delta) / n) + H^2 * epsilon_q` (Theorem 2).
2. For deterministic experts, a binning quantizer and RTVC policy class under
   global P-IISS give a polynomial-horizon bound (Theorem 3).
3. A learning-based quantizer can have small in-distribution error while
   violating RTVC and causing large deployment regret (Theorem 6).
4. Model-based auxiliary rollouts bypass the policy-smoothness requirement and
   improve the quantization dependence, assuming realizability of both the
   policy and transition-model classes (Algorithm 1 and Theorem 7).
5. Information-theoretic lower bounds expose additive statistical and
   quantization limits for deterministic and stochastic experts (Theorems 8
   and 9).

Proposition 5 gives the theoretical RTVC contrast between binning and general
learning-based quantizers. The paper says that this theory suggests a practical
preference for binning; it does not present an empirical quantizer comparison
as a result of this paper.

## Claim-to-evidence ledger

| Claim | Paper contract | Producer → output | Current finding |
|---|---|---|---|
| C1 | Theorem 2: stochastic log-loss BC has the `n^-1/2` statistical rate and a linear quantization floor | `repro/rigorous/claim1.py::run_claim_1` → `repro/release_snapshot/evidence/claim_1`; independent recomputation in `independent_check_1.py` | `VERIFIED_SCOPED`: exact Bernoulli log-loss MLE, six-point `n` sweep with 256 seeds, slope `-0.499193` with 95% CI `[-0.515379, -0.482295]`, epsilon exponent `1.0`, finite-policy `log|Pi|` ratchet, and wrong-rate/zero-effect controls; not a proof of Theorem 2 |
| C2 | Theorem 3: stable P-IISS dynamics plus binning/RTVC yield polynomial horizon dependence | `repro/rigorous/claim2.py::run_claim_2` → `claim_2`; independent rational recurrence in `independent_check_2.py` | `VERIFIED_SCOPED`: exact stable recurrence, 11,000 RTVC pairs with zero violations, stable polynomial fit, unstable `alpha=2` exponential negative control, and independent epsilon sweep; only the registered constructions are covered |
| C3 | Theorem 6: a non-smooth learning quantizer can produce `H * Omega(1)` deployment regret despite `O(epsilon_q)` expert-distribution error | `repro/rigorous/claim346.py::run_claims_3_4_6` → `claim_3`; independent preimage/limit checks in `independent_check_346.py::check_claim_3` | `VERIFIED_SCOPED`: exact monotone-recursion inversions, Gaussian preimage masses, certified tails, `H = omega(|log epsilon_q|)` schedule, expert-error exponent about `0.99`, linear-horizon floor, and vanishing smooth-binning control; the printed numerical example required a parameter repair |
| C4 | Algorithm 1 and Theorem 7: model-based auxiliary rollouts improve the quantization term without policy RTVC, under P-IISS and policy/model realizability | `claim346.py::run_claims_3_4_6` → `claim_4`; independent operational-sum and rollout checks in `check_claim_4` | `VERIFIED_SCOPED`: direct real-environment rollouts, converged quadrature, finite log-loss MLE, all `H × n × epsilon_q × |Pi| × |M|` axes, a broken-realizability control, and a persistent quantization floor; not a universal theorem verification |
| C5 | Theorems 8–9: deterministic lower bound `H(1/n + epsilon_q)` and stochastic lower bound `H(sqrt(1/n) + epsilon_q)` | `repro/rigorous/claim5.py::run_claim_5` → `claim_5`; exact upper-tail checker in `independent_check_5.py` | `VERIFIED_SCOPED_WITH_DISPLAYED_CONSTANT_GAP`: exact rational Hellinger/product-TV identities, bin collisions, exact binomial enumeration, probability threshold, additive quantization term, and broken-width/zero-Delta controls; the displayed `3/(5 sqrt(n))` proof route does not itself yield `1/8`, so a separately certified constant is recorded |
| C6 | Historical wording claimed an empirical binning-versus-learned quantizer result; the paper actually provides Proposition 5/Theorem 6 theory and says the practical conclusion is suggested by theory | `claim346.py::run_claims_3_4_6` → `claim_6`; independent Definition-4 transport and categorical-TV checks in `check_claim_6` | `FALSIFIED_AS_LITERAL_EMPIRICAL_CLAIM`: the source audit rejects the empirical attribution; the theoretical RTVC contrast, learned-quantizer jump, binning control, and stochastic data-processing checks are separately `VERIFIED_SCOPED` |

Every release claim has a source audit, method, provenance, raw result,
status, and independent-checker artifact. Read the exact contracts under
[`repro/claims`](repro/claims) and the committed raw evidence under
[`repro/release_snapshot/evidence`](repro/release_snapshot/evidence).

## Code and branch map

The current history has one integrated `master` branch and nine supporting
`orx/*` branches. All supporting tips are ancestors of the integrated tip, so
their work can be retained under descriptive final branch names. The planned
legacy-to-final map is recorded in [BRANCH_AUDIT.md](BRANCH_AUDIT.md).

| Final branch | Legacy branch | Role |
|---|---|---|
| `main` | `master` | Canonical documentation, integrated source, evidence snapshot, and gate |
| `baseline/frozen-legacy-3-12` | `orx/frozen-legacy-3-12-baseline` | Pinned CPU environment and legacy comparison |
| `research/c1-log-loss-rate` | `orx/c1-rigorous-log-loss-rate` | C1 MLE rate, quantization floor, class-complexity ratchet, and controls |
| `research/c2-c5-exact-lower-bounds` | `orx/c2-c5-exact-dynamics-lower-bounds` | Exact rational dynamics and lower-bound certificates |
| `audit/c3-c4-c6-adversarial-quantizer` | `orx/c3-c4-c6-adversarial-quantizer-audit` | Adversarial quantizer and fail-closed prerequisite audit |
| `audit/c3-exact-preimage` | `orx/c3-exact-preimage-quadrature` | Exact Gaussian preimage quadrature for C3 |
| `research/c4-augmented-rollout` | `orx/c4-operational-augmented-rollout` | Operational model-augmented rollouts for C4 |
| `audit/c6-rtvc-transport` | `orx/c6-exact-rtvc-transport-audit` | Exact RTVC transport and categorical-TV audit |
| `release/cross-platform-gate` | `orx/rc-cross-platform-regeneration-gate` | Cross-platform raw regeneration gate |
| `release/evidence-package` | `orx/release-candidate-evidence-package` | Release-candidate packaging and forensic/vacuous-predicate corrections |

| Path | Role |
|---|---|
| `repro/rigorous/claim1.py` | C1 producer |
| `repro/rigorous/claim2.py` | C2 producer |
| `repro/rigorous/claim346.py` | C3, C4, and C6 producers |
| `repro/rigorous/claim5.py` | C5 producer |
| `repro/rigorous/independent_check_*.py` | Independent claim-specific checkers |
| `repro/src/verify_bc.py` | Cumulative producer/checker/release validator |
| `repro/claims/` | Source-anchored contracts and methods |
| `repro/release_snapshot/evidence/` | Committed authoritative finite evidence |
| `.trackio/logbook/` | Historical and superseded run narrative |
| `outputs/` | Original prototype output; retained for provenance only |

## Reproduce

The pinned CPU environment is Python 3.12 with NumPy, SciPy, and SymPy from
`uv.lock`:

```bash
uv sync --frozen
uv run --frozen python repro/src/verify_bc.py
```

The cumulative command regenerates `.openresearch/artifacts/` and validates the
finite release package. Individual entrypoints are available as
`repro/src/verify_claim_1.py` through `verify_claim_6.py`; claims 3, 4, and 6
share the common construction runner. The committed release snapshot is not
silently overwritten by the historical root verifier.

This is a CPU-only finite audit. It does not establish the paper's universal
quantifiers, asymptotic limits, or high-probability guarantees for every MDP,
policy class, quantizer, or offline algorithm.

## Citation

```bibtex
@article{cao2026understanding,
  title   = {Understanding Behavior Cloning with Action Quantization},
  author  = {Cao, Haoqun and Xie, Tengyang},
  journal = {arXiv preprint arXiv:2603.20538},
  year    = {2026},
  doi     = {10.48550/arXiv.2603.20538}
}
```

Please cite arXiv version 1, the source version audited here.

## Thank you

Thank you to **Haoqun Cao** and **Tengyang Xie** for making this work
available and for developing a useful theoretical lens on action tokenization,
stability, smoothness, and behavior-cloning limits. This repository is an
independent reproduction audit, not an official implementation or endorsement
by the authors; the conservative claim boundaries are intended to make the
paper easier to study and extend.

Maintained by [MachineLearning-Nerd](https://github.com/MachineLearning-Nerd).
