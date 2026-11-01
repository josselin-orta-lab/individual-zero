#!/usr/bin/env python3
"""Offline G0 GitHub-artifact export plan and receipt. No network, engines or births.

The provider SHA-256 is NOT proof of the original M11 ZIP's content, an
independently held archive, an accepted G0 gate, or scientific learning.
"""
from __future__ import annotations

import argparse
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


def write_new_receipt(path: Path, receipt: dict) -> None:
    """Explicit private output only, exclusive-create to protect earlier receipts."""
    if path.is_symlink():
        raise ValueError("symlinked receipt destination")
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
    args = parser.parse_args(argv)
    try:
        plan = trusted_plan()
        if args.command == "plan":
            print(shell_plan(plan) if args.shell else json.dumps(plan, indent=2))
            return 0
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
