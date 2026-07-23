from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
ALLOWLIST_PATH = REPO_ROOT / "repro/release/upload_allowlist.json"
MANIFEST_PATH = REPO_ROOT / "repro/release/sha256_manifest.json"
PROTECTED_PATH = REPO_ROOT / "repro/release/protected_space_manifest.json"
SNAPSHOT_ROOT = REPO_ROOT / "repro/release_snapshot/evidence"
GENERATED_ROOT = REPO_ROOT / ".openresearch/artifacts"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git_blob_oid(path: Path) -> str:
    content = path.read_bytes()
    header = f"blob {len(content)}\0".encode()
    return hashlib.sha1(header + content).hexdigest()


def _parents(path: str) -> set[str]:
    parts = Path(path).parts
    return {
        Path(*parts[:index]).as_posix()
        for index in range(1, len(parts))
    }


def _json_shape(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _json_shape(child)
            for key, child in sorted(value.items())
        }
    if isinstance(value, list):
        unique_shapes = {
            json.dumps(_json_shape(child), sort_keys=True)
            for child in value
        }
        return {
            "type": "list",
            "length": len(value),
            "item_shapes": sorted(unique_shapes),
        }
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "int"
    if isinstance(value, float):
        return "float"
    if isinstance(value, str):
        return "str"
    raise TypeError(f"unsupported JSON value: {type(value)!r}")


def validate_release(ledger: dict[str, Any]) -> dict[str, Any]:
    allowlist = json.loads(ALLOWLIST_PATH.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    protected = json.loads(PROTECTED_PATH.read_text(encoding="utf-8"))
    entries = allowlist["entries"]

    payload_hashes_match = all(
        entry["operation"] == "add"
        and (REPO_ROOT / entry["local_path"]).is_file()
        and (REPO_ROOT / entry["local_path"]).stat().st_size
        == entry["bytes"]
        and _sha256(REPO_ROOT / entry["local_path"]) == entry["sha256"]
        and manifest[entry["path_in_repo"]]["sha256"] == entry["sha256"]
        and manifest[entry["path_in_repo"]]["bytes"] == entry["bytes"]
        for entry in entries
    )
    remote_files = {entry["path_in_repo"] for entry in entries}
    protected_files = {
        entry["path"]
        for entry in protected["entries"]
        if entry["type"] == "file"
    }
    candidate_paths = protected_files | remote_files
    candidate_paths |= {
        parent
        for path in candidate_paths
        for parent in _parents(path)
    }
    protected_paths = {entry["path"] for entry in protected["entries"]}

    expected_legacy_oids = {
        "pages/legacy/logbook.json": "c61e4913387cedd3d84079352c89bf07306fe3bf",
        "pages/legacy/index.md": "483faf724e81ecae85d7231291973b6d0ed8bdfa",
        "pages/legacy/overview/page.md": "1f939aa1b7d3128df26a194cf58aa036e3f3e482",
        "pages/legacy/claims/page.md": "4cd2d59231ed134507be27293017e059f17055ab",
        "pages/legacy/evidence/page.md": "f6378f1c74e060f45aa0b010ec71dad2839b2ce1",
        "pages/legacy/verification-run/page.md": "cc494ba81587eb41f0cd247027e7ddb45c466c73",
        "pages/legacy/conclusion/page.md": "36484980be5546da396c6fbf8f3eab68bbe454d5",
    }
    legacy_exact = all(
        _git_blob_oid(REPO_ROOT / ".trackio/logbook" / path) == oid
        for path, oid in expected_legacy_oids.items()
    )
    snapshot_hashes = {}
    generated_hashes = {}
    raw_schema_matches = True
    for claim in range(1, 7):
        snapshot_path = (
            SNAPSHOT_ROOT / f"claim_{claim}/raw_results.json"
        )
        generated_path = (
            GENERATED_ROOT / f"claim_{claim}/raw_results.json"
        )
        snapshot_hashes[str(claim)] = _sha256(snapshot_path)
        generated_hashes[str(claim)] = _sha256(generated_path)
        snapshot_raw = json.loads(snapshot_path.read_text(encoding="utf-8"))
        generated_raw = json.loads(generated_path.read_text(encoding="utf-8"))
        raw_schema_matches &= (
            _json_shape(snapshot_raw) == _json_shape(generated_raw)
        )
    claim_statuses_complete = all(
        ledger["claims"][str(claim)]["status"]
        in {"VERIFIED", "FALSIFIED"}
        and ledger["claims"][str(claim)]["producer_passed"]
        and ledger["claims"][str(claim)]["independent_checker_passed"]
        for claim in range(1, 7)
    )
    wrappers_present = all(
        (REPO_ROOT / f"repro/src/verify_claim_{claim}.py").is_file()
        for claim in range(1, 7)
    )

    secret_patterns = [
        re.compile(r"hf_[A-Za-z0-9]{20,}"),
        re.compile(r"(?i)bearer\s+[A-Za-z0-9._-]{16,}"),
        re.compile(r"(?i)(api[_-]?key|access[_-]?token)\s*[:=]\s*['\"][^'\"]+"),
    ]
    secret_hits = []
    for entry in entries:
        path = REPO_ROOT / entry["local_path"]
        text = path.read_text(encoding="utf-8")
        if any(pattern.search(text) for pattern in secret_patterns):
            secret_hits.append(entry["local_path"])

    checks = {
        "six_exact_claims": set(ledger["claims"]) == {
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
        },
        "claim_statuses_complete": claim_statuses_complete,
        "all_claims_release_gate": ledger["release_gate_passed"],
        "per_claim_wrappers_present": wrappers_present,
        "raw_results_regenerate_with_snapshot_schema": raw_schema_matches,
        "payload_hashes_match_manifest": payload_hashes_match,
        "text_only_add_operations": all(
            entry["operation"] == "add"
            and Path(entry["path_in_repo"]).suffix
            in {".csv", ".json", ".lock", ".md", ".py", ".toml"}
            for entry in entries
        ),
        "protected_path_set_is_subset": protected_paths <= candidate_paths,
        "protected_legacy_markdown_exact": legacy_exact,
        "no_secret_patterns": not secret_hits,
        "no_vacuous_legacy_predicate_in_current_verifiers": not re.search(
            r"(?m)^\s*(?:if\s+|[A-Za-z_]\w*\s*=\s*)"
            r"reg_min\s*>=\s*0",
            (REPO_ROOT / "repro/rigorous/claim5.py").read_text(
                encoding="utf-8"
            ),
        ),
    }
    result = {
        "checks": checks,
        "passed": bool(all(checks.values())),
        "upload_entry_count": len(entries),
        "protected_path_count": len(protected_paths),
        "candidate_path_count": len(candidate_paths),
        "secret_hit_paths": secret_hits,
        "snapshot_raw_sha256": snapshot_hashes,
        "generated_raw_sha256": generated_hashes,
        "bitwise_identity_required": False,
        "cross_platform_acceptance": (
            "matching raw schema/shape plus every claim-specific numerical "
            "or symbolic producer and independent-checker gate"
        ),
    }
    if not result["passed"]:
        raise AssertionError(f"release validation failed: {result}")
    return result
