"""A2.30-G: independent offline graph witness for original A2.30-E archives.

Only reads already sealed artifacts from original GH Actions run #38715999434.
Neither executes a new life nor imports the I0 planning/simulation machinery.
A missing edge in this graph is not evidence of physical impossibility.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict, deque
from hashlib import sha256
import json
from pathlib import Path
import subprocess

EXPECTED_SHA = "2be8008d51ad0d8a02d4795739a828acfba72aac"
EXPECTED_PROFILES = ("restored", "sustained", "episodic", "marginal")
EXPECTED_STEPS = 192
EXPECTED_SEARCHES = 141
EXPECTED_INCOMPLETE = 121
EXPECTED_EDGES = 926
EXPECTED_UNAVAILABLE = 880
RUN_ID = 38715999434

EXHAUSTIVE = {
    "incomplete_model", "not_found_within_horizon", "partial_progress",
}


def command_key(command: dict) -> str:
    return json.dumps(command, sort_keys=True, separators=(",", ":"))


def independent_known_graph_witness(search: dict) -> dict:
    """Only certify properties of exactly the edges actually witnessed.

    For full-exhaustion searches, construct independently the complete
    reachable *known-edge* graph inside the announced depth. This cannot
    assess the goal predicate, because A2.30-E stored successor hashes but
    not successor body values or predicates.
    """
    status = search["status"]
    depth_limit = search["depth_limit"]
    root = search["initial_state_sha256"]
    if type(depth_limit) is not int or depth_limit < 1:
        raise ValueError("missing or invalid search depth")
    nodes = search["candidate_states"]
    edges = search["edges"]
    if status not in EXHAUSTIVE | {"plan_found"}:
        raise ValueError("unregistered search status: " + str(status))
    if not isinstance(root, str) or len(root) != 64:
        raise ValueError("malformed root state digest")
    by_node: dict[str, dict] = {}
    for node in nodes:
        h = node["state_sha256"]
        if h in by_node:
            raise ValueError("duplicate expanded search state")
        if type(node["depth"]) is not int or not 0 <= node["depth"] < depth_limit:
            raise ValueError("expanded state outside search depth")
        by_node[h] = node
    by_parent: dict[str, list] = defaultdict(list)
    for edge in edges:
        parent = edge["state_sha256"]
        if parent not in by_node:
            raise ValueError("prediction from non-expanded state")
        if edge["parent_depth"] != by_node[parent]["depth"]:
            raise ValueError("wrong parent depth")
        if type(edge["complete"]) is not bool:
            raise ValueError("invalid edge completeness")
        if edge["complete"]:
            h = edge["next_state_sha256"]
            if not isinstance(h, str) or len(h) != 64:
                raise ValueError("known prediction missing successor hash")
            if edge["reason"] is not None:
                raise ValueError("complete edge has failure reason")
        elif edge["next_state_sha256"] is not None:
            raise ValueError("unknown edge invented a successor state")
        by_parent[parent].append(edge)
    if len(nodes) != search["expanded_states"]:
        raise ValueError("expanded-state counter diverges from graph")
    if sum(not e["complete"] for e in edges) != search["unavailable_edges"]:
        raise ValueError("unavailable-edge counter diverges from graph")

    # Independent BFS. Known destinations are NOT inferred from the Oracle.
    queue = deque([(root, 0)])
    seen = {root: 0}
    expected_expansion = {}
    while queue:
        state, depth = queue.popleft()
        if depth >= depth_limit:
            continue
        expected_expansion[state] = depth
        for edge in by_parent.get(state, []):
            if not edge["complete"]:
                continue
            successor = edge["next_state_sha256"]
            if successor not in seen:
                seen[successor] = depth + 1
                queue.append((successor, depth + 1))

    if status in EXHAUSTIVE:
        if expected_expansion != {
            k: node["depth"] for k, node in by_node.items()
        }:
            missing = sorted(set(expected_expansion) - set(by_node))
            extra = sorted(set(by_node) - set(expected_expansion))
            raise ValueError(
                f"independent BFS disagrees with search expansions "
                f"(unexpanded={len(missing)}, unreachable={len(extra)})"
            )
        for h, node in by_node.items():
            generated = Counter(
                command_key(c) for c in node["candidate_commands"]
            )
            actually_queried = Counter(
                command_key(e["command"]) for e in by_parent[h]
            )
            if generated != actually_queried:
                raise ValueError("exhausted search omitted a candidate action")
    else:
        if set(by_node) - set(expected_expansion):
            raise ValueError("plan-found search expanded unreachable state")
        # Plan_found may terminate part way through one node's action list;
        # missing later calls are censorship by success, not pruning.
        for h in by_node:
            generated = [
                command_key(c) for c in by_node[h]["candidate_commands"]
            ]
            queried = [
                command_key(e["command"]) for e in by_parent[h]
            ]
            if generated[:len(queried)] != queried:
                raise ValueError("plan-found search skipped action order")

    root_edges = by_parent.get(root, [])
    initial_actions = by_node[root]["candidate_commands"] if root in by_node else []
    first_known = sum(e["complete"] for e in root_edges)
    first_missing = sum(not e["complete"] for e in root_edges)
    if status in EXHAUSTIVE and not root_edges:
        raise ValueError("exhaustive search never evaluated initial actions")
    unknowns = [e for e in edges if not e["complete"]]
    missing_min_depth = (
        min(e["parent_depth"] for e in unknowns) if unknowns else None
    )
    capped_frontier = {
        h for h, depth in seen.items()
        if depth >= depth_limit and h not in by_node
    }
    fully_closed = (
        status in EXHAUSTIVE
        and not unknowns
        and not capped_frontier
        and set(seen) == set(by_node)
    )
    result_commands = search.get("commands", [])
    # Check predicted plan steps are actually known from root to endpoint.
    # A skipped action must never silently be certified as a valid prefix.
    frontier = {root}
    for action in result_commands:
        key = command_key(action)
        new_frontier = {
            e["next_state_sha256"]
            for state in frontier
            for e in by_parent.get(state, [])
            if e["complete"] and command_key(e["command"]) == key
        }
        if not new_frontier:
            raise ValueError("planner returned a path using an unknown edge")
        frontier = new_frontier

    return {
        "status": status,
        "depth_limit": depth_limit,
        "model_known_edges": sum(e["complete"] for e in edges),
        "model_unknown_edges": len(unknowns),
        "first_unknown_parent_depth": missing_min_depth,
        "root_candidate_actions": len(initial_actions),
        "root_known_edges": first_known,
        "root_unknown_edges": first_missing,
        "zero_known_first_step": (
            status == "incomplete_model" and len(initial_actions) > 0
            and first_known == 0 and first_missing == len(initial_actions)
        ),
        "some_known_first_step": (
            status == "incomplete_model" and first_known > 0
        ),
        "root_unknown_food_actions": sum(
            not e["complete"] and
            e["command"].get("primitive") in {"collecter", "manger"}
            for e in root_edges
        ),
        "root_unknown_movement_actions": sum(
            not e["complete"] and
            e["command"].get("primitive") == "se_deplacer"
            for e in root_edges
        ),
        "known_reachable_state_hashes": len(seen),
        "unexpanded_at_depth_cap": len(capped_frontier),
        "independent_bfs_expansions_match": True,
        "fully_closed_finite_known_graph": fully_closed,
        "goal_predicate_independently_checked": False,
        "real_world_impossibility_proven": False,
    }


def validate_archives(root: Path) -> tuple[dict, list]:
    summaries = list(root.rglob("a230e-summary.json"))
    if len(summaries) != 1:
        raise ValueError(
            f"expected one original A2.30-E summary; got {len(summaries)}"
        )
    base = summaries[0].parent
    summary = json.loads(summaries[0].read_text())
    if summary.get("schema") != "stage12-a230e-prospective-edge-census-v1":
        raise ValueError("unrecognized source cohort schema")
    if summary.get("code_sha") != EXPECTED_SHA:
        raise ValueError("original source SHA mismatch")
    if (
        summary.get("lives") != 8
        or summary.get("physical_steps") != EXPECTED_STEPS
        or summary.get("searches") != EXPECTED_SEARCHES
        or summary.get("incomplete_searches") != EXPECTED_INCOMPLETE
        or summary.get("actual_edges") != EXPECTED_EDGES
        or summary.get("missing_exact_inputs") != EXPECTED_UNAVAILABLE
        or summary.get("deterministic_replay_byte_identical") is not True
    ):
        raise ValueError("original source report mismatch")

    from lab.independent_journal_audit import audit_export_bytes

    datasets = []
    seen = set()
    for profile in EXPECTED_PROFILES:
        for blocked in (False, True):
            label = profile + ("-a2" if blocked else "-free")
            folder = base / label
            if not folder.is_dir():
                raise ValueError("missing cohort: " + label)
            detail = json.loads(
                (folder / "a230e-real-search-edges.json").read_text()
            )
            life = json.loads((folder / "result.json").read_text())
            source = (folder / "canonical.jsonl").read_bytes()
            expected_identity = (
                "i0:stage12:b:a230e:" + profile +
                (":A2" if blocked else ":free")
            )
            if life["birth_id"] != expected_identity:
                raise ValueError("wrong scientific birth identity")
            if detail["birth_id"] != expected_identity or expected_identity in seen:
                raise ValueError("duplicate or wrong birth in edge archive")
            seen.add(expected_identity)
            if sha256(source).hexdigest() != detail["journal_sha256"]:
                raise ValueError("edge archive does not match canonical journal")
            if sha256(source).hexdigest() != life["journal_sha256"]:
                raise ValueError("life journal does not match canonical archive")
            proof = audit_export_bytes(
                source, expected_head=life["journal_head"],
                expected_count=life["journal_count"],
            )
            if proof.world_steps_closed != life["world_steps"]:
                raise ValueError("audited world steps disagree with life")
            if life["world_steps"] != 24:
                raise ValueError("incomplete original A2.30-E life")
            if len(detail["searches"]) != detail["counts"]["searches"]:
                raise ValueError("search detail length mismatch")
            if len(detail["prebirth_training"]) != 4:
                raise ValueError("unexpected original prebirth corpus")
            datasets.append((label, detail, life))
    if len(seen) != 8:
        raise ValueError("source scientific births incomplete")
    return summary, datasets


def execute(source_dir: Path, output_dir: Path) -> dict:
    source_summary, datasets = validate_archives(source_dir)
    output_dir.mkdir(parents=True, exist_ok=False)
    rows = []
    for label, detail, life in datasets:
        witnesses = [
            independent_known_graph_witness(s)
            for s in detail["searches"]
        ]
        distribution = Counter(s["status"] for s in witnesses)
        first_unknown_depths = Counter(
            str(s["first_unknown_parent_depth"])
            for s in witnesses
            if s["first_unknown_parent_depth"] is not None
        )
        row = {
            "life": label,
            "birth_id": life["birth_id"],
            "journal_head": life["journal_head"],
            "physical_steps_previously_executed": life["world_steps"],
            "searches_audited": len(witnesses),
            "statuses": dict(distribution),
            "incomplete_searches": distribution["incomplete_model"],
            "zero_known_first_step": sum(
                x["zero_known_first_step"] for x in witnesses
            ),
            "some_known_first_step": sum(
                x["some_known_first_step"] for x in witnesses
            ),
            "root_unknown_food_actions": sum(
                x["root_unknown_food_actions"] for x in witnesses
            ),
            "root_unknown_movement_actions": sum(
                x["root_unknown_movement_actions"] for x in witnesses
            ),
            "first_unknown_depths": dict(first_unknown_depths),
            "known_closed_graphs": sum(
                x["fully_closed_finite_known_graph"] for x in witnesses
            ),
            "depth_boundary_states": sum(
                x["unexpanded_at_depth_cap"] for x in witnesses
            ),
            "bfs_mismatches": 0,
            "goal_predicate_independently_checked": False,
        }
        (output_dir / (label + "-graph-witness.json")).write_text(
            json.dumps({
                "schema": "stage12-a230g-graph-witness-v1",
                "source_code_sha": EXPECTED_SHA,
                "life": row,
                "search_witnesses": witnesses,
            }, sort_keys=True, indent=2) + "\n"
        )
        rows.append(row)
        print("A230G_LIFE " + json.dumps(row, sort_keys=True), flush=True)

    result = {
        "schema": "stage12-a230g-offline-witness-v1",
        "source_action_run": RUN_ID,
        "source_code_sha": EXPECTED_SHA,
        "analysis_code_sha": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True
        ).strip(),
        "independent_births_new": 0,
        "physical_steps_new": 0,
        "original_births_reanalysed": len(rows),
        "original_physical_steps_reanalysed": sum(
            x["physical_steps_previously_executed"] for x in rows
        ),
        "searches_witnessed": sum(x["searches_audited"] for x in rows),
        "incomplete_searches": sum(x["incomplete_searches"] for x in rows),
        "incomplete_zero_known_first_step": sum(
            x["zero_known_first_step"] for x in rows
        ),
        "incomplete_some_known_first_step": sum(
            x["some_known_first_step"] for x in rows
        ),
        "unavailable_food_action_at_root": sum(
            x["root_unknown_food_actions"] for x in rows
        ),
        "unavailable_movement_action_at_root": sum(
            x["root_unknown_movement_actions"] for x in rows
        ),
        "known_closed_graphs": sum(x["known_closed_graphs"] for x in rows),
        "depth_boundary_states": sum(x["depth_boundary_states"] for x in rows),
        "bfs_mismatches": 0,
        "goal_predicate_independently_checked": False,
        "physical_impossibility_established": False,
        "model_change": False,
        "stage12": "PARTIAL",
        "rows": rows,
    }
    if (
        result["original_births_reanalysed"] != 8
        or result["original_physical_steps_reanalysed"] != EXPECTED_STEPS
        or result["searches_witnessed"] != EXPECTED_SEARCHES
        or result["incomplete_searches"] != EXPECTED_INCOMPLETE
        or result["incomplete_zero_known_first_step"]
        + result["incomplete_some_known_first_step"] != EXPECTED_INCOMPLETE
    ):
        raise ValueError("incomplete or unclassified source search audit")
    (output_dir / "a230g-summary.json").write_text(
        json.dumps(result, sort_keys=True, indent=2) + "\n"
    )
    print("A230G_SUMMARY " + json.dumps({
        k: v for k, v in result.items() if k != "rows"
    }, sort_keys=True), flush=True)
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-dir", required=True, type=Path)
    ap.add_argument("--output-dir", required=True, type=Path)
    args = ap.parse_args()
    execute(args.source_dir, args.output_dir)


if __name__ == "__main__":
    main()
