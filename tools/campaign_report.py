#!/usr/bin/env python3
"""Produce factual, local engine campaign evidence; no remote CI-status oracle.

Read only an actual checked-out Git HEAD, engine contract, recorded suite JSON,
and JUnit results. Report unobserved gates explicitly. GitHub run metadata are
labels from the environment, *not* proof the overall workflow succeeded.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SUITES = ("structure", "smoke", "full", "m11", "source")
REPO_NAME = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z")


def _git_head(root: Path) -> str:
    check = subprocess.run(
        ["git", "rev-parse", "--verify", "HEAD"],
        cwd=root, capture_output=True, text=True, check=False,
    )
    if check.returncode or not re.fullmatch(r"[0-9a-f]{40}", check.stdout.strip()):
        raise ValueError("not an authenticated Git HEAD")
    return check.stdout.strip()


def _read_suite(path: Path, sha: str, engine: str, suite: str) -> dict:
    if not path.is_file():
        return {"status": "NOT_OBSERVED", "file": path.name}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        if (raw["engine"] != engine or raw["suite"] != suite
                or raw.get("local_head") != sha or raw.get("executed") is not True
                or raw.get("scientific_gate") != "NOT_EVALUATED"):
            raise ValueError("suite provenance or execution mismatch")
        steps = raw["steps"]
        if not isinstance(steps, list) or not steps:
            raise ValueError("empty recorded suite")
        if raw["status"] not in ("PASS", "FAIL"):
            raise ValueError("record not an executed result")
        if raw["status"] == "PASS" and not all(
            step.get("status") == "PASS" and step.get("returncode") == 0
            for step in steps
        ):
            raise ValueError("passing suite contains unverified step")
        return {"status": raw["status"], "file": path.name,
                "observed_steps": len(steps)}
    except (OSError, UnicodeError, ValueError, KeyError, TypeError) as exc:
        return {"status": "INVALID", "file": path.name, "reason": str(exc)}


def _read_junit(path: Path) -> dict:
    if not path.is_file():
        return {"status": "NOT_OBSERVED", "file": path.name}
    try:
        root = ET.parse(path).getroot()
        suites = [root] if root.tag == "testsuite" else list(root.findall("testsuite"))
        if not suites or root.tag not in ("testsuite", "testsuites"):
            raise ValueError("not JUnit XML")
        counts = {
            "tests": sum(int(s.attrib["tests"]) for s in suites),
            "failures": sum(int(s.attrib.get("failures", 0)) for s in suites),
            "errors": sum(int(s.attrib.get("errors", 0)) for s in suites),
            "skipped": sum(int(s.attrib.get("skipped", 0)) for s in suites),
        }
        if counts["tests"] < 1:
            raise ValueError("zero tests reported")
        return {"status": ("FAIL" if counts["failures"] or counts["errors"]
                          else "PASS"), "file": path.name, **counts}
    except (ET.ParseError, OSError, UnicodeError, ValueError, KeyError) as exc:
        return {"status": "INVALID", "file": path.name, "reason": str(exc)}


def generate_report(*, root: Path, report_dir: Path, engine: str,
                    python_version: str, env: dict[str, str] | None = None) -> dict:
    env = dict(os.environ) if env is None else env
    sha = _git_head(root)
    registry = json.loads((root / "config/engine-registry.json").read_text())
    if engine != registry["active_generation"] or engine not in registry["generations"]:
        raise ValueError("only the registered current engine can issue this report")
    entry = registry["generations"][engine]
    contract_path = root / entry["source"] / "engine.json"
    contract_bytes = contract_path.read_bytes()
    contract = json.loads(contract_bytes)
    if contract["generation"] != engine or contract["status"] != "active":
        raise ValueError("engine contract disagrees with active generation")
    if contract["validation"]["workflow"] != entry["ci"]:
        raise ValueError("workflow path does not match registry")
    if not re.fullmatch(r"[0-9]+\.[0-9]+", python_version):
        raise ValueError("invalid Python version identifier")
    suite_evidence = {
        key: _read_suite(
            report_dir / f"{engine.lower()}-{key}-{python_version}.json",
            sha, engine, key,
        )
        for key in ("structure", "m11", "source")
    }
    junit = {
        "smoke": _read_junit(
            report_dir / f"{engine.lower()}-{python_version}.xml"
        ),
        "full": _read_junit(
            report_dir / f"{engine.lower()}-full-{python_version}.xml"
        ),
    }
    all_evidence = [*suite_evidence.values(), *junit.values()]
    failures = any(e["status"] in ("INVALID", "FAIL") for e in all_evidence)
    missing = [name for name, item in {**suite_evidence, **junit}.items()
               if item["status"] == "NOT_OBSERVED"]
    status = "EVIDENCE_FAILURE" if failures else (
        "RECORDED_SOFTWARE_GATES_PASS" if not missing else "PARTIAL_EVIDENCE"
    )
    repository = env.get("GITHUB_REPOSITORY", "")
    run_id = env.get("GITHUB_RUN_ID", "")
    metadata = {
        "provider": "github_actions" if env.get("GITHUB_ACTIONS") == "true" else "local",
        "repository": repository if REPO_NAME.fullmatch(repository) else None,
        "run_id": run_id if run_id.isdigit() else None,
        "event_sha": env.get("GITHUB_SHA") or None,
        "head_ref": env.get("GITHUB_HEAD_REF") or None,
        "base_ref": env.get("GITHUB_BASE_REF") or None,
        "event_name": env.get("GITHUB_EVENT_NAME") or None,
    }
    return {
        "schema": "individual-zero-campaign-evidence/v1",
        "engine": engine,
        "source_of_truth": "LOCAL_CHECKOUT_AND_RECORDED_FILES_ONLY",
        "local_head": sha,
        "python_version": python_version,
        "contract": {"path": str(contract_path.relative_to(root)),
                     "sha256": sha256(contract_bytes).hexdigest()},
        "run_context": metadata,
        "software": {"status": status,
                     "note": "These results do not certify the whole GitHub workflow",
                     "suites": suite_evidence, "junit": junit,
                     "not_observed": missing},
        "scientific": {"status": "NOT_EVALUATED",
                       "stage10_nonempty_publication": "NOT_PROVEN",
                       "long_horizon_emergence": "NOT_PROVEN"},
        "merge_status": "NOT_VERIFIED_WITH_GITHUB",
    }


def markdown_report(report: dict) -> str:
    soft = report["software"]
    lines = [
        f"# {report['engine']} engineering campaign evidence",
        "",
        f"- Git HEAD: \`{report['local_head']}\`",
        f"- Python: \`{report['python_version']}\`",
        f"- Software evidence: **{soft['status']}**",
        f"- Scientific conclusion: **NOT EVALUATED**",
        "- GitHub PR / merge status: **NOT VERIFIED by this local report**",
        "",
        "| Gate | Recorded result |",
        "| --- | --- |",
    ]
    for key, val in {**soft["suites"], **soft["junit"]}.items():
        lines.append(f"| {key} | {val['status']} |")
    lines += ["", "Unobserved evidence is not considered passing. "
              "Read the actual GitHub Actions run for the final workflow result.", ""]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--engine", required=True)
    ap.add_argument("--reports-dir", type=Path, default=ROOT / "reports")
    ap.add_argument("--python-version", required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--markdown-output", type=Path)
    args = ap.parse_args()
    try:
        report = generate_report(
            root=ROOT, report_dir=args.reports_dir, engine=args.engine,
            python_version=args.python_version,
        )
    except (OSError, ValueError, KeyError) as exc:
        print(f"campaign report refused: {exc}", file=sys.stderr)
        return 2
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if args.markdown_output:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_output.write_text(markdown_report(report), encoding="utf-8")
    print(f"CAMPAIGN_REPORT {report['engine']} "
          f"{report['local_head'][:12]} {report['software']['status']}")
    return 1 if report["software"]["status"] == "EVIDENCE_FAILURE" else 0


if __name__ == "__main__":
    sys.exit(main())
