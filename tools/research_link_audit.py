#!/usr/bin/env python3
"""Read-only audit of local Markdown links in root-level historical research files."""
from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
import re
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"(?<!!)\[[^\]\n]*\]\((<[^>]+>|[^)\n]+)\)")
SKIP_SCHEMES = ("http:", "https:", "mailto:", "data:", "doi:", "javascript:")


def check_link(root: Path, source: Path, href: str) -> dict | None:
    raw = href.strip().strip("<>").strip()
    if not raw or raw.startswith("#") or raw.lower().startswith(SKIP_SCHEMES):
        return None
    # Treat optional Markdown quoted titles as presentation, not path syntax.
    raw = re.split(r'\s+["\']', raw, maxsplit=1)[0]
    url = urlsplit(raw)
    if url.scheme or url.netloc or not url.path:
        return None
    target = unquote(url.path)
    if "\\" in target or target.startswith("/"):
        return {"status": "REVIEW_UNSAFE_OR_ABSOLUTE_PATH", "href": href}
    candidate = source.parent / target
    base = root.resolve()
    try:
        resolved = candidate.resolve()
        if not resolved.is_relative_to(base):
            return {"status": "REVIEW_PATH_ESCAPES_REPOSITORY", "href": href}
        if candidate.is_symlink():
            return {"status": "REVIEW_SYMLINK", "href": href}
        return {"status": "LOCAL_TARGET_PRESENT" if resolved.exists()
                else "REVIEW_MISSING_LOCAL_TARGET",
                "href": href, "target": resolved.relative_to(base).as_posix()}
    except (OSError, RuntimeError):
        return {"status": "REVIEW_UNRESOLVED_LOCAL_TARGET", "href": href}


def audit(root: Path = ROOT) -> dict:
    base = root / "docs/research"
    if not base.is_dir() or base.is_symlink():
        raise ValueError("research root missing or symlinked")
    issues = []
    counts = {}
    examined = 0
    for source in sorted(base.glob("*.md")):
        if not source.is_file() or source.is_symlink():
            raise ValueError("research entry missing, invalid or symlinked")
        text = source.read_text(encoding="utf-8")
        fence = None
        for number, line in enumerate(text.splitlines(), 1):
            marker = re.match(r"^\s*(`{3,}|~{3,})", line)
            if marker:
                ch = marker.group(1)[0]
                fence = None if fence == ch else ch
                continue
            if fence is not None:
                continue
            for match in LINK.finditer(line):
                finding = check_link(root, source, match.group(1))
                if finding is None:
                    continue
                examined += 1
                counts[finding["status"]] = counts.get(finding["status"], 0) + 1
                if finding["status"] != "LOCAL_TARGET_PRESENT":
                    issues.append({"source": source.relative_to(root).as_posix(),
                                   "line": number, **finding})
    return {"schema": "individual-zero-research-local-links/v1",
            "status": "REVIEW_QUEUE_ONLY", "links_examined": examined,
            "by_status": dict(sorted(counts.items())), "issues": issues,
            "scientific_verdict": "NOT_EVALUATED",
            "warning": "Missing or ambiguous paths are leads for independent review, not authorization to rewrite historical evidence."}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=30)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if args.limit < 0:
        parser.error("--limit must be nonnegative")
    report = audit()
    output = {**report, "total_issues": len(report["issues"]),
              "issues": report["issues"][:args.limit],
              "truncated": len(report["issues"]) > args.limit}
    if args.json:
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        print("Local links:", report["links_examined"], "issues for review:", len(report["issues"]))
        for issue in output["issues"]:
            print(f'{issue["source"]}:{issue["line"]} {issue["status"]}: {issue["href"]}')
        if output["truncated"]:
            print("Use --limit for more findings.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
