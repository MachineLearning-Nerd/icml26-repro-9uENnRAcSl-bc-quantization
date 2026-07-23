# Provenance and artifact manifest

- Paper: arXiv `2603.20538`; ar5iv SHA-256
  `a1517e403f96e5c0c3529bbf8fcf3d8fad29b3149f164added02036f3318f0e1`.
- Repository start: `master` at
  `12c6b41365d2af3b38e97fcb585139eb2b51347f` (matched).
- Frozen legacy baseline: `edf75504`.
- Cumulative scientific snapshot: `ca81069980d0373357ee1bdc675c059c4a56872c`.
- Local cumulative run: `9bcfb200-70d6-402e-8aa3-5d147be11b7e`.
- Fixed command: `uv run --frozen python repro/src/verify_bc.py`.
- Hardware policy: CPU only; no GPU-backed run.
- Seeds and runtime/platform versions are recorded per claim.

Every artifact has a per-claim SHA-256 manifest. The release also contains a
global text upload allowlist and SHA-256 manifest. The judged Space revision
`cbdb6955777b019e1787d7fc6d7208841fa6ec4d` has 23 paths; the release
validator treats the candidate as that immutable path set plus text additions
and fails unless all 23 remain present.

The protected legacy page blobs are recorded in
`repro/release/protected_space_manifest.json`. Exact original Markdown is
also retained under [Legacy audit](#/legacy).
