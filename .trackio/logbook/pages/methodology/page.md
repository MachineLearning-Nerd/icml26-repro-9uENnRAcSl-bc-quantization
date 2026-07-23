# Methodology

The primary source is the ar5iv rendering of arXiv `2603.20538`, retrieved
2026-07-23 with SHA-256
`a1517e403f96e5c0c3529bbf8fcf3d8fad29b3149f164added02036f3318f0e1`.
Each contract transcribes theorem assumptions, quantifiers, rate terms, and
the direct-test/proof-audit boundary before inspecting outcomes.

The fixed command is:

```text
uv run --frozen python repro/src/verify_bc.py
```

The lockfile pins NumPy and SciPy. Every experiment is CPU-only and runs the
same command. Each stronger child reruns every earlier verifier. A claim is
complete only if its producer and a claim-specific independent checker pass
and its status is exactly `VERIFIED` or `FALSIFIED`; `BLOCKED`, toy, skipped,
and inconclusive statuses fail the process.

Every claim directory contains `claim_contract.json`, `source_audit.md`,
`method.md`, raw JSON/CSV results, status, provenance, a manifest, and an
independent check. Negative controls are designed to break the claimed
mechanism and are acceptance-gated.

The release snapshot comes from cumulative local run
`9bcfb200-70d6-402e-8aa3-5d147be11b7e` at Git
`ca81069980d0373357ee1bdc675c059c4a56872c`. The release-candidate branch
adds only check isolation, packaging, and preservation gates, then reruns the
same scientific suite on Hugging Face `cpu-upgrade`.

Cross-platform regeneration requires identical raw JSON schema and array
shapes plus every registered numerical/symbolic producer and independent
checker gate. Byte-identical floating-point JSON is deliberately not required:
the immutable macOS snapshot and regenerated Linux hashes are both printed,
and platform-level numerical differences must remain inside the scientific
acceptance contracts.
