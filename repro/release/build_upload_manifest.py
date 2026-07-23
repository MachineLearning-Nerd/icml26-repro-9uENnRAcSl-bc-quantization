from __future__ import annotations

import hashlib
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUTS = {
    REPO_ROOT / "repro/release/upload_allowlist.json",
    REPO_ROOT / "repro/release/sha256_manifest.json",
}
TEXT_SUFFIXES = {
    ".csv",
    ".json",
    ".lock",
    ".md",
    ".py",
    ".toml",
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _remote_path(relative: Path) -> str:
    value = relative.as_posix()
    if value.startswith(".trackio/logbook/"):
        return value.removeprefix(".trackio/logbook/")
    if value.startswith("repro/release_snapshot/"):
        return value.removeprefix("repro/release_snapshot/")
    return value


def _payload_files() -> list[Path]:
    candidates: set[Path] = set()
    roots = [
        REPO_ROOT / ".trackio/logbook",
        REPO_ROOT / "repro/claims",
        REPO_ROOT / "repro/rigorous",
        REPO_ROOT / "repro/src",
        REPO_ROOT / "repro/release",
        REPO_ROOT / "repro/release_snapshot",
    ]
    for root in roots:
        for path in root.rglob("*"):
            if (
                path.is_file()
                and path.suffix in TEXT_SUFFIXES
                and path not in OUTPUTS
            ):
                candidates.add(path)
    candidates.update(
        {
            REPO_ROOT / "pyproject.toml",
            REPO_ROOT / "uv.lock",
        }
    )
    return sorted(candidates)


def main() -> int:
    entries = []
    for path in _payload_files():
        relative = path.relative_to(REPO_ROOT)
        entries.append(
            {
                "operation": "add",
                "local_path": relative.as_posix(),
                "path_in_repo": _remote_path(relative),
                "bytes": path.stat().st_size,
                "sha256": _sha256(path),
            }
        )
    remote_paths = [entry["path_in_repo"] for entry in entries]
    if len(remote_paths) != len(set(remote_paths)):
        raise AssertionError("duplicate remote path in upload allowlist")
    allowlist = {
        "space_id": "DineshAI/9uENnRAcSl",
        "base_revision": "cbdb6955777b019e1787d7fc6d7208841fa6ec4d",
        "policy": "text-only additions/updates; no delete operations",
        "entry_count": len(entries),
        "entries": entries,
    }
    hashes = {
        entry["path_in_repo"]: {
            "bytes": entry["bytes"],
            "sha256": entry["sha256"],
        }
        for entry in entries
    }
    (REPO_ROOT / "repro/release/upload_allowlist.json").write_text(
        json.dumps(allowlist, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (REPO_ROOT / "repro/release/sha256_manifest.json").write_text(
        json.dumps(hashes, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"UPLOAD_ALLOWLIST_ENTRIES={len(entries)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
