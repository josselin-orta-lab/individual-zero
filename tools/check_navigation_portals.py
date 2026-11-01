#!/usr/bin/env python3
"""Fail-closed link check for current navigation portals, not historical reports."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
PORTALS = (
    "docs/research/studies/README.md",
    "tests/research/README.md",
    "tests/research/a2r/README.md",
    "archive/README.md",
)
LINK = re.compile(r"(?<!!)\[[^\]\n]*\]\((<[^>]+>|[^)\n]+)\)")


def audit(root: Path = ROOT, portals: tuple[str, ...] = PORTALS) -> dict:
    """Check local Markdown links outside code fences, without writing files."""
    base = root.resolve()
    problems = []
    checked = 0
    for name in portals:
        source = root / name
        if source.is_symlink() or not source.is_file():
            problems.append({"source": name, "line": 0, "reason": "MISSING_OR_SYMLINK_PORTAL"})
            continue
        fence = None
        for line_no, line in enumerate(source.read_text(encoding="utf-8").splitlines(), 1):
            marker = re.match(r"^\s*(`{3,}|~{3,})", line)
            if marker:
                char = marker.group(1)[0]
                fence = None if fence == char else char
                continue
            if fence is not None:
                continue
            for match in LINK.finditer(line):
                raw = match.group(1).strip().strip("<>")
                if not raw or raw.startswith("#"):
                    continue
                href = re.split(r'\s+["\']', raw, maxsplit=1)[0]
                url = urlsplit(href)
                if url.scheme or url.netloc or not url.path:
                    continue
                target = unquote(url.path)
                checked += 1
                if "\\" in target or target.startswith("/"):
                    problems.append({"source": name, "line": line_no, "reason": "UNSAFE_LINK", "href": raw})
                    continue
                candidate = source.parent / target
                resolved = candidate.resolve()
                if (not resolved.is_relative_to(base) or candidate.is_symlink()
                        or not resolved.exists()):
                    problems.append({"source": name, "line": line_no,
                                     "reason": "UNRESOLVED_OR_UNSAFE_LOCAL_LINK", "href": raw})
    return {"status": "PASS" if not problems else "FAIL", "local_links_checked": checked,
            "problems": problems, "scientific_verdict": "NOT_EVALUATED"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = audit()
    print(json.dumps(report, indent=2) if args.json else
          f"{report['status']}: {report['local_links_checked']} local navigation links; "
          f"{len(report['problems'])} broken or unsafe")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
