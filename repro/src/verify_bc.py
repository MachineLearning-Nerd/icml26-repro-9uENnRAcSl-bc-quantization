"""Cumulative fail-closed verifier for arXiv 2603.20538."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from repro.rigorous.claim1 import run_claim_1
from repro.rigorous.common import ARTIFACT_ROOT, canonical_json, write_json
from repro.rigorous.independent_check_1 import check_claim_1


def main() -> int:
    summary = run_claim_1()
    independent = check_claim_1()
    ledger = {
        "paper": "Understanding Behavior Cloning with Action Quantization",
        "arxiv": "2603.20538",
        "claims": {
            "1": {
                "status": summary["status"],
                "producer_passed": summary["passed"],
                "independent_checker_passed": independent["passed"],
            },
            "2": {"status": "BLOCKED", "reason": "not implemented on this node"},
            "3": {"status": "BLOCKED", "reason": "not implemented on this node"},
            "4": {"status": "BLOCKED", "reason": "not implemented on this node"},
            "5": {"status": "BLOCKED", "reason": "not implemented on this node"},
            "6": {"status": "BLOCKED", "reason": "not implemented on this node"},
        },
        "release_gate_passed": False,
    }
    write_json(ARTIFACT_ROOT / "claim_ledger.json", ledger)
    eval_lines = [
        "# Cumulative rigorous verification",
        "",
        f"- Claim 1: {summary['status']}",
        "- Claims 2-6: BLOCKED on this intermediate node",
        "- Release gate: FAIL (expected until all six claims are complete)",
        "",
        "The command exits nonzero if Claim 1 or its independent checker fails.",
    ]
    (ARTIFACT_ROOT / "EVAL.md").write_text(
        "\n".join(eval_lines) + "\n", encoding="utf-8"
    )
    print("CLAIM_1_SUMMARY=" + json.dumps(summary, sort_keys=True))
    print(
        "CLAIM_1_INDEPENDENT="
        + json.dumps(
            {
                "passed": independent["passed"],
                "rate_slope": independent["rate_fit"]["slope"],
                "rate_ci95": independent["bootstrap"]["ci95"],
            },
            sort_keys=True,
        )
    )
    print("CUMULATIVE_LEDGER=" + json.dumps(ledger, sort_keys=True))
    print(canonical_json({"claim_1_artifact_dir": str(ARTIFACT_ROOT / "claim_1")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
