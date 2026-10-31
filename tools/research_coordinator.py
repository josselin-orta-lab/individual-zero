#!/usr/bin/env python3
"""Conservative, read-only global research status and next-intervention advisor.

This program never imports a cognitive engine, launches experiments, writes to
GitHub, verifies scientific evidence, approves a gate or promotes a generation.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone, timedelta
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PROGRAM = "config/research-program.json"
REGISTRY = "config/engine-registry.json"
SCHEMA = "individual-zero-research-program/v1"
GITHUB_SCHEMA = "individual-zero-github-snapshot/v1"
SHA40 = re.compile(r"^[0-9a-fA-F]{40}$")
POSITIVE_GATE_STATES = {"APPROVED", "VERIFIED", "FROZEN", "CONFIRMATORY_GO"}


def read_json(root: Path, path: str) -> dict:
    return json.loads((root / path).read_text(encoding="utf-8"))


def safe_path(path: str) -> bool:
    return (isinstance(path, str) and bool(path) and not path.startswith("/")
            and "\\" not in path
            and not any(p in (".", "..") for p in PurePosixPath(path).parts))


def head_sha(root: Path, supplied: str | None) -> str | None:
    if supplied is not None:
        if not SHA40.fullmatch(supplied):
            raise ValueError("--at-sha needs exactly 40 hexadecimal characters")
        return supplied.lower()
    try:
        result = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                                capture_output=True, text=True, check=True, timeout=3)
        return result.stdout.strip().lower() if SHA40.fullmatch(result.stdout.strip()) else None
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None


def audit(root: Path = ROOT) -> dict:
    errors = []
    try:
        m = read_json(root, PROGRAM)
        registry = read_json(root, REGISTRY)
        i2 = read_json(root, "src/i2/engine.json")
    except (OSError, ValueError, TypeError) as exc:
        return {"status": "FAIL", "errors": [str(exc)], "scientific_verdict": "NOT_EVALUATED"}
    if m.get("schema") != SCHEMA:
        errors.append("research program schema mismatch")
    policy = m.get("policy", {})
    for key in ("no_auto_execution", "no_auto_promotion", "no_auto_scientific_go",
                "unreviewed_evidence_fails_closed", "score_is_heuristic_not_probability"):
        if policy.get(key) is not True:
            errors.append("required policy is missing: " + key)
    if registry.get("active_generation") not in registry.get("generations", {}):
        errors.append("registry active_generation is absent")
    if i2.get("status") == "proposal" and (
            "I2" in registry.get("generations", {}) or i2.get("entrypoints")):
        errors.append("I2 proposal cannot be registered or executable")
    sources = m.get("source_checks", [])
    questions = m.get("questions", [])
    gates = m.get("gates", [])
    tasks = m.get("interventions", [])
    for label, rows in (("source_checks", sources), ("questions", questions),
                        ("gates", gates), ("interventions", tasks)):
        if not isinstance(rows, list) or len(rows) != len(
                set(x.get("id") for x in rows if isinstance(x, dict))):
            errors.append("duplicate/malformed " + label)
    source_ids = {s["id"] for s in sources}
    question_ids = {q["id"] for q in questions}
    gate_ids = {g["id"] for g in gates}
    for s in sources:
        if not safe_path(s.get("path")) or not (root / s["path"]).is_file():
            errors.append("unsafe/missing cited source: " + str(s.get("path")))
        if not s.get("marker") or not s.get("authority"):
            errors.append("source lacks exact marker/authority: " + str(s.get("id")))
    for row in [*questions, *gates]:
        if not set(row.get("source_checks", [])) <= source_ids or not row.get("source_checks"):
            errors.append("unresolved evidence references: " + row["id"])
        if row.get("generation") not in ("I1", "I2"):
            errors.append("unknown generation in " + row["id"])
    for g in gates:
        if not set(g.get("prerequisites", [])) <= gate_ids or g["id"] in g.get("prerequisites", []):
            errors.append("unknown/self gate dependency: " + g["id"])
        if g.get("reported_assessment") in POSITIVE_GATE_STATES:
            errors.append("manifest may not assert human gate approval: " + g["id"])
    dag = {g["id"]:g.get("prerequisites", []) for g in gates}
    def visit(gid: str, stack: set[str], done: set[str]) -> None:
        if gid in stack:
            errors.append("cyclic gate dependencies at " + gid)
            return
        if gid in done:
            return
        for dep in dag.get(gid, []):
            visit(dep, stack | {gid}, done)
        done.add(gid)
    completed = set()
    for gid in dag:
        visit(gid, set(), completed)
    for t in tasks:
        if t.get("gate") not in gate_ids or not set(t.get("requires_gates", [])) <= gate_ids:
            errors.append("unknown gate in intervention " + t["id"])
        if not set(t.get("questions", [])) <= question_ids:
            errors.append("unknown question in intervention " + t["id"])
        if any(t.get(k) not in (1, 2, 3) for k in ("information_gain", "effort", "risk")):
            errors.append("nonordinal ranking fields in " + t["id"])
        if not isinstance(t.get("issue"), int) or not t.get("disconfirming_result"):
            errors.append("missing issue or falsification criterion: " + t["id"])
    return {"status": "FAIL" if errors else "PASS", "errors": sorted(set(errors)),
            "sources": len(sources), "questions": len(questions),
            "gates": len(gates), "interventions": len(tasks),
            "scientific_verdict": "NOT_EVALUATED"}


def source_integrity(root: Path, program: dict) -> dict:
    result = {}
    for s in program["source_checks"]:
        try:
            if not safe_path(s["path"]):
                state = "UNSAFE_SOURCE"
            else:
                content = (root / s["path"]).read_text(encoding="utf-8")
                state = "MARKER_PRESENT" if s["marker"] in content else "SOURCE_CHANGED"
        except OSError:
            state = "SOURCE_MISSING"
        result[s["id"]] = {"path": s["path"], "status": state, "authority": s["authority"]}
    return result


def issue_snapshot(path: Path | None, repo: str, sha: str | None, max_age: int) -> dict:
    empty = {"status": "NOT_SUPPLIED", "issues": {},
             "warning": "Check issue/PR state with live GitHub on the exact SHA."}
    if path is None:
        return empty
    try:
        j = json.loads(path.read_text(encoding="utf-8"))
        if j.get("schema") != GITHUB_SCHEMA or j.get("repository") != repo:
            raise ValueError("snapshot schema/repository mismatch")
        if sha is None or j.get("commit_sha", "").lower() != sha:
            raise ValueError("snapshot does not match a known exact HEAD")
        timestamp = datetime.fromisoformat(j["captured_at"].replace("Z", "+00:00"))
        if timestamp.tzinfo is None:
            raise ValueError("snapshot must include a timezone")
        age = datetime.now(timezone.utc) - timestamp
        if not timedelta(minutes=-5) <= age <= timedelta(hours=max_age):
            raise ValueError("snapshot is stale or future-dated")
        issues = {}
        for item in j.get("issues", []):
            n = item["number"]
            if (not isinstance(n, int) or n in issues or item["state"] not in ("open", "closed")
                    or item["url"] != f"https://github.com/{repo}/issues/{n}"):
                raise ValueError("untrusted or duplicate issue entry")
            issues[n] = item["state"].upper()
        return {"status": "SCHEMA_VALID_NOT_ATTESTED", "issues": issues,
                "warning": "The tool cannot authenticate user-supplied snapshots; verify in GitHub."}
    except (OSError, ValueError, TypeError, KeyError) as exc:
        return {**empty, "status": "INVALID_OR_STALE", "warning": str(exc)}


def research_state(root: Path = ROOT, *, at_sha: str | None = None,
                   snapshot: Path | None = None) -> dict:
    structure = audit(root)
    if structure["status"] != "PASS":
        return {"status": "INVALID_PROGRAM", "audit": structure, "scientific_verdict": "NOT_EVALUATED"}
    m = read_json(root, PROGRAM)
    registry = read_json(root, REGISTRY)
    sha = head_sha(root, at_sha)
    sources = source_integrity(root, m)
    failed = sorted(k for k, x in sources.items() if x["status"] != "MARKER_PRESENT")
    def map_item(item: dict) -> dict:
        missing = [key for key in item["source_checks"] if key in failed]
        return {**item, "source_integrity": "TEXT_MATCH_ONLY" if not missing else "UNVERIFIED",
                "unverified_sources": missing, "gate_approved": False}
    generations = {}
    for gen in ("I0", "I1", "I2"):
        contract_path = root / f"src/{gen.lower()}/engine.json"
        contract = read_json(root, f"src/{gen.lower()}/engine.json") if contract_path.is_file() else {}
        generations[gen] = {"active": registry["active_generation"] == gen,
                            "registry_role": registry.get("generations", {}).get(gen, {}).get("role", "UNREGISTERED"),
                            "contract_status": contract.get("status", "UNVERIFIED"),
                            "entrypoints_declared": bool(contract.get("entrypoints"))}
    github = issue_snapshot(snapshot, m["project"], sha, m["policy"]["github_snapshot_max_age_hours"])
    return {"status": "SOURCE_REVIEW_REQUIRED" if failed else "RECORDED_TEXT_MATCHES",
            "repository": m["project"], "head_sha": sha or "UNKNOWN",
            "active_generation": registry["active_generation"], "generations": generations,
            "questions": [map_item(q) for q in m["questions"]],
            "gates": [map_item(g) for g in m["gates"]],
            "unverified_sources": failed, "source_checks": sources, "github": github,
            "scientific_verdict": "NOT_EVALUATED",
            "warning": "Text matching is not scientific verification. Historical reports and CI never approve a gate."}


def depends_on(candidate: str, ancestor: str, dag: dict, visited: set | None = None) -> bool:
    visited = set() if visited is None else visited
    if candidate in visited:
        return False
    visited.add(candidate)
    return ancestor in dag.get(candidate, []) or any(
        depends_on(node, ancestor, dag, visited) for node in dag.get(candidate, []))


def recommendations(state: dict, program: dict, top: int = 5, generation: str = "all") -> dict:
    if state["status"] == "INVALID_PROGRAM":
        return {"status": "BLOCKED_INVALID_PROGRAM", "recommended_next": None}
    gates = {g["id"]:g for g in state["gates"]}
    questions = {q["id"]:q for q in state["questions"]}
    dag = {g["id"]:g["prerequisites"] for g in state["gates"]}
    proposals = []
    for t in program["interventions"]:
        if generation != "all" and not any(questions[q]["generation"] == generation for q in t["questions"]):
            continue
        blockers = [g for g in t["requires_gates"] if not gates[g]["gate_approved"]]
        stale = set(gates[t["gate"]]["unverified_sources"])
        for qid in t["questions"]:
            stale.update(questions[qid]["unverified_sources"])
        for gid in blockers:
            stale.update(gates[gid]["unverified_sources"])
        issue_state = state["github"]["issues"].get(t["issue"], "UNKNOWN")
        if stale:
            status = "SOURCE_REVIEW_REQUIRED"
        elif blockers:
            status = "BLOCKED_GATE"
        elif issue_state == "CLOSED":
            status = "CLOSED_ISSUE_RECONCILIATION_REQUIRED"
        else:
            status = "REVIEW_CANDIDATE"
        downstream = sum(1 for gid in dag if gid != t["gate"] and depends_on(gid, t["gate"], dag))
        score = (7 * downstream + 4 * t["information_gain"]
                 + (6 if t["priority_class"] == "blocking" else 2)
                 - 2 * t["effort"] - t["risk"])
        proposals.append({"id": t["id"], "title": t["title"], "gate": t["gate"],
                          "questions": t["questions"], "agent_route": t["agent_route"],
                          "issue": t["issue"],
                          "issue_url": f"https://github.com/{state['repository']}/issues/{t['issue']}",
                          "issue_state": issue_state, "stage": status,
                          "blocked_by_gates": blockers, "unverified_sources": sorted(stale),
                          "action": t["action"], "expected_knowledge": t["expected_knowledge"],
                          "disconfirming_result": t["disconfirming_result"],
                          "deliverables": t["deliverables"],
                          "heuristic": {"score": score, "downstream_gates": downstream,
                                        "ordinal_information_gain": t["information_gain"],
                                        "ordinal_effort": t["effort"], "ordinal_risk": t["risk"],
                                        "not_a_scientific_probability": True},
                          "authorization": "RECOMMENDATION_ONLY", "human_review_required": True})
    order = {"REVIEW_CANDIDATE": 0, "CLOSED_ISSUE_RECONCILIATION_REQUIRED": 1,
             "BLOCKED_GATE": 2, "SOURCE_REVIEW_REQUIRED": 3}
    proposals.sort(key=lambda p: (order[p["stage"]], -p["heuristic"]["score"], p["id"]))
    next_step = next((p for p in proposals if p["stage"] == "REVIEW_CANDIDATE"), None)
    return {"status": "PROVISIONAL_RESEARCH_ADVICE", "head_sha": state["head_sha"],
            "active_generation": state["active_generation"],
            "recommended_next": next_step, "proposals": proposals[:top],
            "total_proposals": len(proposals), "external_verification_required": True,
            "scoring": "Ordinal information gain, gate unblock count, effort and risk; not scientific confidence.",
            "scientific_verdict": "NOT_EVALUATED", "execution": "NOT_PERFORMED",
            "promotion": "NOT_AUTHORIZED"}


def graph(program: dict) -> str:
    lines = ["flowchart LR"]
    for g in program["gates"]:
        name = g["id"].replace("-", "_")
        lines.append(f'  {name}["{g["id"]}: {g["reported_assessment"]}"]')
        for dep in g["prerequisites"]:
            lines.append(f'  {dep.replace("-", "_")} --> {name}')
    return "\n".join(lines) + "\n"


def markdown(state: dict, ranked: dict) -> str:
    lines = [f'# Individual Zero: research state at {state["head_sha"]}',
             f'Active generation: {state["active_generation"]}. Scientific verdict: NOT_EVALUATED.',
             f'GitHub issue state: {state["github"]["status"]}. Source status: {state["status"]}.',
             "", "## Research questions"]
    for q in state["questions"]:
        lines.append(f'- {q["id"]}: {q["reported_assessment"]}, {q["source_integrity"]}. {q["question"]} Missing: {q["missing_evidence"]}')
    lines.extend(["", "## Gates (reported only)"])
    for g in state["gates"]:
        lines.append(f'- {g["id"]}: {g["reported_assessment"]}; dependencies {g["prerequisites"]}; human approval NOT_GRANTED')
    lines.extend(["", "## Suggested next intervention"])
    step = ranked["recommended_next"]
    if step:
        lines += [step["title"], step["action"],
                  "Possible falsification: " + step["disconfirming_result"],
                  "This is a provisional review suggestion, not authorization."]
    else:
        lines += ["None; revalidate changed sources or review upstream gate blockers."]
    lines += ["", "## Other interventions"]
    for p in ranked["proposals"]:
        lines.append(f'- {p["title"]}: {p["stage"]}, {p["gate"]}, issue #{p["issue"]}')
    lines += ["", state["warning"], "No engine action, study or scientific promotion performed.", ""]
    return "\n".join(lines)


def main(argv: list[str] | None = None, root: Path = ROOT) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("audit")
    commands.add_parser("graph")
    for name in ("status", "recommend"):
        p = commands.add_parser(name)
        p.add_argument("--at-sha")
        p.add_argument("--github-snapshot", type=Path)
        p.add_argument("--format", choices=("markdown", "json"), default="markdown")
        if name == "recommend":
            p.add_argument("--top", type=int, default=5)
            p.add_argument("--generation", choices=("all", "I1", "I2"), default="all")
    args = parser.parse_args(argv)
    try:
        if args.command == "audit":
            outcome = audit(root)
            if outcome["status"] == "PASS":
                changed = [key for key, value in source_integrity(root, read_json(root, PROGRAM)).items()
                           if value["status"] != "MARKER_PRESENT"]
                if changed:
                    outcome["status"] = "FAIL"
                    outcome["errors"] += ["source marker changed: " + key for key in changed]
            print(json.dumps(outcome, ensure_ascii=False, indent=2))
            return 0 if outcome["status"] == "PASS" else 1
        program = read_json(root, PROGRAM)
        if args.command == "graph":
            print(graph(program), end="")
            return 0
        state = research_state(root, at_sha=args.at_sha, snapshot=args.github_snapshot)
        if state["status"] == "INVALID_PROGRAM":
            print(json.dumps(state, ensure_ascii=False, indent=2))
            return 1
        if args.command == "status":
            if args.format == "json":
                print(json.dumps(state, ensure_ascii=False, indent=2))
            else:
                print(markdown(state, recommendations(state, program, top=0)))
        else:
            if not 1 <= args.top <= 30:
                raise ValueError("--top must be between 1 and 30")
            ranked = recommendations(state, program, top=args.top, generation=args.generation)
            if args.format == "json":
                print(json.dumps(ranked, ensure_ascii=False, indent=2))
            else:
                print(markdown(state, ranked))
        return 2 if state["status"] == "SOURCE_REVIEW_REQUIRED" else 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print("research-coordinator: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
