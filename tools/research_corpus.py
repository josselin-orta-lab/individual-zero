#!/usr/bin/env python3
"""Incremental research corpus inventory and unverified cross-document leads.

Read-only unless --output explicitly specifies an inventory destination. Standard
library only; never loads an engine, executes a study, or approves scientific gates.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
PROGRAM = "config/research-program.json"
SCHEMA = "individual-zero-research-corpus/v1"
REPOSITORY = "josselin-orta-lab/individual-zero"
DEFAULT_MAX_BYTES = 1024 * 1024
MAX_DOCUMENTS = 10000
MAX_MENTIONS = 48
MAX_LINKS = 60
MAX_TOPICS = 60
SHA40 = re.compile(r"^[a-f0-9]{40}$")
EXPERIMENT = re.compile(r"(?<![\w-])EXP-([0-9]{4,6})(?![\w-])", re.I)
STUDY = re.compile(r"(?<![\w-])(?:A1-P|A1-C|A2-R)(?![\w-])", re.I)
ADR = re.compile(r"(?<![\w-])ADR-([0-9]{4,6})(?![\w-])", re.I)
ISSUE = re.compile(r"\bissues?\s*#?([1-9][0-9]{1,5})\b", re.I)
ISSUE_URL = re.compile(
    r"https://github\.com/josselin-orta-lab/individual-zero/issues/([1-9][0-9]{1,5})\b", re.I)
ISSUE_HEADING = re.compile(r"^\s*#{1,6}\s+#([1-9][0-9]{1,5})\b")
ISSUE_FILENAME = re.compile(r"^(?:EXPERIMENT|ISSUE)_([1-9][0-9]{1,5})(?:_|\.|$)", re.I)
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]\n]+\]\(([^)\n]+)\)")
CODE_FENCE = re.compile(r"^\s*(\x60{3,}|~{3,})")
# All signals are *mentions*, not verdicts. PASS is not scientific GO.
SIGNALS = [
    ("NO_GO", re.compile(r"(?<![\w])NO[_ -]GO(?![\w])", re.I)),
    ("NOT_EXECUTED", re.compile(r"(?<![\w])NOT[_ -]EXECUTED(?![\w])", re.I)),
    ("NOT_ESTABLISHED", re.compile(r"(?<![\w])NOT[_ -]ESTABLISHED(?![\w])", re.I)),
    ("NOT_OBSERVED", re.compile(r"(?<![\w])NOT[_ -]OBSERVED(?![\w])", re.I)),
    ("INCONCLUSIVE", re.compile(r"\bINCONCLUSIVE\b|\bINDETERMINATE\b|\bINDETERMINE\b", re.I)),
    ("REVIEW_REQUIRED", re.compile(r"(?<![\w])REVIEW[_ -]REQUIRED(?![\w])", re.I)),
    ("APPROVED_MENTION", re.compile(r"\bAPPROVED\b|\bAPPROUV[ÉE]\b", re.I)),
    ("PASS_MENTION", re.compile(r"(?<![\w])PASS(?![\w])", re.I)),
]
# Filename-only hints are not scientific classifications. The order is deliberate.
KIND_HINTS = [
    ("possible_preregistration", ("prereg", "pre-registration", "preenregistrement")),
    ("possible_results", ("results", "resultat", "result")),
    ("possible_protocol", ("protocol", "protocole")),
    ("possible_decision", ("decision", "verdict")),
    ("possible_review", ("review", "relecture")),
    ("possible_audit", ("audit", "inspection")),
    ("possible_status", ("status", "etat")),
    ("possible_proposal", ("proposal", "proposition")),
]


def safe_relative(value: str) -> bool:
    if not isinstance(value, str) or not value or "\\" in value or value.startswith("/"):
        return False
    parts = PurePosixPath(value).parts
    return bool(parts) and all(p not in (".", "..") for p in parts)


def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def git_sha(root: Path) -> str:
    try:
        result = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                                text=True, capture_output=True, check=True, timeout=3)
        sha = result.stdout.strip().lower()
        return sha if SHA40.fullmatch(sha) else "UNKNOWN"
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return "UNKNOWN"


def load_roots(root: Path) -> list[str]:
    program = json.loads((root / PROGRAM).read_text(encoding="utf-8"))
    roots = program["catalog_roots"]
    if not isinstance(roots, list) or not roots or len(roots) != len(set(roots)):
        raise ValueError("catalog_roots must be a nonempty unique list")
    if any(not safe_relative(s) for s in roots):
        raise ValueError("unsafe catalog root")
    normalized = [s.rstrip("/") for s in roots]
    for i, first in enumerate(normalized):
        if any(i != j and first.startswith(other + "/")
               for j, other in enumerate(normalized)):
            raise ValueError("overlapping catalog roots are not permitted")
    return sorted(normalized)


def collect_paths(root: Path, roots: list[str]) -> tuple[list[str], list[str]]:
    base = root.resolve()
    docs: list[str] = []
    skipped: list[str] = []
    for folder in roots:
        if not safe_relative(folder):
            raise ValueError("unsafe catalog path: " + str(folder))
        located = root / folder
        if located.is_symlink() or not located.is_dir() or not located.resolve().is_relative_to(base):
            raise ValueError("catalog root missing/symlink/escape: " + folder)
        for current, dirs, names in os.walk(located, topdown=True, followlinks=False):
            cur = Path(current)
            dirs[:] = sorted(d for d in dirs if not (cur / d).is_symlink())
            for name in sorted(names):
                target = cur / name
                if target.suffix.lower() != ".md":
                    continue
                rel = target.relative_to(root).as_posix()
                if (target.is_symlink() or not target.is_file()
                        or not target.resolve().is_relative_to(base)):
                    skipped.append(rel)
                else:
                    docs.append(rel)
                if len(docs) + len(skipped) > MAX_DOCUMENTS:
                    raise ValueError("corpus path limit exceeded")
    if len(set(docs)) != len(docs):
        raise ValueError("duplicate catalog document path")
    return sorted(docs), sorted(skipped)


def kind_hint(path: str) -> str:
    name = Path(path).stem.lower()
    for label, needles in KIND_HINTS:
        if any(part in name for part in needles):
            return label
    return "unknown_document_kind"


def generation_scope(path: str) -> str:
    if path.startswith("src/i1/"):
        return "I1_DOCUMENTATION"
    if path.startswith("src/i2/"):
        return "I2_DOCUMENTATION"
    if path.startswith("docs/architecture/proposals/"):
        return "ARCHITECTURE_PROPOSAL"
    if "/archive/" in path or "STATUS_HISTORY" in path:
        return "HISTORICAL_LOCATION"
    return "GENERATION_NOT_INFERRED"


def parse_links(path: str, line: str, line_no: int, root: Path) -> list[dict]:
    found = []
    for match in MARKDOWN_LINK.finditer(line):
        raw = match.group(1).strip().strip("<>")
        if not raw or raw.startswith(("#", "mailto:", "data:", "http:", "https:")):
            continue
        url = urlsplit(raw)
        if url.scheme or url.netloc:
            continue
        target = unquote(url.path)
        if not target or "\\" in target:
            continue
        resolved = (root / path).parent.joinpath(target).resolve()
        if not resolved.is_relative_to(root.resolve()):
            continue
        if resolved.suffix.lower() != ".md":
            continue
        found.append({"target": resolved.relative_to(root.resolve()).as_posix(),
                      "line": line_no, "target_exists": resolved.is_file(),
                      "relation": "EXPLICIT_MARKDOWN_LINK_NOT_AUTHORITY"})
        if len(found) >= MAX_LINKS:
            break
    return found


def add_ref(refs: dict[str, int], label: str, line: int) -> None:
    if label not in refs and len(refs) < MAX_TOPICS:
        refs[label] = line


def extract_metadata(root: Path, path: str, raw: bytes, max_bytes: int) -> dict:
    entry = {"path": path, "blob_sha": git_blob(raw), "bytes": len(raw),
             "generation_scope": generation_scope(path), "filename_hint": kind_hint(path),
             "title": None, "topics": [], "status_mentions": [], "links": [],
             "parse_status": "NOT_PARSED", "scientific_verdict": "NOT_EVALUATED"}
    if len(raw) > max_bytes:
        entry["parse_status"] = "TOO_LARGE_SKIPPED"
        return entry
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        entry["parse_status"] = "INVALID_UTF8_SKIPPED"
        return entry
    refs: dict[str, int] = {}
    filename = Path(path).name
    issue_match = ISSUE_FILENAME.search(filename)
    if issue_match:
        add_ref(refs, "issue:" + issue_match.group(1), 0)
    for pattern, prefix in ((EXPERIMENT, "exp:"), (STUDY, "study:"), (ADR, "adr:")):
        for match in pattern.finditer(filename):
            add_ref(refs, prefix + match.group(0).upper(), 0)
    fence_token: str | None = None
    for line_no, line in enumerate(text.splitlines(), 1):
        fence = CODE_FENCE.match(line)
        if fence:
            marker = fence.group(1)
            if fence_token is None:
                fence_token = marker[0]
            elif fence_token == marker[0]:
                fence_token = None
            continue
        if fence_token is not None:
            continue
        if entry["title"] is None and re.match(r"^#\s+\S", line):
            entry["title"] = line[2:].strip()[:180]
        for m in ISSUE.finditer(line):
            add_ref(refs, "issue:" + m.group(1), line_no)
        for m in ISSUE_URL.finditer(line):
            add_ref(refs, "issue:" + m.group(1), line_no)
        heading_issue = ISSUE_HEADING.match(line)
        if heading_issue:
            add_ref(refs, "issue:" + heading_issue.group(1), line_no)
        for pattern, prefix in ((EXPERIMENT, "exp:"), (STUDY, "study:"), (ADR, "adr:")):
            for m in pattern.finditer(line):
                add_ref(refs, prefix + m.group(0).upper(), line_no)
        if len(entry["status_mentions"]) < MAX_MENTIONS:
            statuses = [label for label, expression in SIGNALS if expression.search(line)]
            if statuses:
                entry["status_mentions"].append({"line": line_no,
                    "signals": statuses, "excerpt": line.strip()[:220],
                    "interpretation": "TEXT_MENTION_NOT_SCIENTIFIC_VERDICT"})
        if len(entry["links"]) < MAX_LINKS:
            entry["links"].extend(parse_links(path, line, line_no, root)[:MAX_LINKS - len(entry["links"])])
    entry["topics"] = [{"key": key, "first_line": line} for key, line in sorted(refs.items())]
    entry["parse_status"] = "EXTRACTED_HINTS_ONLY"
    return entry


def build_index(root: Path = ROOT, *, max_bytes: int = DEFAULT_MAX_BYTES,
                roots: list[str] | None = None) -> dict:
    if not 1024 <= max_bytes <= 16 * 1024 * 1024:
        raise ValueError("max_bytes must be between 1 KiB and 16 MiB")
    selected = load_roots(root) if roots is None else sorted(roots)
    paths, skipped = collect_paths(root, selected)
    docs = []
    for path in paths:
        raw = (root / path).read_bytes()
        docs.append(extract_metadata(root, path, raw, max_bytes))
    return {"schema": SCHEMA, "repository": REPOSITORY,
            "head_sha": git_sha(root), "roots": selected,
            "max_parse_bytes": max_bytes,
            "documents": docs, "skipped_symlink_paths": skipped,
            "summary": {"documents": len(docs),
                        "hinted_documents": sum(bool(d["topics"]) for d in docs),
                        "by_kind_hint": dict(sorted(Counter(d["filename_hint"] for d in docs).items())),
                        "skipped_unparsed": sum(d["parse_status"] != "EXTRACTED_HINTS_ONLY" for d in docs)},
            "scientific_verdict": "NOT_EVALUATED",
            "warning": "Identity references and status strings are navigation hints only. No scientific validation, independent review or agent action was performed."}


def validate_snapshot(snapshot: dict, *, roots: list[str] | None = None) -> dict[str, dict]:
    if not isinstance(snapshot, dict) or snapshot.get("schema") != SCHEMA or snapshot.get("repository") != REPOSITORY:
        raise ValueError("incompatible/untrusted corpus baseline")
    selected = snapshot.get("roots")
    if not isinstance(selected, list) or not selected or len(selected) != len(set(selected)) or any(
            not safe_relative(x) for x in selected):
        raise ValueError("invalid baseline scope")
    if roots is not None and selected != roots:
        raise ValueError("baseline scope differs from current corpus")
    files = snapshot.get("documents")
    if not isinstance(files, list) or len(files) > MAX_DOCUMENTS:
        raise ValueError("invalid baseline document count")
    lookup = {}
    for entry in files:
        if not isinstance(entry, dict):
            raise ValueError("malformed baseline entry")
        name, sha = entry.get("path"), entry.get("blob_sha")
        if (not safe_relative(name) or not any(name.startswith(r + "/") for r in selected)
                or not isinstance(sha, str) or not SHA40.fullmatch(sha)
                or name in lookup):
            raise ValueError("unsafe/duplicate/bad SHA baseline entry")
        lookup[name] = entry
    return lookup


def diff_index(before: dict, current: dict) -> dict:
    old = validate_snapshot(before, roots=current["roots"])
    new = validate_snapshot(current, roots=current["roots"])
    added = sorted(set(new) - set(old))
    removed = sorted(set(old) - set(new))
    changed = sorted(p for p in set(new) & set(old)
                     if new[p]["blob_sha"] != old[p]["blob_sha"])
    impacted = sorted({ref["key"] for path in [*added, *removed, *changed]
                       for entry in (old.get(path), new.get(path)) if entry is not None
                       for ref in entry.get("topics", [])
                       if isinstance(ref, dict) and isinstance(ref.get("key"), str)})
    return {"schema": "individual-zero-research-corpus-delta/v1",
            "previous_head": before.get("head_sha", "UNKNOWN"),
            "current_head": current["head_sha"], "added": added,
            "removed": removed, "changed": changed,
            "unchanged": len(set(new) & set(old)) - len(changed),
            "topics_for_independent_review": impacted,
            "status": "REVIEW_CHANGED_EVIDENCE" if added or removed or changed else "NO_FILE_CHANGES",
            "scientific_verdict": "NOT_EVALUATED",
            "warning": "Baseline metadata is user-supplied and not authenticated. A file delta never validates or invalidates a scientific finding automatically."}


def related_groups(index: dict, *, topic: str | None = None, limit: int = 30) -> dict:
    if not 0 <= limit <= 500:
        raise ValueError("limit must be 0..500")
    by_topic: dict[str, list[dict]] = defaultdict(list)
    for doc in index["documents"]:
        for item in doc.get("topics", []):
            if not isinstance(item, dict) or not isinstance(item.get("key"), str):
                continue
            by_topic[item["key"]].append(doc)
    if topic is not None and topic not in by_topic:
        return {"status": "NO_EXPLICIT_TOPIC_MATCH", "topic": topic,
                "groups": [], "total_groups": 0, "scientific_verdict": "NOT_EVALUATED"}
    groups = []
    for identifier in sorted(by_topic):
        if topic is not None and topic != identifier:
            continue
        docs = sorted(by_topic[identifier], key=lambda x: x["path"])
        if len(docs) < 2 and topic is None:
            continue
        kinds = sorted(set(x["filename_hint"] for x in docs))
        signals = sorted({s for d in docs for mention in d.get("status_mentions", [])
                          for s in mention.get("signals", [])})
        group = {"topic": identifier, "document_count": len(docs),
                 "documents": [{"path": x["path"], "blob_sha": x["blob_sha"],
                                "kind_hint": x["filename_hint"],
                                "first_topic_line": next((y["first_line"] for y in x["topics"]
                                                          if y["key"] == identifier), None),
                                "status_mentions": x["status_mentions"][:4]} for x in docs[:60]],
                 "total_documents_in_group": len(docs),
                 "kind_hints": kinds,
                 "status_signals": signals,
                 "review_prompts": [], "status": "POSSIBLE_RELATION_NOT_VERIFIED"}
        if "possible_preregistration" in kinds and "possible_results" in kinds:
            group["review_prompts"].append("Compare protocol and result on matching exact SHAs, protocols, populations and endpoints.")
        elif "possible_results" in kinds:
            group["review_prompts"].append("Locate an original preregistration; an absent filename hint is not proof a protocol is missing.")
        if "NO_GO" in signals and ("APPROVED_MENTION" in signals or "PASS_MENTION" in signals):
            group["review_prompts"].append("Mixed negative and approval/test language: inspect contexts and gate scopes; not a verified contradiction.")
            group["status"] = "POSSIBLE_STATUS_SCOPE_DISAGREEMENT_REVIEW"
        if "NOT_EXECUTED" in signals and "PASS_MENTION" in signals:
            group["review_prompts"].append("Test PASS and NOT_EXECUTED may describe different stages; do not infer a study ran.")
        if len(kinds) > 1:
            group["review_prompts"].append("Check whether records describe the same experiment, dated supersession, or only share an issue ID.")
        groups.append(group)
    groups.sort(key=lambda g: (-g["document_count"], g["topic"]))
    return {"schema": "individual-zero-research-corpus-relations/v1",
            "status": "NAVIGATION_REVIEW_QUEUE", "topic": topic,
            "total_groups": len(groups), "groups": groups[:limit],
            "scientific_verdict": "NOT_EVALUATED",
            "warning": "Lexical identifier overlap and status mentions are not evidence of scientific equivalence, outcome or contradiction."}


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Explicit checkout path, for offline tests")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("index", "delta", "review", "report"):
        p = commands.add_parser(name)
        p.add_argument("--max-parse-bytes", type=int, default=DEFAULT_MAX_BYTES)
        p.add_argument("--output", type=Path, help="Optional explicit JSON/Markdown output file")
        if name == "delta":
            p.add_argument("--baseline", type=Path, required=True,
                           help="Previous inventory JSON; never used as scientific authority")
        if name == "review":
            p.add_argument("--topic", help="Exact topic identifier, e.g. study:A1-C or issue:304")
            p.add_argument("--limit", type=int, default=30)
        if name == "report":
            p.add_argument("--top", type=int, default=8)
    return parser.parse_args(argv)


def human_report(index: dict, relations: dict, limit: int) -> str:
    lines = ["# Incremental research corpus navigation", "",
             "Research findings are not independently evaluated. No engine was executed.", "",
             f"Documents: {index['summary']['documents']}; explicit-ID hints: "
             f"{index['summary']['hinted_documents']}; review groups: {relations['total_groups']}.",
             "", "## Candidate relationships to review", ""]
    for item in relations["groups"][:limit]:
        lines.append("- " + item["topic"] + ": " + str(item["document_count"]) +
                     " records, " + item["status"])
        for reason in item["review_prompts"][:2]:
            lines.append("  - " + reason)
    lines += ["", "## Mandatory interpretation", "",
              "A shared ID is not proof of a shared experiment; PASS may mean software tests only.",
              "Original preregistrations, exact code SHAs, datasets and independent reviews must be inspected.", ""]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    try:
        args = parse_args(argv)
        root = args.root.resolve()
        index = build_index(root, max_bytes=args.max_parse_bytes)
        if args.command == "index":
            output = index
        elif args.command == "delta":
            before = json.loads(args.baseline.read_text(encoding="utf-8"))
            output = diff_index(before, index)
        elif args.command == "review":
            output = related_groups(index, topic=args.topic, limit=args.limit)
        else:
            if not 1 <= args.top <= 50:
                raise ValueError("--top must be between 1 and 50")
            output = human_report(index, related_groups(index, limit=args.top), args.top)
        rendered = output if isinstance(output, str) else json.dumps(output, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered, encoding="utf-8")
            print(json.dumps({"status": "WRITTEN_LOCAL_ONLY", "output": str(args.output),
                              "scientific_verdict": "NOT_EVALUATED"}))
        else:
            print(rendered, end="" if rendered.endswith("\n") else "\n")
        return 0
    except (ValueError, OSError, UnicodeError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print("research-corpus: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
