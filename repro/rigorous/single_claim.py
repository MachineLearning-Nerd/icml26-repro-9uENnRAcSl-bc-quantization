from __future__ import annotations

import json
from typing import Any

from .claim1 import run_claim_1
from .claim2 import run_claim_2
from .claim346 import run_claims_3_4_6
from .claim5 import run_claim_5
from .independent_check_1 import check_claim_1
from .independent_check_2 import check_claim_2
from .independent_check_346 import (
    check_claim_3,
    check_claim_4,
    check_claim_6,
)
from .independent_check_5 import check_claim_5


def verify_single_claim(claim: int) -> tuple[dict[str, Any], dict[str, Any]]:
    if claim == 1:
        summary, independent = run_claim_1(), check_claim_1()
    elif claim == 2:
        summary, independent = run_claim_2(), check_claim_2()
    elif claim == 5:
        summary, independent = run_claim_5(), check_claim_5()
    elif claim in {3, 4, 6}:
        summaries = run_claims_3_4_6()
        checkers = {
            3: check_claim_3,
            4: check_claim_4,
            6: check_claim_6,
        }
        summary, independent = summaries[str(claim)], checkers[claim]()
    else:
        raise ValueError(f"unsupported claim: {claim}")
    print(
        f"CLAIM_{claim}_SUMMARY="
        + json.dumps(summary, sort_keys=True)
    )
    print(
        f"CLAIM_{claim}_INDEPENDENT="
        + json.dumps(independent, sort_keys=True)
    )
    return summary, independent


def main_for(claim: int) -> int:
    summary, independent = verify_single_claim(claim)
    complete = (
        summary["status"] in {"VERIFIED", "FALSIFIED"}
        and summary["passed"]
        and independent["passed"]
    )
    return 0 if complete else 1
