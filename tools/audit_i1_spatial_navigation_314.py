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
    physically_certified = []
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
            physically_certified.append((attempt, option_ref, p_idx, proposal, after))
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
        # This is a passive interpretation of exactly the SAME WAL events
        # already cryptographically sealed by audit(). It makes no motor,
        # learning or hidden-world inference and never weakens the #314 gate.
        "memory_causality_317": classify_memory_causality_317(
            events, proposals, physically_certified,
        ),
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


def certify_multihop_return_317(
    events, physically_certified, capture_before,
):
    """Certify *complete* returns begun beyond perception, including sleep.

    A last-step-only outside-visibility test is insufficient: for a genuine
    multi-hop return the destination naturally becomes visible on the last
    hop. Start with an independently certified, formerly unseen first hop;
    require an explicit first-person Stage11 continuation and a complete,
    uninterrupted chain of physically committed same-entity memory hops.
    Physiological stationary actions (including sleep) may intervene, but
    a competing movement, contradicting observation, missing WAL step, or
    unverifiable motor command breaks the chain. Read-only; no motor oracle.
    """
    from collections import defaultdict

    commands = defaultdict(list)
    transitions = defaultdict(list)
    closures = defaultdict(list)
    admissions = defaultdict(list)
    continuations = defaultdict(list)
    contradictory_sightings = defaultdict(list)
    for idx, row in enumerate(events):
        t, attempt = row.get("t_monde"), row.get("attempt_ref")
        if type(t) is not int or not isinstance(attempt, str):
            continue
        key = (t, attempt)
        kind = row.get("kind")
        if kind == "command_experienced":
            commands[t].append((idx, key, row))
        elif kind == "world_transition_experienced":
            transitions[t].append((idx, key, row))
        elif kind == "step_closed":
            closures[t].append((idx, key, _data(row)))
        elif kind == "command_admitted":
            admissions[t].append((idx, key, _data(row)))
        elif kind == "i1_place_memory_intention_continued":
            continuations[t].append((idx, key, _data(row)))
        elif kind == "i1_entity_place_observed":
            data = _data(row)
            if isinstance(data.get("entity_id"), str):
                contradictory_sightings[t].append((data["entity_id"],
                    _position(data.get("position"))))

    def committed(t):
        # Reject ambiguous attempts, mixed attempt IDs, uncommitted events,
        # non-Action-Control sends, incorrect admission lineage and positions.
        c = commands.get(t, ())
        w = transitions.get(t, ())
        x = closures.get(t, ())
        if len(c) != 1 or len(w) != 1 or len(x) != 1:
            return None
        (ci, ck, ce), (wi, wk, we), (xi, xk, xd) = c[0], w[0], x[0]
        if (ck != wk or wk != xk or not ci < wi < xi
            or ce.get("emitter") != "action_control"
            or we.get("emitter") != "world_and_body"
            or xd.get("outcome") not in ("normal", "dead")
            or xd.get("applied_command_count") != 1
            or xd.get("world_advance_count") != 1):
            return None
        admitted = [(i, d) for i, k, d in admissions.get(t, ())
                    if k == ck and i < ci
                    and d.get("command_hash") == ce.get("command_hash")
                    and d.get("primitive") == ce.get("primitive")]
        after = _position(we.get("position_after"))
        if len(admitted) != 1 or after is None:
            return None
        return ck, ce.get("primitive"), after, ci

    moves = defaultdict(list)
    for attempt, option_ref, p_idx, proposal, after in physically_certified:
        moves[attempt[0]].append(
            (attempt, option_ref, p_idx, proposal, after)
        )

    arrivals = []
    completed_total = 0
    completed_with_sleep = 0
    last_command_step = max(commands.keys(), default=0)
    seen_starts = set()
    for attempt, initial_ref, p_idx, proposed, first_after in physically_certified:
        target = _position(proposed.get("target"))
        first_next = _position(proposed.get("next"))
        initial_capture = capture_before(attempt, p_idx)
        entity_id = proposed.get("entity_id")
        if (initial_capture is None or target is None
            or first_next is None or first_next == target
            or target in initial_capture[1] or first_after != first_next
            or not isinstance(entity_id, str)
            or (attempt[0], initial_ref) in seen_starts):
            continue
        seen_starts.add((attempt[0], initial_ref))
        latest_position = first_after
        previous_ref = initial_ref
        expected_ref = None
        actions = [(attempt[0], initial_ref)]
        sleep_steps = 0
        stationary_steps = 0
        for t in range(attempt[0] + 1, last_command_step + 1):
            step = committed(t)
            if step is None:
                break
            step_attempt, primitive, after, command_index = step
            if any(
                eid == entity_id and observed is not None
                and observed != target
                for eid, observed in contradictory_sightings.get(t, ())
            ):
                break
            if expected_ref is None:
                # The continuation MUST be published in the next world step
                # after the preceding real movement, never conjured later.
                matches = [
                    data for idx, key, data in continuations.get(t, ())
                    if idx < command_index and key == step_attempt
                    and data.get("previous_option_ref") == previous_ref
                    and data.get("source")
                        == "previous_applied_command_and_current_perception"
                    and data.get("forced_motor_selection") is False
                    and _position(data.get("confirmed_position"))
                        == latest_position
                    and isinstance(data.get("next_option_ref"), str)
                    and data["next_option_ref"].startswith("option:place-memory:")
                ]
                if len(matches) != 1:
                    break
                expected_ref = matches[0]["next_option_ref"]
            if after == latest_position:
                if primitive == "se_deplacer":
                    break
                stationary_steps += 1
                sleep_steps += int(primitive == "dormir")
                continue
            if primitive != "se_deplacer":
                break
            matched = [
                (a, opt, idx, proposal, dest)
                for a, opt, idx, proposal, dest in moves.get(t, ())
                if a == step_attempt and opt == expected_ref
                and proposal.get("entity_id") == entity_id
                and _position(proposal.get("target")) == target
                and _position(proposal.get("next")) == after
                and dest == after
                and (lambda capture:
                    capture is not None and capture[0] == latest_position
                )(capture_before(a, idx))
            ]
            if len(matched) != 1 or len(actions) >= 8:
                break
            _, next_ref, _, _, _ = matched[0]
            actions.append((t, next_ref))
            if after == target:
                completed_total += 1
                completed_with_sleep += int(sleep_steps > 0)
                if len(arrivals) < 32:
                    arrivals.append({
                        "start_world_step": attempt[0],
                        "arrival_world_step": t,
                        "entity_id": entity_id,
                        "initially_unseen_target": list(target),
                        "initial_position": list(initial_capture[0]),
                        "physical_memory_hops": len(actions),
                        "stationary_interruption_steps": stationary_steps,
                        "physically_applied_sleep_steps": sleep_steps,
                        "motor_option_refs": [ref for _, ref in actions],
                        "motor_world_steps": [step for step, _ in actions],
                    })
                break
            # A newly observed intermediate physical position must validate a
            # *new* per-hop motor option on the immediate following step.
            previous_ref = next_ref
            expected_ref = None
            latest_position = after
    return {
        "completed_remote_multihop_returns": completed_total,
        "completed_remote_returns_after_sleep": completed_with_sleep,
        "completed_remote_return_examples": arrivals[:12],
    }


def classify_memory_causality_317(events, proposals, physically_certified):
    """Separate remote, locally visible and genuinely learned memory evidence.

    \`events\` must be from the same sealed WAL passed through the original
    #314 audit. This function is also testable on synthetic events, which
    are NOT in themselves evidence of physical behaviour or learned utility.
    """
    from collections import defaultdict

    captures = defaultdict(list)
    assessments = defaultdict(list)
    learned_updates = defaultdict(list)
    crossing_traces = defaultdict(list)
    for idx, row in enumerate(events):
        t = row.get("t_monde")
        attempt = row.get("attempt_ref")
        data = _data(row)
        if type(t) is not int or not isinstance(attempt, str):
            continue
        key = (t, attempt)
        kind = row.get("kind")
        if kind == "perceptual_capture":
            captures[key].append((idx, data))
        elif kind == "stage8_option_evaluation":
            opt = data.get("option_ref")
            if isinstance(opt, str) and opt.startswith("option:place-memory:"):
                assessments[(key, opt)].append((idx, data))
        elif kind == "td_update_published":
            signatures = data.get("updated_signatures", ())
            if isinstance(signatures, list):
                for signature in signatures:
                    if isinstance(signature, str):
                        learned_updates[signature].append(idx)
        elif kind == "competition_cycle":
            for trace in data.get("traces", ()):
                if isinstance(trace, dict):
                    ref = trace.get("option_ref")
                    if isinstance(ref, str) and ref.startswith("option:place-memory:"):
                        crossing_traces[(key, ref)].append((idx, trace))

    def capture_before(attempt, proposal_index):
        prior = [d for idx, d in captures.get(attempt, ())
                 if idx < proposal_index]
        if len(prior) != 1:
            return None
        capture = prior[0]
        if capture.get("capture_t_monde") != attempt[0]:
            return None
        position = _position(capture.get("position"))
        adjacent = capture.get("agency_visible_adjacent")
        if (position is None or not isinstance(adjacent, list)
                or len(adjacent) > 4):
            return None
        coords = {position}
        for cell in adjacent:
            if not isinstance(cell, dict):
                return None
            x, y = cell.get("x"), cell.get("y")
            if type(x) is not int or type(y) is not int:
                return None
            coords.add((x, y))
        return (position, coords)

    def prior_genuine_td(option_ref, attempt, proposal_index):
        evaluated = assessments.get((attempt, option_ref), ())
        for idx, data in evaluated:
            if idx <= proposal_index or data.get("status") != "evaluated":
                continue
            if data.get("learned_value_status") != "learned":
                continue
            if data.get("learned_value") is None:
                continue
            signature = data.get("learning_signature")
            if not isinstance(signature, str):
                continue
            if any(update_idx < idx for update_idx in learned_updates.get(signature, ())):
                return True
        return False

    evaluated_proposals = 0
    remote_candidates = 0
    unseen_candidates = 0
    unseen_ratio = None
    learned_assessments_with_td = 0
    for (attempt, option_ref), (idx, proposal) in proposals.items():
        capture = capture_before(attempt, idx)
        target = _position(proposal.get("target"))
        next_hop = _position(proposal.get("next"))
        if capture is not None and target is not None and next_hop is not None:
            evaluated_proposals += 1
            if target not in capture[1]:
                unseen_candidates += 1
                if target != next_hop:
                    remote_candidates += 1
                for _, trace in crossing_traces.get((attempt, option_ref), ()):
                    ratio = None
                    try:
                        threshold = trace.get("threshold")
                        accumulator = trace.get("accumulator_after")
                        if isinstance(threshold, dict) and set(threshold) == {"$f64"}:
                            threshold = float.fromhex(threshold["$f64"])
                        if isinstance(accumulator, dict) and set(accumulator) == {"$f64"}:
                            accumulator = float.fromhex(accumulator["$f64"])
                        if (type(threshold) in (int, float)
                                and type(accumulator) in (int, float)
                                and threshold > 0 and accumulator >= 0):
                            ratio = accumulator / threshold
                    except (ValueError, TypeError):
                        pass
                    if ratio is not None:
                        unseen_ratio = (ratio if unseen_ratio is None
                                        else max(unseen_ratio, ratio))
        learned_assessments_with_td += int(
            prior_genuine_td(option_ref, attempt, idx)
        )

    confirmed = []
    remote_memory_actions = 0
    arrival_from_outside_capture = 0
    actions_after_td = 0
    for attempt, option_ref, idx, proposal, after in physically_certified:
        capture = capture_before(attempt, idx)
        target = _position(proposal.get("target"))
        next_hop = _position(proposal.get("next"))
        learned = prior_genuine_td(option_ref, attempt, idx)
        if learned:
            actions_after_td += 1
        if capture is not None and target is not None and next_hop is not None:
            unseen = target not in capture[1]
            remote = unseen and next_hop != target
            if remote:
                remote_memory_actions += 1
            if unseen and after == target:
                arrival_from_outside_capture += 1
            if len(confirmed) < 16:
                confirmed.append({
                    "t_monde": attempt[0],
                    "option_ref": option_ref,
                    "entity_id": proposal.get("entity_id"),
                    "origin": list(capture[0]),
                    "target": list(target),
                    "next_hop": list(next_hop),
                    "target_outside_perception": unseen,
                    "unseen_multihop_first_step": remote,
                    "arrived_on_this_step": after == target,
                    "previous_td_used_in_evaluation": learned,
                })

    journeys = certify_multihop_return_317(
        events, physically_certified, capture_before,
    )
    return {
        "schema": "i1-memory-causality-317/v2",
        **journeys,
        "proposals_with_verified_current_capture": evaluated_proposals,
        "proposals_to_unseen_sites": unseen_candidates,
        "proposed_unseen_multihop_options": remote_candidates,
        "max_unseen_accumulation_over_threshold": unseen_ratio,
        "assessments_with_prior_published_td": learned_assessments_with_td,
        "physically_applied_unseen_multihop_first_hops": remote_memory_actions,
        "physically_arrived_from_outside_current_perception": arrival_from_outside_capture,
        "physically_applied_memory_actions_using_prior_td": actions_after_td,
        "examples": confirmed,
        "interpretation": (
            "Remote proposal is not movement. Only prior #314-certified physical "
            "action with an independently preceding first-person capture counts. "
            "Remote *completion* is certified across only personally observed "
            "and physically committed same-entity memory hops, including a "
            "legitimate stationary sleep interruption; it is not a guarantee "
            "of resource utility. TD evaluation shows value re-use only."
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
