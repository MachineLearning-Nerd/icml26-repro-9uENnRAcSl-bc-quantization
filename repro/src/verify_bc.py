"""Cumulative fail-closed verifier for arXiv 2603.20538."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from repro.rigorous.claim1 import run_claim_1
from repro.rigorous.claim2 import run_claim_2
from repro.rigorous.claim346 import run_claims_3_4_6
from repro.rigorous.claim5 import run_claim_5
from repro.rigorous.common import ARTIFACT_ROOT, canonical_json, write_json
from repro.rigorous.independent_check_1 import check_claim_1
from repro.rigorous.independent_check_2 import check_claim_2
from repro.rigorous.independent_check_346 import (
    check_claim_3,
    check_claim_4,
    check_claim_6,
)
from repro.rigorous.independent_check_5 import check_claim_5
from repro.release.validate_release import validate_release


def main() -> int:
    summaries = {
        "1": run_claim_1(),
        "2": run_claim_2(),
        "5": run_claim_5(),
    }
    summaries.update(run_claims_3_4_6())
    independent = {
        "1": check_claim_1(),
        "2": check_claim_2(),
        "5": check_claim_5(),
    }
    independent.update(
        {
            "3": check_claim_3(),
            "4": check_claim_4(),
            "6": check_claim_6(),
        }
    )
    ledger = {
        "paper": "Understanding Behavior Cloning with Action Quantization",
        "arxiv": "2603.20538",
        "claims": {
            "1": {
                "status": summaries["1"]["status"],
                "producer_passed": summaries["1"]["passed"],
                "independent_checker_passed": independent["1"]["passed"],
            },
            "2": {
                "status": summaries["2"]["status"],
                "producer_passed": summaries["2"]["passed"],
                "independent_checker_passed": independent["2"]["passed"],
            },
            "3": {"status": summaries["3"]["status"], "producer_passed": summaries["3"]["passed"], "independent_checker_passed": independent["3"]["passed"]},
            "4": {"status": summaries["4"]["status"], "producer_passed": summaries["4"]["passed"], "independent_checker_passed": independent["4"]["passed"]},
            "5": {
                "status": summaries["5"]["status"],
                "theorem_8_status": summaries["5"]["theorem_8_status"],
                "theorem_9_status": summaries["5"]["theorem_9_status"],
                "producer_passed": summaries["5"]["passed"],
                "independent_checker_passed": independent["5"]["passed"],
            },
            "6": {"status": summaries["6"]["status"], "producer_passed": summaries["6"]["passed"], "independent_checker_passed": independent["6"]["passed"]},
        },
        "release_gate_passed": all(
            summaries[claim]["status"] in {"VERIFIED", "FALSIFIED"}
            and summaries[claim]["passed"]
            and independent[claim]["passed"]
            for claim in ["1", "2", "3", "4", "5", "6"]
        ),
    }
    write_json(ARTIFACT_ROOT / "claim_ledger.json", ledger)
    eval_lines = [
        "# Cumulative rigorous verification",
        "",
        f"- Claim 1: {summaries['1']['status']}",
        f"- Claim 2: {summaries['2']['status']}",
        f"- Claim 3: {summaries['3']['status']}",
        f"- Claim 4: {summaries['4']['status']}",
        f"- Claim 5: {summaries['5']['status']} "
        f"(Theorem 8: {summaries['5']['theorem_8_status']}; "
        f"Theorem 9: {summaries['5']['theorem_9_status']})",
        f"- Claim 6: {summaries['6']['status']}",
        f"- Release gate: {'PASS' if ledger['release_gate_passed'] else 'FAIL'}",
        "",
        "The command exits nonzero if any implemented claim or independent "
        "checker fails.",
    ]
    (ARTIFACT_ROOT / "EVAL.md").write_text(
        "\n".join(eval_lines) + "\n", encoding="utf-8"
    )
    for claim in ["1", "2", "3", "4", "5", "6"]:
        print(
            f"CLAIM_{claim}_SUMMARY="
            + json.dumps(summaries[claim], sort_keys=True)
        )
        print(
            f"CLAIM_{claim}_INDEPENDENT="
            + json.dumps(
                {
                    "passed": independent[claim]["passed"],
                    "checks": independent[claim]["checks"],
                },
                sort_keys=True,
            )
        )
    print("CUMULATIVE_LEDGER=" + json.dumps(ledger, sort_keys=True))
    release_validation = validate_release(ledger)
    print(
        "RELEASE_VALIDATION="
        + json.dumps(release_validation, sort_keys=True)
    )
    print(
        canonical_json(
            {
                "artifact_dirs": {
                    claim: str(ARTIFACT_ROOT / f"claim_{claim}")
                    for claim in ["1", "2", "3", "4", "5", "6"]
                }
            }
        )
    )
    implemented_passed = all(
        summaries[claim]["passed"] and independent[claim]["passed"]
        for claim in ["1", "2", "3", "4", "5", "6"]
    )
    return 0 if implemented_passed and release_validation["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
