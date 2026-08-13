# Source and provenance manifest

## Paper identity

- Title: *Understanding Behavior Cloning with Action Quantization*
- Authors: Haoqun Cao; Tengyang Xie
- arXiv record: [2603.20538](https://arxiv.org/abs/2603.20538)
- Audited version: [arXiv v1 HTML](https://arxiv.org/html/2603.20538)
- OpenReview: [9uENnRAcSl](https://openreview.net/forum?id=9uENnRAcSl)
- The claim contracts pin the ar5iv HTML source retrieved on 2026-07-23.

## Source hash

The claim contracts and release evidence use this source SHA-256:

```text
a1517e403f96e5c0c3529bbf8fcf3d8fad29b3149f164added02036f3318f0e1
```

The official arXiv record and HTML were rechecked on 2026-08-14. No local PDF
is committed in this repository; the source hash in each claim contract is the
version boundary for the finite audit.

## Claim anchors

| Claim | Paper anchor | Evidence boundary |
|---|---|---|
| C1 | Theorem 2, Section 3.2 | Bernoulli log-loss MLE rate, quantization floor, finite-class ratchet, and controls |
| C2 | Theorem 3, Definitions 3–4 | Exact stable/unstable recurrences, P-IISS/RTVC construction, and epsilon sweep |
| C3 | Theorem 6, Section 4.1 | Exact trigger-interval preimages, Gaussian tails, asymptotic horizon schedule, and smooth control |
| C4 | Algorithm 1 and Theorem 7, Section 4.2 | Direct auxiliary/real rollouts and finite policy/model class sweep |
| C5 | Theorems 8–9 and Appendix E | Exact rational identities, product TV, bin collisions, and displayed-constant audit |
| C6 | Proposition 5 and Theorem 6 | Theoretical RTVC contrast; historical empirical wording tested and falsified |

## Repository evidence

- Claim contracts and source audits: `repro/claims/claim_*/`.
- Producers: `repro/rigorous/claim1.py`, `claim2.py`, `claim346.py`, and
  `claim5.py`.
- Independent checkers: `repro/rigorous/independent_check_*.py`.
- Authoritative committed outputs: `repro/release_snapshot/evidence/`.
- Historical prototype outputs: `outputs/verdict.json` and
  `outputs/verify_run.log`.
- Historical experiment narrative: `.trackio/logbook/`.

The release snapshot contains raw results, status files, provenance, manifests,
negative controls where applicable, and independent-checker results for all six
contracts. It is finite evidence, not a replacement for the paper's proofs.
