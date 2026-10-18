#!/usr/bin/env python3
"""Read-only, fail-closed physical trace audit for I1 issue #314.

A WAL event saying "proposal" is not an applied action. We certify a memory
return only when an earlier personal sighting, a later Planning proposal,
Competition crossing, Action Control admission, actual command, physical
world transition and committed step closure match by attempt and ordering.
Nothing is sent to the living individual; no revival, rollback or oracle.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory


def _data(event):
    value = event.get("data", {})
    return value if isinstance(value, dict) else {}


def _position(value):
    if (isinstance(value, dict) and
        type(value.get("x")) is int and type(value.get("y")) is int):
        return (value["x"], value["y"])
    if (isinstance(value, (list, tuple)) and len(value) == 2
        and all(type(n) is int for n in value)):
        return tuple(value)
    return None


def classify_events(events):
    """Passive interpretation of already independently WAL-verified events.

    Can also be unit-tested on synthetic events, which by themselves do
    NOT establish physical or scientific evidence.
    """
    kinds = Counter(e.get("kind") for e in events)
    prior_sightings = []
    proposals = {}
    registered = {}
    crossings = {}
    admissions = {}
    commands = {}
    transitions = {}
    closures = {}
    evaluations = set()
    recalls_with_candidates = 0
    recall_without_candidates = 0
    for idx, row in enumerate(events):
        t = row.get("t_monde")
        attempt = row.get("attempt_ref")
        kind = row.get("kind")
        data = _data(row)
        if type(t) is not int or not isinstance(attempt, str):
            continue
        key = (t, attempt)
        if kind == "i1_entity_place_observed":
            prior_sightings.append((idx, t, data))
        elif kind == "i1_place_memory_recalled":
            if data.get("candidates"):
                recalls_with_candidates += 1
            else:
                recall_without_candidates += 1
        elif kind == "i1_place_memory_option_proposed":
            opt = data.get("option_ref")
            if isinstance(opt, str) and opt.startswith("option:place-memory:"):
                proposals[(key, opt)] = (idx, data)
        elif kind == "i1_place_memory_option_registration":
            opt = data.get("option_ref")
            if isinstance(opt, str):
                k = (key, opt)
                if data.get("registered") is True:
                    registered.setdefault(k, []).append(idx)
        elif kind == "competition_cycle":
            for trace in data.get("traces", ()):
                if not isinstance(trace, dict):
                    continue
                opt = trace.get("option_ref")
                if (isinstance(opt, str)
                    and opt.startswith("option:place-memory:")
                    and trace.get("crossed") is True):
                    crossings.setdefault((key, opt), []).append(idx)
        elif kind == "stage8_option_evaluation":
            opt = data.get("option_ref")
            if isinstance(opt, str):
                evaluations.add((key, opt))
        elif kind == "command_admitted":
            admissions.setdefault(key, []).append((idx, data))
        elif kind == "command_experienced":
            commands.setdefault(key, []).append((idx, row))
        elif kind == "world_transition_experienced":
            transitions.setdefault(key, []).append((idx, row))
        elif kind == "step_closed":
            closures.setdefault(key, []).append((idx, data))

    stages = Counter()
    examples = []
    seen_attempts = set()
    for (attempt, option_ref), (p_idx, proposal) in sorted(
        proposals.items(), key=lambda x: x[1][0]
    ):
        stages["proposed"] += 1
        regs = [i for i in registered.get((attempt, option_ref), ())
                if i > p_idx]
        if not regs:
            stages["proposed_not_registered"] += 1
            continue
        stages["registered"] += 1
        xs = [i for i in crossings.get((attempt, option_ref), ())
              if i > regs[0]]
        if not xs:
            stages["registered_not_crossed"] += 1
            continue
        stages["crossed"] += 1
        ads = [(i, d) for i, d in admissions.get(attempt, ())
               if i > xs[0] and d.get("option_ref") == option_ref
               and d.get("primitive") == "se_deplacer"]
        if not ads:
            stages["crossed_not_admitted"] += 1
            continue
        stages["admitted"] += 1
        # The physically sent command is uniquely identified by its digest,
        # not inferred from the name, the highest score or the route proposal.
        sent = []
        for cidx, cmd in commands.get(attempt, ()):
            if (cidx <= ads[0][0] or cmd.get("emitter") != "action_control"
                or cmd.get("primitive") != "se_deplacer"):
                continue
            matches = [(i, d) for i, d in admissions.get(attempt, ())
                       if i < cidx and d.get("command_hash") ==
                       cmd.get("command_hash")]
            if (matches and matches[-1][1].get("option_ref") == option_ref
                and matches[-1][0] >= ads[0][0]):
                sent.append((cidx, cmd))
        if len(sent) != 1:
            stages["admitted_not_sent"] += 1
            continue
        stages["sent"] += 1
        cidx, command = sent[0]
        physical = [(i, e) for i, e in transitions.get(attempt, ()) if i > cidx]
        close = [(i, d) for i, d in closures.get(attempt, ())
                 if i > cidx and d.get("outcome") in ("normal", "dead")
                 and d.get("applied_command_count") == 1
                 and d.get("world_advance_count") == 1]
        if (len(commands.get(attempt, ())) != 1
            or len(physical) != 1 or len(close) != 1
            or not (cidx < physical[0][0] < close[0][0])):
            stages["sent_without_proven_physical_commit"] += 1
            continue
        stages["physically_applied"] += 1
        after = _position(physical[0][1].get("position_after"))
        next_position = _position(proposal.get("next"))
        target_position = _position(proposal.get("target"))
        if next_position is None or after != next_position:
            stages["applied_unexpected_position"] += 1
            continue
        stages["applied_expected_next_hop"] += 1
        if attempt not in seen_attempts:
            seen_attempts.add(attempt)
            if len(examples) < 12:
                examples.append({
                    "t_monde": attempt[0],
                    "attempt_ref": attempt[1],
                    "option_ref": option_ref,
                    "next_hop": list(after),
                    "reached_target_this_step": after == target_position,
                })
        witnessed = any(
            observation_t < attempt[0]
            and _position(sighting.get("position")) == target_position
            and sighting.get("entity_id") == proposal.get("entity_id")
            and type(sighting.get("first_seen_step")) is int
            and sighting["first_seen_step"] < attempt[0]
            and observation_idx < p_idx
            and sighting.get("source") == "perceptual_capture"
            for observation_idx, observation_t, sighting in prior_sightings
        )
        if witnessed:
            stages["applied_with_prior_personal_sighting"] += 1
            if after == target_position:
                stages["arrived_at_previously_seen_site"] += 1
        else:
            stages["applied_without_verified_prior_sighting"] += 1

    return {
        "schema": "i1-spatial-navigation-audit/v2",
        "remembered_sightings": kinds["i1_entity_place_observed"],
        "recall_events": kinds["i1_place_memory_recalled"],
        "recalls_with_candidates": recalls_with_candidates,
        "recalls_without_candidates": recall_without_candidates,
        "evaluated_memory_options": sum(k in evaluations for k in proposals),
        "stages": {k: stages[k] for k in (
            "proposed", "proposed_not_registered", "registered",
            "registered_not_crossed", "crossed", "crossed_not_admitted",
            "admitted", "admitted_not_sent", "sent",
            "sent_without_proven_physical_commit", "physically_applied",
            "applied_unexpected_position", "applied_expected_next_hop",
            "applied_with_prior_personal_sighting",
            "applied_without_verified_prior_sighting",
            "arrived_at_previously_seen_site",
        )},
        "proven_memory_action_applied": (
            stages["applied_with_prior_personal_sighting"] > 0),
        "proven_return_arrival": (
            stages["arrived_at_previously_seen_site"] > 0),
        "causal_learning_proven": False,
        "survival_improvement_proven": False,
        "examples": examples,
        "interpretation": (
            "Physical application and site arrival require aligned, ordered "
            "Action Control, command, physical transition and committed closure "
            "events plus an earlier personal sighting. This does not establish "
            "learned resource usefulness, causal attribution, or survival gain."
        ),
    }


def audit(path: Path) -> dict:
    if not path.is_file() or path.is_symlink():
        raise ValueError("WAL must be a regular existing file")
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "src"))
    sys.path.insert(0, str(root / "scripts"))
    from build_i1_fork import generate

    # The generation wrapper builds the exact current I1, not an archived I0
    # lab. The reader never instantiates the world or a living individual.
    # Read the immutable evidence image once. Both hash-chain verification
    # and semantic classification MUST consume these exact bytes, avoiding
    # a validate-then-reread race on a WAL being extended by a live birth.
    with path.open("rb") as stream:
        raw_evidence = stream.read()
    with TemporaryDirectory(prefix="i1-spatial-wal-audit-") as folder:
        isolated = Path(folder)
        sealed_wal = isolated / "sealed-evidence.wal"
        sealed_wal.write_bytes(raw_evidence)
        build = isolated / "generated"
        generate(build)
        sys.path.insert(0, str(build))
        try:
            from i1lab.journal import HashChainedJournal
            attestation = HashChainedJournal.audit_durable_wal(
                str(sealed_wal))
        finally:
            sys.path.remove(str(build))

    events = [json.loads(line)["causal_event"]
              for line in raw_evidence.splitlines()]
    if len(events) != attestation["verified_entries"]:
        raise ValueError("verified WAL evidence count mismatch")
    report = classify_events(events)
    report.update({
        "wal": path.name,
        "journal_entries": attestation["verified_entries"],
        "journal_head": attestation["head_hash"],
        "independent_hash_chain_verified": True,
    })
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("wal", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit(args.wal)
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        print(encoded, end="")
    else:
        if args.output.exists():
            raise FileExistsError("audit report must not overwrite evidence")
        args.output.write_text(encoded, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
