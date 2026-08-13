# Branch audit and rename map

## Legacy-to-final map

| Legacy ref | Final ref | Role |
|---|---|---|
| `master` | `main` | Canonical integrated source, evidence snapshot, and publication surface |
| `orx/frozen-legacy-3-12-baseline` | `baseline/frozen-legacy-3-12` | Pinned CPU environment and legacy comparison |
| `orx/c1-rigorous-log-loss-rate` | `research/c1-log-loss-rate` | C1 MLE rate, quantization floor, class ratchet, and controls |
| `orx/c2-c5-exact-dynamics-lower-bounds` | `research/c2-c5-exact-lower-bounds` | Exact rational dynamics and lower-bound certificates |
| `orx/c3-c4-c6-adversarial-quantizer-audit` | `audit/c3-c4-c6-adversarial-quantizer` | Adversarial quantizer and fail-closed prerequisite audit |
| `orx/c3-exact-preimage-quadrature` | `audit/c3-exact-preimage` | Exact Gaussian preimage audit for C3 |
| `orx/c4-operational-augmented-rollout` | `research/c4-augmented-rollout` | Operational model-augmented rollout evidence |
| `orx/c6-exact-rtvc-transport-audit` | `audit/c6-rtvc-transport` | Exact RTVC transport and categorical-TV audit |
| `orx/rc-cross-platform-regeneration-gate` | `release/cross-platform-gate` | Cross-platform regeneration and release gate |
| `orx/release-candidate-evidence-package` | `release/evidence-package` | Release packaging and forensic/vacuous-predicate correction |

All nine supporting legacy tips are ancestors of `origin/master`; mapping them
to descriptive refs preserves their work. The final publication target is ten
branches total: one `main` branch and nine named supporting branches.

## Identity requirement

After normalization, every reachable commit on every final branch must use:

```text
MachineLearning-Nerd <MachineLearning-Nerd@users.noreply.github.com>
```

## Publication checks

After publication, verify and record:

- repository name and homepage;
- default branch `main`;
- exactly the ten final branches above;
- absence of all `orx/*` and `master` remote refs;
- reachable commit author and committer identities;
- published README, gate, publication JSON, and branch audit;
- local `main` tracking `origin/main` with a clean worktree.
