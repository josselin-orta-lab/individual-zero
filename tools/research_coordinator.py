#!/usr/bin/env python3
"""Conservative, read-only global research status and next-intervention advisor.

This program never imports a cognitive engine, launches experiments, writes to
GitHub, verifies scientific evidence, approves a gate or promotes a generation.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone, timedelta
import hashlib
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
        if not SHA40.fullmatch(s.get("blob_sha", "")):
            errors.append("missing/invalid pinned Git blob for source: " + str(s.get("id")))
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
    findings = m.get("findings", [])
    if not isinstance(findings, list) or len(findings) != len(set(
            f.get("id") for f in findings if isinstance(f, dict))):
        errors.append("duplicate or malformed findings")
    for finding in findings:
        if finding.get("kind") not in FINDING_KINDS:
            errors.append("invalid finding kind: " + str(finding.get("id")))
        if not set(finding.get("questions", [])) <= question_ids or not finding.get("questions"):
            errors.append("unknown question for finding: " + str(finding.get("id")))
        if not set(finding.get("gates", [])) <= gate_ids:
            errors.append("unknown gate for finding: " + str(finding.get("id")))
        if not set(finding.get("source_checks", [])) <= source_ids or not finding.get("source_checks"):
            errors.append("unknown source for finding: " + str(finding.get("id")))
        if not finding.get("scope_limit") or not finding.get("summary"):
            errors.append("missing scope limit/summary for finding: " + str(finding.get("id")))
        if finding.get("reported_assessment") in POSITIVE_GATE_STATES:
            errors.append("cannot approve gates through findings: " + str(finding.get("id")))
    roots = m.get("catalog_roots", [])
    if not isinstance(roots, list) or len(roots) != len(set(roots)):
        errors.append("duplicate/malformed catalog roots")
    for dirname in roots:
        if not safe_path(dirname) or not (root / dirname).is_dir():
            errors.append("missing or unsafe catalog directory: " + str(dirname))
    route_path = root / "config/agent-context-map.json"
    if route_path.is_file():
        try:
            allowed = read_json(root, "config/agent-context-map.json")["routes"]
            for item in tasks:
                if item.get("agent_route") not in allowed:
                    errors.append("unrecognized agent route in " + item["id"])
        except (OSError, ValueError, TypeError, KeyError):
            errors.append("cannot validate agent routes")
    return {"status": "FAIL" if errors else "PASS", "errors": sorted(set(errors)),
            "sources": len(sources), "questions": len(questions),
            "gates": len(gates), "interventions": len(tasks), "findings": len(findings),
            "scientific_verdict": "NOT_EVALUATED"}


def source_integrity(root: Path, program: dict) -> dict:
    result = {}
    for s in program["source_checks"]:
        actual_blob = None
        try:
            if not safe_path(s["path"]):
                state = "UNSAFE_SOURCE"
            else:
                raw = (root / s["path"]).read_bytes()
                content = raw.decode("utf-8")
                actual_blob = hashlib.sha1(
                    b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()
                if s["marker"] not in content:
                    state = "SOURCE_CHANGED"
                elif actual_blob != s.get("blob_sha"):
                    state = "SOURCE_BLOB_DRIFT"
                else:
                    state = "PIN_MATCH"
        except (OSError, UnicodeError):
            state = "SOURCE_MISSING_OR_INVALID_UTF8"
        result[s["id"]] = {"path": s["path"], "status": state,
                           "pinned_blob_sha": s.get("blob_sha"),
                           "actual_blob_sha": actual_blob,
                           "authority": s["authority"]}
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
    failed = sorted(k for k, x in sources.items() if x["status"] != "PIN_MATCH")
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
            "findings": [map_item(f) for f in m.get("findings", [])],
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
        linked_findings = [f for f in state.get("findings", [])
                           if set(f["questions"]) & set(t["questions"])]
        proposals.append({"id": t["id"], "title": t["title"], "gate": t["gate"],
                          "questions": t["questions"], "agent_route": t["agent_route"],
                          "issue": t["issue"],
                          "issue_url": f"https://github.com/{state['repository']}/issues/{t['issue']}",
                          "issue_state": issue_state, "stage": status,
                          "blocked_by_gates": blockers, "unverified_sources": sorted(stale),
                          "action": t["action"], "expected_knowledge": t["expected_knowledge"],
                          "disconfirming_result": t["disconfirming_result"],
                          "deliverables": t["deliverables"],
                          "recorded_findings_not_verified": [{"id": f["id"], "kind": f["kind"],
                             "assessment": f["reported_assessment"], "scope_limit": f["scope_limit"],
                             "source_integrity": f["source_integrity"]} for f in linked_findings],
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
    lines.extend(["", "## Recorded findings (not independently verified)"])
    for finding in state.get("findings", []):
        lines.append(f'- {finding["id"]}: {finding["kind"]}, {finding["reported_assessment"]}; {finding["scope_limit"]}')
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



# These links describe provenance and planning, never scientific proof.
FINDING_KINDS = {"negative_result", "not_executed", "open_evidence_gap",
                 "software_only", "pending_review"}
CATALOG_HINTS = (("prereg", "possible_preregistration"),
                 ("protocol", "possible_protocol"),
                 ("results", "possible_result"), ("result", "possible_result"),
                 ("audit", "possible_audit"), ("review", "possible_review"),
                 ("status", "possible_status"), ("experiment", "possible_experiment"))


def catalog(root: Path, program: dict, limit: int = 25) -> dict:
    """Inventory files by filename; do not infer scientific results."""
    if not 0 <= limit <= 500:
        raise ValueError("catalog limit must be 0..500")
    referenced = {s["path"] for s in program["source_checks"]}
    counts: dict[str, dict] = {}
    uncited: list[dict] = []
    all_paths: set[str] = set()
    for dirname in program.get("catalog_roots", []):
        if not safe_path(dirname):
            raise ValueError("unsafe catalog directory: " + str(dirname))
        base = (root / dirname).resolve()
        if not base.is_relative_to(root.resolve()) or not base.is_dir():
            raise ValueError("missing or escaping catalog directory: " + dirname)
        docs = []
        for candidate in base.rglob("*.md"):
            if not candidate.is_file() or not candidate.resolve().is_relative_to(root.resolve()):
                continue
            rel = candidate.relative_to(root).as_posix()
            if rel not in all_paths:
                all_paths.add(rel)
                docs.append(rel)
        docs.sort()
        covered = set(docs) & referenced
        counts[dirname] = {"markdown_files": len(docs),
                           "directly_cited_in_program": len(covered),
                           "not_directly_cited": len(docs) - len(covered)}
        for rel in docs:
            if rel not in referenced:
                lower = Path(rel).name.lower()
                hint = next((kind for pattern, kind in CATALOG_HINTS
                             if pattern in lower), "unknown_document_kind")
                uncited.append({"path": rel, "filename_hint": hint,
                                "review": "NOT_REVIEWED_FOR_RESEARCH_GRAPH",
                                "scientific_verdict": "NOT_EVALUATED"})
    uncited.sort(key=lambda x: x["path"])
    return {"status": "NAVIGATION_ONLY", "roots": counts,
            "total_markdown_files": len(all_paths),
            "directly_cited_in_program": len(all_paths & referenced),
            "not_directly_cited": len(all_paths - referenced),
            "sample_unreviewed": uncited[:limit], "returned": min(limit, len(uncited)),
            "scientific_verdict": "NOT_EVALUATED",
            "warning": "Direct-link coverage is not scientific coverage; filename hints are unverified."}


def knowledge_graph(program: dict, state: dict) -> dict:
    """Construct typed evidence/provenance links from curated metadata."""
    nodes: dict[str, dict] = {}
    edges: set[tuple[str, str, str]] = set()

    def node(kind: str, name: str, label: str, **details: object) -> str:
        ident = kind + ":" + name
        if ident not in nodes:
            nodes[ident] = {"id": ident, "kind": kind, "label": label, **details}
        return ident

    def edge(origin: str, dest: str, relation: str) -> None:
        if origin not in nodes or dest not in nodes:
            raise ValueError("invalid research graph reference")
        edges.add((origin, dest, relation))

    for gen in ("I0", "I1", "I2"):
        node("generation", gen, gen, active=state["generations"][gen]["active"])
    for source in program["source_checks"]:
        key = node("source", source["id"], source["id"],
                   path=source["path"], marker=source["marker"],
                   source_integrity=state["source_checks"][source["id"]]["status"],
                   pinned_blob_sha=state["source_checks"][source["id"]]["pinned_blob_sha"],
                   actual_blob_sha=state["source_checks"][source["id"]]["actual_blob_sha"],
                   source_authority=source["authority"])
        file_key = node("artifact", source["path"], source["path"])
        edge(key, file_key, "located_in")
    for question in state["questions"]:
        key = node("question", question["id"], question["question"],
                   reported_assessment=question["reported_assessment"],
                   source_integrity=question["source_integrity"])
        edge("generation:" + question["generation"], key, "research_question")
        for source_id in question["source_checks"]:
            edge(key, "source:" + source_id, "reported_in")
    for gate in state["gates"]:
        key = node("gate", gate["id"], gate["label"],
                   reported_assessment=gate["reported_assessment"],
                   source_integrity=gate["source_integrity"],
                   gate_approved=False)
        edge("generation:" + gate["generation"], key, "research_gate")
        for source_id in gate["source_checks"]:
            edge(key, "source:" + source_id, "reported_in")
        for required in gate["prerequisites"]:
            edge(key, "gate:" + required, "requires_unapproved_gate")
    for finding in state.get("findings", []):
        key = node("finding", finding["id"], finding["summary"],
                   kind_of_finding=finding["kind"],
                   reported_assessment=finding["reported_assessment"],
                   scope_limit=finding["scope_limit"],
                   source_integrity=finding["source_integrity"])
        for question in finding["questions"]:
            edge(key, "question:" + question, "qualifies_question")
        for gate in finding["gates"]:
            edge(key, "gate:" + gate, "qualifies_gate")
        for source_id in finding["source_checks"]:
            edge(key, "source:" + source_id, "reported_in")
    for task in program["interventions"]:
        key = node("intervention", task["id"], task["title"],
                   proposed_not_authorized=True)
        issue_id = str(task["issue"])
        issue = node("issue", issue_id, "#" + issue_id,
                     url="https://github.com/" + state["repository"] + "/issues/" + issue_id)
        owner = node("agent_route", task["agent_route"], task["agent_route"])
        edge(key, issue, "tracked_by")
        edge(key, owner, "initial_code_scope")
        edge(key, "gate:" + task["gate"], "targets")
        for question in task["questions"]:
            edge(key, "question:" + question, "investigates")
        for required in task["requires_gates"]:
            edge(key, "gate:" + required, "requires_unapproved_gate")
    return {"schema": "individual-zero-research-knowledge-graph/v1",
            "head_sha": state["head_sha"], "status": "CURATED_PROVENANCE_ONLY",
            "nodes": [nodes[key] for key in sorted(nodes)],
            "edges": [{"from": a, "to": b, "relation": r}
                      for a, b, r in sorted(edges)],
            "scientific_verdict": "NOT_EVALUATED",
            "warning": "Graph edges are documented associations, not scientific proof or permission."}


def graph_mermaid(knowledge: dict) -> str:
    names = {n["id"]: "n" + str(i) for i, n in enumerate(knowledge["nodes"])}
    lines = ["flowchart LR"]
    for item in knowledge["nodes"]:
        label = re.sub(r'["<>{}\[\]\x60\\\n\r]', "", item["label"])
        label = label[:72].replace("|", "/")
        lines.append('  ' + names[item["id"]] + '["' + item["kind"] + ": " + label + '"]')
    for edge in knowledge["edges"]:
        lines.append("  " + names[edge["from"]] + " -->|" +
                     edge["relation"] + "| " + names[edge["to"]])
    return "\n".join(lines) + "\n"


def explain(knowledge: dict, identifier: str) -> dict:
    """Return a bounded two-hop trace with exact citation anchors."""
    by_id = {n["id"]: n for n in knowledge["nodes"]}
    candidates = [key for key in by_id
                  if key == identifier or key.split(":", 1)[-1] == identifier]
    if len(candidates) != 1:
        raise ValueError("unknown/ambiguous id: " + identifier +
                         "; use a qualified id; matches: " + ", ".join(candidates))
    focus = candidates[0]
    visited = {focus}
    for _ in range(2):
        additional = {endpoint for edge in knowledge["edges"]
                      if edge["from"] in visited or edge["to"] in visited
                      for endpoint in (edge["from"], edge["to"])}
        visited |= additional
    relevant = [e for e in knowledge["edges"]
                if e["from"] in visited and e["to"] in visited]
    sources = [by_id[key] for key in sorted(visited) if key.startswith("source:")]
    changed = [s["id"] for s in sources
               if s["source_integrity"] != "PIN_MATCH"]
    return {"status": "SOURCE_REVIEW_REQUIRED" if changed else "PROVENANCE_LINKS_ONLY",
            "focus": by_id[focus], "nodes": [by_id[key] for key in sorted(visited)],
            "edges": relevant,
            "source_references": [{"id": s["id"], "path": s["path"],
                                   "quoted_marker": s["marker"],
                                   "pinned_blob_sha": s["pinned_blob_sha"],
                                   "actual_blob_sha": s["actual_blob_sha"],
                                   "status": s["source_integrity"],
                                   "authority": s["source_authority"]} for s in sources],
            "changed_or_missing_sources": changed,
            "scientific_verdict": "NOT_EVALUATED", "human_review_required": True,
            "warning": "A matching citation anchor is not observation or proof. Verify source SHA and original evidence."}


def main(argv: list[str] | None = None, root: Path = ROOT) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    audit_parser = commands.add_parser("audit")
    audit_parser.add_argument("--structure-only", action="store_true",
                              help="Validate schema and report source drift without failing on live status updates")
    graph_parser = commands.add_parser("graph", help="Gate dependency or provenance graph")
    graph_parser.add_argument("--mode", choices=("gates", "knowledge"), default="gates")
    graph_parser.add_argument("--format", choices=("mermaid", "json"), default="mermaid")
    trace_parser = commands.add_parser("trace", help="Show the source links of a research node")
    trace_parser.add_argument("--id", required=True)
    trace_parser.add_argument("--at-sha")
    trace_parser.add_argument("--format", choices=("json", "markdown"), default="json")
    catalog_parser = commands.add_parser("catalog", help="Inventory unreviewed research files")
    catalog_parser.add_argument("--limit", type=int, default=25)
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
                sources = source_integrity(root, read_json(root, PROGRAM))
                changed = [key for key, value in sources.items()
                           if value["status"] != "PIN_MATCH"]
                outcome["source_review_required"] = sorted(changed)
                outcome["source_status"] = ("SOURCE_REVIEW_REQUIRED" if changed else "PIN_MATCH")
                outcome["source_integrity"] = sources
                if changed and not args.structure_only:
                    outcome["status"] = "FAIL"
                    outcome["errors"] += ["source pin or marker changed: " + key for key in changed]
            outcome["audit_mode"] = "STRUCTURE_ONLY" if args.structure_only else "STRICT_SOURCES"
            print(json.dumps(outcome, ensure_ascii=False, indent=2))
            return 0 if outcome["status"] == "PASS" else 1
        program = read_json(root, PROGRAM)
        if args.command == "graph":
            if args.mode == "gates":
                diagram = graph(program)
                if args.format == "json":
                    print(json.dumps({"gates_mermaid": diagram,
                                      "scientific_verdict": "NOT_EVALUATED"}))
                else:
                    print(diagram, end="")
            else:
                state = research_state(root)
                if state["status"] == "INVALID_PROGRAM":
                    print(json.dumps(state, ensure_ascii=False))
                    return 1
                knowledge = knowledge_graph(program, state)
                if args.format == "json":
                    print(json.dumps(knowledge, ensure_ascii=False, indent=2))
                else:
                    print(graph_mermaid(knowledge), end="")
            return 0
        if args.command == "catalog":
            print(json.dumps(catalog(root, program, args.limit), ensure_ascii=False, indent=2))
            return 0
        if args.command == "trace":
            state = research_state(root, at_sha=args.at_sha)
            if state["status"] == "INVALID_PROGRAM":
                print(json.dumps(state, ensure_ascii=False))
                return 1
            result = explain(knowledge_graph(program, state), args.id)
            if args.format == "json":
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print("# Research provenance: " + result["focus"]["id"])
                for source in result["source_references"]:
                    print("- " + source["path"] + ": " + source["status"] +
                          " (marker: " + source["quoted_marker"] + ")")
                print(result["warning"])
            return 2 if result["status"] == "SOURCE_REVIEW_REQUIRED" else 0
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
