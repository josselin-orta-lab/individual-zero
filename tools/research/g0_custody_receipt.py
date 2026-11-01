#!/usr/bin/env python3
"""Offline G0 GitHub-artifact export plan and receipt. No network, engines or births.

The provider SHA-256 is NOT proof of the original M11 ZIP's content, an
independently held archive, an accepted G0 gate, or scientific learning.
"""
from __future__ import annotations

import argparse
import ast
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import stat
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from research_dossiers import audit_g0_inventory, G0_INVENTORY  # noqa: E402

SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")
NAME = re.compile(r"^a1c?-(?:native|reversed)-s[0-9]{1,3}-(?:canonical|td_read_masked)$|^a1c?-aggregate-[0-9]+$")
CAMPAIGNS = ("A1P", "A1C")
ORIGINAL_MAX_BYTES = 128 * 1024 * 1024
A1P_READER_BLOB = "a17201d2bca062c1312bbbce76503ddce9259604"
A1C_READER_BLOB = "d0db46c19f5752236fca080b33e3e4fafeba1cff"
A1C_MANIFEST_SHA256 = "01ac08f8a084dff682256fca721cb6ff0e02b9d085207f088151b76a5e44bfca"
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def trusted_plan(repo_root: Path = ROOT) -> dict:
    """Refuse malformed or scientifically promoted provider metadata."""
    report = audit_g0_inventory(repo_root)
    if report["status"] != "PASS":
        raise ValueError("invalid G0 provider snapshot: " + "; ".join(report["errors"]))
    raw = (repo_root / G0_INVENTORY).read_bytes()
    inventory = json.loads(raw)
    return {
        "status": "PROVIDER_METADATA_PLAN_ONLY",
        "repository": inventory["repository"],
        "observed_on": inventory["observed_on"],
        "inventory_sha256": hashlib.sha256(raw).hexdigest(),
        "campaigns": {
            label: {
                "run_id": inventory["campaigns"][label]["run_id"],
                "run_head_sha": inventory["campaigns"][label]["run_head_sha"],
                "run_conclusion": inventory["campaigns"][label]["run_conclusion"],
                "artifacts": [{
                    "id": item["id"],
                    "name": item["name"],
                    "filename": item["name"] + ".zip",
                    "expected_provider_digest": item["provider_artifact_digest"],
                    "expected_size_bytes": item["size_bytes"],
                    "expires_at": item["expires_at"],
                } for item in inventory["campaigns"][label]["artifact_provider_snapshot"]]
            } for label in CAMPAIGNS
        },
        "original_m11_sha256_verified": False,
        "external_durable_custody_attested": False,
        "scientific_verdict": "NOT_EVALUATED",
    }


def shell_plan(plan: dict) -> str:
    """Print reviewable gh commands. No command execution, auth or download."""
    lines = [
        "# Review before executing. Only copies ephemeral provider packages.",
        "# Set IZ_G0_EXPORT_ROOT to a secure, existing path OUTSIDE the repo.",
        "set -euo pipefail",
        'test -n "$IZ_G0_EXPORT_ROOT"',
        'test -d "$IZ_G0_EXPORT_ROOT" && test ! -L "$IZ_G0_EXPORT_ROOT"',
        '# Private destination must resolve completely outside the Git working tree.',
        'repo_root="$(git rev-parse --show-toplevel)"',
        'private_root="$(cd "$IZ_G0_EXPORT_ROOT" && pwd -P)"',
        'case "$private_root" in "$repo_root"|"$repo_root"/*) echo "Refusing export inside Git repository" >&2; exit 1;; esac',
        "umask 077",
        "gh auth status >&2",
    ]
    for label in CAMPAIGNS:
        lines.append(f'mkdir -p "$IZ_G0_EXPORT_ROOT/{label}"')
        lines.append(f'test ! -L "$IZ_G0_EXPORT_ROOT/{label}"')
        for item in plan["campaigns"][label]["artifacts"]:
            if not NAME.fullmatch(item["name"]) or item["filename"] != item["name"] + ".zip":
                raise ValueError("unsafe artifact name")
            target = f'$IZ_G0_EXPORT_ROOT/{label}/{item["filename"]}'
            api = f'repos/{plan["repository"]}/actions/artifacts/{item["id"]}/zip'
            lines.extend([
                f'# Run {plan["campaigns"][label]["run_id"]}, artifact {item["id"]}, expires {item["expires_at"]}',
                f'test ! -e "{target}" && test ! -L "{target}"',
                f'tmp="$(mktemp "$IZ_G0_EXPORT_ROOT/{label}/.g0-partial.XXXXXXXX")"',
                f'if ! gh api --method GET {shlex.quote(api)} > "$tmp"; then rm -f "$tmp"; exit 1; fi',
                'chmod 600 "$tmp"',
                f'if ! ln "$tmp" "{target}"; then rm -f "$tmp"; exit 1; fi',
                'rm -f "$tmp"',
            ])
    lines.append("# Verify provider bytes offline, then verify original M11 ZIPs separately.")
    return "\n".join(lines) + "\n"


def _hash_regular_no_links(path: Path, expected_size: int) -> tuple[int, str]:
    if path.is_symlink():
        raise ValueError("symlinked provider file: " + path.name)
    before = path.lstat()
    if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
        raise ValueError("absent, hard-linked or non-regular provider file: " + path.name)
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    try:
        opened = os.fstat(fd)
        if (not stat.S_ISREG(opened.st_mode) or opened.st_nlink != 1
                or (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino)):
            raise ValueError("provider file replaced or linked: " + path.name)
        if opened.st_size != expected_size:
            raise ValueError("provider byte size mismatch: " + path.name)
        h = hashlib.sha256()
        with os.fdopen(fd, "rb", closefd=False) as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                h.update(block)
        after = os.fstat(fd)
        if (after.st_size != opened.st_size or after.st_mtime_ns != opened.st_mtime_ns
                or after.st_ctime_ns != opened.st_ctime_ns or after.st_nlink != 1):
            raise ValueError("provider file changed while reading: " + path.name)
        return opened.st_size, h.hexdigest()
    finally:
        os.close(fd)


def verify_provider_exports(root: Path, plan: dict, campaign: str = "ALL") -> dict:
    """Verify complete campaign's provider bytes; never claim M11 custody."""
    if campaign not in (*CAMPAIGNS, "ALL"):
        raise ValueError("unknown G0 campaign")
    if root.is_symlink() or not root.is_dir():
        raise ValueError("export root missing or symlinked")
    if root.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError("private provider exports must remain outside the repository")
    selected = CAMPAIGNS if campaign == "ALL" else (campaign,)
    results = []
    for label in selected:
        folder = root / label
        if folder.is_symlink() or not folder.is_dir():
            raise ValueError("campaign directory missing or symlinked: " + label)
        expected = plan["campaigns"][label]["artifacts"]
        names = {item["filename"] for item in expected}
        observed = {entry.name for entry in folder.iterdir()}
        if observed != names:
            raise ValueError(label + ": missing or unexpected provider files: "
                             + repr(sorted(names ^ observed)))
        for item in expected:
            name = item["name"]
            if not NAME.fullmatch(name) or item["filename"] != name + ".zip":
                raise ValueError("invalid provider filename")
            digest = item["expected_provider_digest"]
            if not SHA256.fullmatch(digest):
                raise ValueError("invalid provider digest in plan")
            size, actual = _hash_regular_no_links(folder / item["filename"],
                                                  item["expected_size_bytes"])
            if "sha256:" + actual != digest:
                raise ValueError("GitHub provider package SHA-256 mismatch: " + name)
            results.append({"campaign": label, "artifact_id": item["id"], "name": name,
                            "bytes": size, "sha256": actual, "provider_package_match": True})
    return {
        "status": "PROVIDER_PACKAGE_BYTES_MATCH_METADATA",
        "verified_provider_packages": len(results),
        "campaign": campaign,
        "complete_two_campaign_provider_set": campaign == "ALL" and len(results) == 58,
        "inventory_sha256": plan["inventory_sha256"],
        "verified_artifacts": results,
        "original_inner_m11_zip_sha256_verified": False,
        "original_m11_chain_audited": False,
        "independent_durable_custody_attested": False,
        "independent_reviewer_attested": False,
        "source_ref_protection_checked_now": False,
        "G0_scientific_gate": "PARTIAL",
        "scientific_verdict": "NOT_EVALUATED",
        "warning": "Provider packages only. Verify inner original M11 ZIPs via the locked A1-P/A1-C readers; preserve copies independently and commission a G0 review.",
    }



def _source_literal(path: Path, expected_blob: str, name: str):
    """Read frozen literal from a pinned reader, without importing/executing it."""
    if path.is_symlink() or not path.is_file():
        raise ValueError("missing or symlinked frozen research reader")
    raw = path.read_bytes()
    sha = hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()
    if sha != expected_blob:
        raise ValueError("frozen reader Git blob changed; independent source review required")
    tree = ast.parse(raw.decode("utf-8"))
    matches = [
        ast.literal_eval(node.value)
        for node in tree.body
        if isinstance(node, (ast.Assign, ast.AnnAssign))
        and (
            (isinstance(node, ast.Assign) and len(node.targets) == 1
             and isinstance(node.targets[0], ast.Name) and node.targets[0].id == name)
            or (isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name)
                and node.target.id == name)
        )
    ]
    if len(matches) != 1:
        raise ValueError("frozen reader missing/duplicate provenance constant: " + name)
    return matches[0]


def _load_small_pinned_json(path: Path, sha256: str) -> dict:
    if not HEX64.fullmatch(sha256):
        raise ValueError("invalid original manifest SHA-256 pin")
    if path.is_symlink() or not path.is_file():
        raise ValueError("missing or linked original manifest")
    st = path.lstat()
    if not stat.S_ISREG(st.st_mode) or st.st_nlink != 1 or st.st_size > 1024 * 1024:
        raise ValueError("unsafe or oversized original manifest")
    if st.st_size <= 0:
        raise ValueError("empty original manifest")
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != sha256:
        raise ValueError("original A1-C manifest SHA-256 differs from frozen research pin")

    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate original manifest JSON key")
            result[key] = value
        return result

    def no_nan(value):
        raise ValueError("nonfinite original manifest value: " + value)

    parsed = json.loads(raw.decode("utf-8"), object_pairs_hook=unique, parse_constant=no_nan)
    if not isinstance(parsed, dict):
        raise ValueError("original manifest root is not a JSON object")
    return parsed


def _original_a1p_expectations(repo_root: Path = ROOT) -> dict:
    frozen = _source_literal(repo_root / "tools/research/i1_a1p_h48_reproduce.py",
                             A1P_READER_BLOB, "ORIGINAL_SHA256")
    if not isinstance(frozen, dict) or len(frozen) != 8:
        raise ValueError("wrong frozen A1-P original count")
    expected = {
        f"a1-{role}-s{seed}-{arm}.zip"
        for role in ("native", "reversed") for seed in (1, 2)
        for arm in ("canonical", "td-read-masked")
    }
    if set(frozen) != expected or any(
            not isinstance(value, str) or not HEX64.fullmatch(value)
            for value in frozen.values()):
        raise ValueError("invalid frozen A1-P original SHA matrix")
    return {key: {"sha256": value, "bytes": None} for key, value in frozen.items()}


def _original_a1c_expectations(manifest: Path, repo_root: Path = ROOT) -> dict:
    recorded = _source_literal(repo_root / "tools/research/i1_a1c_reward_shadow_audit.py",
                               A1C_READER_BLOB, "ORIGINAL_MANIFEST_SHA256")
    if recorded != A1C_MANIFEST_SHA256:
        raise ValueError("original A1-C manifest digest differs from frozen reader")
    data = _load_small_pinned_json(manifest, A1C_MANIFEST_SHA256)
    plan = trusted_plan(repo_root)
    campaign = plan["campaigns"]["A1C"]
    if (data.get("original_run_id") != campaign["run_id"]
            or data.get("original_source_sha") != campaign["run_head_sha"]
            or data.get("archived_independent_lives") != 48):
        raise ValueError("original A1-C manifest cohort/run/source does not match frozen provider provenance")
    records = data.get("original_zip_archives")
    if not isinstance(records, list) or len(records) != 48:
        raise ValueError("wrong original A1-C manifest cohort size")
    expected = {f"a1c-{role}-s{seed}-{arm}.zip" for role in ("native", "reversed")
                for seed in range(101, 113) for arm in ("canonical", "td_read_masked")}
    by_name = {}
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("malformed original A1-C record")
        name, sha, count = record.get("name"), record.get("sha256"), record.get("bytes")
        if (not isinstance(name, str) or name not in expected or name in by_name
                or not isinstance(sha, str) or not HEX64.fullmatch(sha)
                or type(count) is not int or count <= 0 or count > ORIGINAL_MAX_BYTES):
            raise ValueError("malformed, duplicate or unbounded original A1-C archive record")
        by_name[name] = {"sha256": sha, "bytes": count}
    if set(by_name) != expected:
        raise ValueError("incomplete original A1-C manifest original archive names")
    return by_name


def _verify_original_files(original_dir: Path, expected: dict, campaign: str) -> dict:
    """Hash exact historical ZIP file bytes; no decompression or SQLite execution."""
    if original_dir.is_symlink() or not original_dir.is_dir():
        raise ValueError("original M11 directory missing or symlinked")
    if original_dir.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError("original M11 ZIPs must remain outside the repository")
    actual = {entry.name for entry in original_dir.iterdir()}
    if actual != set(expected):
        raise ValueError("missing or unexpected original M11 ZIPs: " + repr(sorted(actual ^ set(expected))))
    verified = []
    for name, record in sorted(expected.items()):
        if (name != Path(name).name or not name.endswith(".zip")
                or not isinstance(record, dict) or not HEX64.fullmatch(record.get("sha256", ""))):
            raise ValueError("invalid historical M11 expectation")
        target = original_dir / name
        before = target.lstat()
        if before.st_size <= 0 or before.st_size > ORIGINAL_MAX_BYTES:
            raise ValueError("invalid original M11 ZIP byte size: " + name)
        size_limit = record.get("bytes")
        if size_limit is not None and (type(size_limit) is not int or size_limit != before.st_size):
            raise ValueError("original M11 byte size differs from frozen manifest: " + name)
        count, digest = _hash_regular_no_links(target, before.st_size)
        if digest != record["sha256"]:
            raise ValueError("original M11 ZIP SHA-256 mismatch: " + name)
        verified.append({"name": name, "bytes": count, "sha256": digest,
                         "historical_pinned_bytes_match": True})
    return {
        "status": "ORIGINAL_M11_ZIP_BYTES_MATCH_HISTORICAL_PINS",
        "campaign": campaign,
        "original_zip_files_checked": len(verified),
        "original_zip_bytes_match_historical_sha256": True,
        "original_zip_files": verified,
        "original_m11_chain_audited": False,
        "original_life_reexecuted": False,
        "independent_source_authentication_attested": False,
        "independent_durable_custody_attested": False,
        "independent_reviewer_attested": False,
        "G0_scientific_gate": "PARTIAL",
        "scientific_verdict": "NOT_EVALUATED",
        "warning": "Original ZIP hashes match frozen project references only; native M11 chain, external custody, independent source authenticity and science remain unreviewed.",
    }


def verify_originals(*, original_dir: Path, campaign: str,
                     manifest: Path | None = None, repo_root: Path = ROOT) -> dict:
    if campaign not in CAMPAIGNS:
        raise ValueError("original verification requires A1P or A1C")
    run = trusted_plan(repo_root)["campaigns"][campaign]
    if campaign == "A1P":
        if manifest is not None:
            raise ValueError("A1-P uses eight frozen hashes, not the A1-C manifest")
        reader = repo_root / "tools/research/i1_a1p_h48_reproduce.py"
        if (_source_literal(reader, A1P_READER_BLOB, "ORIGIN_RUN") != run["run_id"]
                or _source_literal(reader, A1P_READER_BLOB, "SOURCE_SHA") != run["run_head_sha"]):
            raise ValueError("A1-P original SHA list does not match frozen run/source")
        expected = _original_a1p_expectations(repo_root)
        reader_blob = A1P_READER_BLOB
    else:
        if manifest is None:
            raise ValueError("A1-C requires the independently pinned original manifest")
        expected = _original_a1c_expectations(manifest, repo_root)
        reader_blob = A1C_READER_BLOB
    receipt = _verify_original_files(original_dir, expected, campaign)
    receipt["historical_run_id"] = run["run_id"]
    receipt["historical_source_sha"] = run["run_head_sha"]
    receipt["frozen_reader_git_blob_sha1"] = reader_blob
    receipt["historical_original_manifest_sha256"] = (A1C_MANIFEST_SHA256 if campaign == "A1C" else None)
    return receipt


def write_new_receipt(path: Path, receipt: dict) -> None:
    """Explicit private output only, exclusive-create to protect earlier receipts."""
    if path.is_symlink():
        raise ValueError("symlinked receipt destination")
    if path.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError("private custody receipts must remain outside the repository")
    raw = (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode("utf-8")
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL
                 | getattr(os, "O_NOFOLLOW", 0), 0o600)
    try:
        with os.fdopen(fd, "wb", closefd=False) as f:
            f.write(raw)
            f.flush()
            os.fsync(f.fileno())
    finally:
        os.close(fd)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="command", required=True)
    p = subs.add_parser("plan", help="Retrieval metadata only, no network")
    p.add_argument("--shell", action="store_true", help="Print reviewable gh shell commands")
    v = subs.add_parser("verify", help="Verify previously downloaded provider packages")
    v.add_argument("--root", required=True, type=Path)
    v.add_argument("--campaign", choices=["ALL", "A1P", "A1C"], default="ALL")
    v.add_argument("--receipt", type=Path, help="Optionally create a new private receipt")
    o = subs.add_parser("verify-originals", help="Hash original M11 ZIPs against frozen project sources, no M11 replay")
    o.add_argument("--campaign", choices=["A1P", "A1C"], required=True)
    o.add_argument("--originals-dir", required=True, type=Path)
    o.add_argument("--manifest", type=Path, help="Required for A1-C; its entire SHA-256 must match the cold audit's pin")
    o.add_argument("--receipt", type=Path, help="Optional private receipt, create only")
    args = parser.parse_args(argv)
    try:
        plan = trusted_plan()
        if args.command == "plan":
            print(shell_plan(plan) if args.shell else json.dumps(plan, indent=2))
            return 0
        if args.command == "verify-originals":
            receipt = verify_originals(original_dir=args.originals_dir,
                                       campaign=args.campaign, manifest=args.manifest)
        else:
            receipt = verify_provider_exports(args.root, plan, campaign=args.campaign)
        receipt["local_clock_recorded_at_utc"] = datetime.now(timezone.utc).isoformat()
        if args.receipt:
            write_new_receipt(args.receipt, receipt)
        print(json.dumps(receipt, indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print("G0 provider receipt failed: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
