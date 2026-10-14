"""A2.21: detached, sealed observation custody versus independently rehashed forgeries.

Only a laboratory observer. Physical intervention labels never feed the candidate.
"""
from copy import deepcopy
from dataclasses import replace
import argparse
import json
from pathlib import Path
import random
import subprocess

from i0.interfaces import PrimitiveCommand
from i0.modules.perception import SymbolicPerception
from i0.modules.stage12_goal_agency import GoalAgencyService
from lab.determinism import canonical_causal_bytes, sha256_hex
from lab.stage11_reference_fixture import build_stage11_reference_runtime
from lab.world import Position, WorldBody, WorldLayout

SEEDS = range(121, 129)
CASES = ("normal", "confounded")
FOLLOWUPS = ("stay", "passive")


def digest(value):
    return sha256_hex(canonical_causal_bytes(value))


def capture(world, step):
    from dataclasses import asdict
    return asdict(SymbolicPerception().capture(
        local_state=world.capture_local(t_monde=step).as_dict(),
        telemetry=world.telemetry()))


def candidate_rebuild(candidate):
    """An adversary can also recalculate the complete internal candidate chain."""
    chain = digest(["a221-candidate-v1", candidate["life_ref"],
                    candidate["original"], candidate["captures"]])
    candidate["events"] = []
    before, after = candidate["captures"][1:]
    moved = (before["x"], before["y"]) != (after["x"], after["y"])
    event = {"prev_hash": chain, "world_step": after["t_monde"],
             "cue_ref": candidate["cue_ref"], "event":
             "reconsider_to_unknown" if moved else "no_revision",
             "from_original": candidate["original"]["assessment_ref"],
             "before_sha": digest(before), "after_sha": digest(after)}
    event["hash"] = digest(event)
    candidate["events"].append(event)
    candidate["head_sha"] = event["hash"]
    return candidate


def internal_audit(candidate):
    if (len(candidate["captures"]) != 3 or len(candidate["events"]) != 1
            or candidate["original"]["subjective_agency"] != "self"):
        return False
    before, after = candidate["captures"][1:]
    if ([c["t_monde"] for c in candidate["captures"]] != [1, 2, 3]
            or not candidate["cue_ref"] or candidate["cue_ref"] == candidate["original"]["cue_ref"]):
        return False
    expected = deepcopy(candidate)
    candidate_rebuild(expected)
    return expected == candidate


def seal_source(*, life_ref, captures, judgement, transition_hashes):
    """Source sealed BEFORE candidate assembly, never passed to its classifier."""
    payload = {"life_ref": life_ref, "captures": deepcopy(captures),
               "original": deepcopy(judgement), "transition_hashes": list(transition_hashes)}
    return {"payload": payload, "seal_sha": digest(payload)}


def independent_source_audit(candidate, seal):
    """Separate keeper checks sealed source instead of trusting candidate hashes."""
    p = seal["payload"]
    return (seal["seal_sha"] == digest(p)
            and candidate["life_ref"] == p["life_ref"]
            and candidate["captures"] == p["captures"]
            and candidate["original"] == p["original"]
            and internal_audit(candidate))


def trial(config, seed, cause, followup):
    from dataclasses import asdict
    rng = random.Random(seed * 991)
    origin = Position(rng.randint(5, 18), rng.randint(5, 18))
    first = origin.moved("east")
    world = WorldBody(config=replace(config, initial_position=origin),
                      layout=WorldLayout(water_sources=frozenset({first})))
    private_id = digest(["a221-opaque", seed, cause, followup])
    life_ref = "life:" + private_id
    owner = GoalAgencyService()
    c1 = capture(world, 1)
    move = PrimitiveCommand("se_deplacer", {"direction": "east"})
    owner.preregister(
        assessment_ref="assessment:" + private_id, intent_ref="intent:" + private_id,
        life_id=life_ref, goal_ref="goal:water", option_ref="option:move",
        command_hash=digest(move.as_dict()), world_step=1, measure="spatial_distance",
        command=move,
        capture=SymbolicPerception().capture(
            local_state=world.capture_local(t_monde=1).as_dict(),
            telemetry=world.telemetry()),
        spatial_target=(first.x, first.y, "water"))
    external = []
    if cause == "confounded":
        p = {"primitive": "se_deplacer", "schedule": [True]}
        world.apply_scenario_event("set_action_failure_schedule", p)
        external.append({"step": 1, "operation": "set_action_failure_schedule", "payload": p})
    t1 = world.apply(move, t_monde=1)
    after_move = world.position.as_dict()
    if cause == "confounded":
        assert t1.effects.get("scenario_forced_failure") == "se_deplacer"
        assert after_move == origin.as_dict()
        p = {"position": first.as_dict()}
        world.apply_scenario_event("set_position", p)
        external.append({"step": 1, "operation": "set_position", "payload": p})
    else:
        assert t1.effects.get("movement") == "moved"
    c2 = capture(world, 2)
    judged = owner.evaluate(
        capture=SymbolicPerception().capture(
            local_state=world.capture_local(t_monde=2).as_dict(),
            telemetry=world.telemetry()),
        world_step=2, cue_ref="perception:" + private_id + ":2", paid=True)
    assert judged and judged.subjective_agency == "self"
    wait = PrimitiveCommand("attendre", {})
    t2 = world.apply(wait, t_monde=2)
    assert t2.effects["rest"] == "attendre"
    if followup == "passive":
        p = {"position": world.position.moved("east").as_dict()}
        world.apply_scenario_event("set_position", p)
        external.append({"step": 2, "operation": "set_position", "payload": p})
    c3 = capture(world, 3)
    captures = [c1, c2, c3]
    original = judged.as_dict()
    transitions = [digest(t1.as_dict()), digest(t2.as_dict())]
    # The sealed source is kept outside the candidate before candidate creation.
    seal = seal_source(life_ref=life_ref, captures=captures,
                       judgement=original, transition_hashes=transitions)
    candidate = candidate_rebuild({"life_ref": life_ref,
                                   "captures": deepcopy(captures),
                                   "original": deepcopy(original),
                                   "cue_ref": "perception:" + private_id + ":3"})
    assert internal_audit(candidate) and independent_source_audit(candidate, seal)
    return {"seed": seed, "cause": cause, "followup": followup, "sealed_source": seal,
            "candidate": candidate, "external_physics":
            {"transitions": transitions, "effects": [dict(t1.effects), dict(t2.effects)],
             "interventions": external}}


def attacks(rows):
    rejected = {key: 0 for key in (
        "full_rehash_capture", "original_rehash", "cross_episode",
        "wrong_life", "truncate", "swap_order")}
    internal_bypass = 0
    total = 0
    for row in rows:
        base, seal = row["candidate"], row["sealed_source"]
        def probe(name, modified):
            nonlocal internal_bypass, total
            total += 1
            if internal_audit(modified):
                internal_bypass += 1
            if independent_source_audit(modified, seal):
                raise AssertionError("detached source accepted " + name)
            rejected[name] += 1
        # A1: perception tampering with complete internal reconstruction.
        forged = deepcopy(base)
        forged["captures"][2]["x"] += 1
        probe("full_rehash_capture", candidate_rebuild(forged))
        # A2: rewrite the previous subjective provenance as well.
        forged = deepcopy(base)
        forged["original"]["assessment_ref"] += ":forged"
        probe("original_rehash", candidate_rebuild(forged))
        # A3: swap between a different followup on same seed and physical cause.
        other = next(x for x in rows if x["seed"] == row["seed"]
                     and x["cause"] == row["cause"]
                     and x["followup"] != row["followup"])
        forged = deepcopy(base)
        forged["captures"][2] = deepcopy(other["candidate"]["captures"][2])
        probe("cross_episode", candidate_rebuild(forged))
        # A4: replay a valid internal record under wrong life id.
        forged = deepcopy(base)
        forged["life_ref"] += ":replayed"
        probe("wrong_life", candidate_rebuild(forged))
        # A5: remove source capture and rehash.
        forged = deepcopy(base)
        forged["captures"].pop()
        # A missing capture is structurally invalid; it cannot be rebuilt as a valid episode.
        probe("truncate", forged)
        # A6: permute observations and rehash.
        forged = deepcopy(base)
        forged["captures"][1], forged["captures"][2] = (
            forged["captures"][2], forged["captures"][1])
        probe("swap_order", candidate_rebuild(forged))
    assert all(v == len(rows) for v in rejected.values())
    assert internal_bypass > 0
    return {"rejected": rejected, "internal_bypasses": internal_bypass,
            "attack_attempts": total}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=False)
    config = build_stage11_reference_runtime().world.config
    rows = []
    for seed in SEEDS:
        for followup in FOLLOWUPS:
            normal = trial(config, seed, "normal", followup)
            confounded = trial(config, seed, "confounded", followup)
            assert normal["candidate"]["captures"] == confounded["candidate"]["captures"]
            assert (normal["candidate"]["events"][0]["event"] ==
                    confounded["candidate"]["events"][0]["event"])
            assert normal["external_physics"]["effects"][0] != confounded["external_physics"]["effects"][0]
            for row in (normal, confounded):
                rows.append(row)
                (args.output_dir / f'{seed}-{followup}-{row["cause"]}.json').write_text(
                    json.dumps(row, sort_keys=True, indent=2) + "\n")
    results = attacks(rows)
    summary = {"schema": "a221-detached-custody-v1",
               "code_sha": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
               "seeds": list(SEEDS), "physical_worlds": len(rows),
               "real_physical_transitions": 2 * len(rows),
               "initial_external_relocations": sum(r["cause"] == "confounded" for r in rows),
               "passive_external_relocations": sum(r["followup"] == "passive" for r in rows),
               "candidate_revisions": sum(
                   r["candidate"]["events"][0]["event"] == "reconsider_to_unknown"
                   for r in rows),
               **results, "cognitive_revisions": 0, "autonomous_lives": 0,
               "ga06_pairs": 0, "stage12": "PARTIAL", "operator_reception": False}
    assert (summary["physical_worlds"], summary["real_physical_transitions"],
            summary["initial_external_relocations"], summary["passive_external_relocations"],
            summary["candidate_revisions"], summary["attack_attempts"]) == (
                32, 64, 16, 16, 16, 192)
    (args.output_dir / "a221-summary.json").write_text(json.dumps(summary, sort_keys=True, indent=2) + "\n")
    print("A221_SUMMARY " + json.dumps(summary, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
