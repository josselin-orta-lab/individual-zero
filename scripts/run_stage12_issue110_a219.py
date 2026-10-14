"""A2.19 pre-registered physical trial, with lab-only append-only revision probe."""
from dataclasses import asdict, replace
from pathlib import Path
import argparse
import json
import random
import subprocess

from i0.interfaces import PrimitiveCommand
from i0.modules.perception import SymbolicPerception
from i0.modules.stage12_goal_agency import GoalAgencyService
from lab.determinism import canonical_causal_bytes, sha256_hex
from lab.stage11_reference_fixture import build_stage11_reference_runtime
from lab.world import WorldBody, WorldLayout, Position

SEEDS = tuple(range(101, 109))
CAUSES = ("normal", "confounded")
FOLLOWUPS = ("stay", "passive_displacement")


def capture(world, step):
    return SymbolicPerception().capture(
        local_state=world.capture_local(t_monde=step).as_dict(),
        telemetry=world.telemetry(),
    )


def proposed_reconsideration(*, original, before, after, command, cue_ref):
    """Only authorized first-person evidence; never receives external truth.

    Returns an immutable record, not a replacement for the original judgement.
    """
    if (original.subjective_agency != "self"
            or original.cue_ref is None
            or original.observed_world_step != before.t_monde
            or after.t_monde != before.t_monde + 1
            or command.primitive != "attendre" or bool(command.parameters)
            or not isinstance(cue_ref, str) or not cue_ref.strip()
            or cue_ref == original.cue_ref):
        raise ValueError("invalid or unrelated first-person revision evidence")
    moved = (before.x, before.y) != (after.x, after.y)
    return {
        "original_assessment_ref": original.assessment_ref,
        "original_cue_ref": original.cue_ref,
        "followup_cue_ref": cue_ref,
        "observed_world_step": after.t_monde,
        "original_label_preserved": original.subjective_agency,
        "revision": "reconsider_to_unknown" if moved else "no_revision",
        "current_epistemic_label": "unknown" if moved else "self",
        "reason": ("passive_displacement_witnessed_after_wait"
                   if moved else "no_passive_displacement_witnessed"),
    }


def trial(config, seed, cause, followup):
    rng = random.Random(seed * 991)
    origin = Position(rng.randint(5, 18), rng.randint(5, 18))
    intended = origin.moved("east")
    further = intended.moved("east")
    world = WorldBody(
        config=replace(config, initial_position=origin),
        layout=WorldLayout(water_sources=frozenset({intended})),
    )
    owner = GoalAgencyService()
    before = capture(world, 1)
    move = PrimitiveCommand("se_deplacer", {"direction": "east"})
    assessment = owner.preregister(
        assessment_ref=f"assessment:{seed}:{cause}:{followup}:1",
        intent_ref=f"intent:{seed}:{cause}:{followup}:1",
        life_id=f"lab:{seed}:{cause}:{followup}",
        goal_ref="goal:water", option_ref="option:move:1",
        command_hash=sha256_hex(canonical_causal_bytes(move.as_dict())),
        world_step=1, measure="spatial_distance", command=move,
        capture=before, spatial_target=(intended.x, intended.y, "water"),
    )
    interventions = []
    if cause == "confounded":
        payload = {"primitive": "se_deplacer", "schedule": [True]}
        world.apply_scenario_event("set_action_failure_schedule", payload)
        interventions.append({"step": 1, "operation": "set_action_failure_schedule", "payload": payload})
    transition1 = world.apply(move, t_monde=1)
    actual_after_command = world.position.as_dict()
    if cause == "confounded":
        assert transition1.effects.get("scenario_forced_failure") == "se_deplacer"
        assert actual_after_command == origin.as_dict()
        payload = {"position": intended.as_dict()}
        world.apply_scenario_event("set_position", payload)
        interventions.append({"step": 1, "operation": "set_position", "payload": payload})
    else:
        assert transition1.effects.get("movement") == "moved"
        assert actual_after_command == intended.as_dict()
    middle = capture(world, 2)
    judgment = owner.evaluate(
        capture=middle, world_step=2,
        cue_ref=f"perception:{seed}:{cause}:{followup}:2", paid=True,
    )
    assert judgment is not None and judgment.subjective_agency == "self"
    wait = PrimitiveCommand("attendre", {})
    transition2 = world.apply(wait, t_monde=2)
    assert transition2.effects.get("rest") == "attendre"
    if followup == "passive_displacement":
        payload = {"position": further.as_dict()}
        world.apply_scenario_event("set_position", payload)
        interventions.append({"step": 2, "operation": "set_position", "payload": payload})
    after = capture(world, 3)
    cue_ref = f"perception:{seed}:{cause}:{followup}:3"
    new = proposed_reconsideration(
        original=judgment, before=middle, after=after, command=wait, cue_ref=cue_ref,
    )
    expected = "reconsider_to_unknown" if followup == "passive_displacement" else "no_revision"
    assert new["revision"] == expected
    assert owner.last_judgement == judgment
    assert owner.export_causal_state()["last_judgement"] == judgment.as_dict()
    return {
        "seed": seed, "cause": cause, "followup": followup,
        "captures": [asdict(x) for x in (before, middle, after)],
        "capture_sha256": [
            sha256_hex(canonical_causal_bytes(asdict(x))) for x in (before, middle, after)
        ],
        "commitment": assessment.as_dict(), "original_judgement": judgment.as_dict(),
        "revision_probe": new,
        "transitions": [
            {"step": 1, "sha256": sha256_hex(canonical_causal_bytes(transition1.as_dict())),
             "effects": dict(transition1.effects), "post_command_position": actual_after_command},
            {"step": 2, "sha256": sha256_hex(canonical_causal_bytes(transition2.as_dict())),
             "effects": dict(transition2.effects)},
        ],
        "external_interventions": interventions,
    }


def guard_tests(rows):
    from types import SimpleNamespace
    source = rows[0]
    judgment = SimpleNamespace(**source["original_judgement"])
    # Turn exact stored perception payloads into minimal immutable first-person coordinates.
    b = SimpleNamespace(t_monde=2, x=5, y=5)
    a = SimpleNamespace(t_monde=3, x=5, y=6)
    cmd = PrimitiveCommand("attendre", {})
    good = dict(original=judgment, before=b, after=a, command=cmd, cue_ref="independent:3")
    assert proposed_reconsideration(**good)["current_epistemic_label"] == "unknown"
    for key, wrong in (
        ("cue_ref", judgment.cue_ref),
        ("cue_ref", ""),
        ("after", SimpleNamespace(t_monde=2, x=5, y=6)),
        ("command", PrimitiveCommand("se_deplacer", {"direction": "east"})),
        ("original", SimpleNamespace(**{**source["original_judgement"], "subjective_agency": "world"})),
    ):
        try:
            proposed_reconsideration(**{**good, key: wrong})
        except ValueError:
            pass
        else:
            raise AssertionError(f"revision guard accepted forbidden {key}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output-dir", type=Path, required=True)
    args = p.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=False)
    cfg = build_stage11_reference_runtime().world.config
    rows = []
    for seed in SEEDS:
        for followup in FOLLOWUPS:
            normal = trial(cfg, seed, "normal", followup)
            confounded = trial(cfg, seed, "confounded", followup)
            assert normal["captures"][:2] == confounded["captures"][:2]
            assert normal["captures"] == confounded["captures"]
            assert normal["transitions"][0]["effects"] != confounded["transitions"][0]["effects"]
            assert normal["revision_probe"]["revision"] == confounded["revision_probe"]["revision"]
            for row in (normal, confounded):
                rows.append(row)
                (args.output_dir / f'{row["seed"]}-{row["cause"]}-{row["followup"]}.json').write_text(
                    json.dumps(row, sort_keys=True, indent=2) + "\n"
                )
    guard_tests(rows)
    revised = [x for x in rows if x["revision_probe"]["revision"] == "reconsider_to_unknown"]
    summary = {
        "schema": "stage12-a219-lab-only-passive-revision-v1",
        "code_sha": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "seeds": list(SEEDS), "worlds": len(rows),
        "real_physical_transitions": sum(len(x["transitions"]) for x in rows),
        "initial_confounded_relocations": sum(
            x["cause"] == "confounded" for x in rows
        ),
        "followup_passive_displacements": sum(x["followup"] == "passive_displacement" for x in rows),
        "candidate_revisions": len(revised),
        "revisions_of_initially_correct_self": sum(x["cause"] == "normal" for x in revised),
        "revisions_of_initially_incorrect_self": sum(x["cause"] == "confounded" for x in revised),
        "no_revision_controls": sum(x["revision_probe"]["revision"] == "no_revision" for x in rows),
        "revisions_in_production_cognition": 0, "autonomous_lives": 0,
        "ga06_pairs_from_probe": 0, "runtime_policy_changed": False,
        "stage12": "PARTIAL", "operator_reception": False,
    }
    assert (summary["worlds"], summary["real_physical_transitions"],
            summary["initial_confounded_relocations"], summary["followup_passive_displacements"],
            summary["candidate_revisions"], summary["revisions_of_initially_correct_self"],
            summary["revisions_of_initially_incorrect_self"], summary["no_revision_controls"]) == (
                32, 64, 16, 16, 16, 8, 8, 16,
            )
    (args.output_dir / "a219-summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print("A219_SUMMARY " + json.dumps(summary, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
