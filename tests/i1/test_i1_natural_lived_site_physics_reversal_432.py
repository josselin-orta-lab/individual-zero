"""Two non-directed M11 births: can real food consequences reach site evidence?

This is a paired mechanistic experiment, NOT a population study or a GO for
useful autonomous navigation. Only unseen physical berry nutrition differs
before birth. The model cannot read that operator-only fact from the layout.
"""
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from build_i1_fork import generate


class NaturalSitePhysiologyReversal(unittest.TestCase):
    def test_first_person_effect_and_later_spatial_evaluation(self):
        with TemporaryDirectory(prefix="i1-432-paired-") as directory:
            generated = Path(directory) / "generated"
            generate(generated)
            script = r"""
from collections import Counter
from dataclasses import replace
import json
from pathlib import Path
from re import search
from tempfile import TemporaryDirectory

from i1lab.i1_birth import birth_i1_m11
from i1lab.sqlite_life_store import SQLiteLifeLedger
from run_i1_world_preset import load_preset, _birth_parameters

preset, preset_digest = load_preset("dry-valley")
raw_params, local = _birth_parameters(preset)
assert local["current_resources"] == ["berry_a"]
assert not any(key in local for key in (
    "oracle_canary", "berry_effects", "food_gain", "reward",
))
life_id = "i1:432:physiology-matched-site"
TOTAL = 12

def experiment(food_gain, db_path):
    # The one and only intervention is physical berry_a nutrition at birth.
    # Neither the model, perception, goals, TD, UC, sleep nor actions are edited.
    baseline = raw_params["world_config"]
    berry = dict(baseline.berry_effects)
    berry["berry_a"] = replace(berry["berry_a"], food_gain=float(food_gain))
    # Hold physics identity and every other rule fixed. Only the actual
    # nutrition of berry_a changes. The previous probe also changed version,
    # which is an unnecessary second treatment and could confound results.
    physics = replace(baseline, berry_effects=berry)
    assert physics.version == baseline.version
    assert replace(physics, berry_effects=baseline.berry_effects) == baseline, (
        "non-nutritional world physics changed between study arms")
    physics.validate()
    params = dict(
        raw_params, world_config=physics,
        diagnostic_sample_cost_uc=1, module_occupancy_cost_uc=1,
    )
    receipts, bodies = [], []
    with birth_i1_m11(db_path=str(db_path), life_id=life_id, **params) as actor:
        rt = actor._runtime
        first_local = rt.world.capture_local(t_monde=1).as_dict()
        # This is an operator comparison, not an input to the decision owner.
        assert "food_gain" not in json.dumps(first_local)
        for _ in range(TOTAL):
            # M11 publishes a NEW runtime only after the SQLite commit.
            # Never retain the genesis owner across physical generations.
            before = dict(actor._runtime.world.body.as_dict())
            receipt = actor.run_step()
            rt = actor._runtime
            assert receipt.status in ("active", "dead"), receipt
            bodies.append({
                "step": receipt.world_step, "before": before,
                "after": dict(rt.world.body.as_dict()),
                "position": rt.world.position.as_dict(),
            })
            receipts.append({
                "generation": receipt.generation,
                "status": receipt.status,
                "journal_head": receipt.journal_head,
            })
            if receipt.status == "dead":
                break
        events = [dict(e.causal_event) for e in rt.journal.entries_since(0)]
        state = rt.exploration.geographic.export_causal_state()
        td_updates = dict(sorted(rt.q_active.export_causal_state()[
            "update_counts"].items()))
        journal_head = rt.journal.head_hash
    ledger = SQLiteLifeLedger.audit_read_only(
        path=str(db_path), expected_individual_id=life_id)
    assert ledger.generation == len(receipts)
    assert ledger.journal_head == journal_head == receipts[-1]["journal_head"]
    assert not ledger.pending_intent
    assert ledger.status == receipts[-1]["status"]

    applied = {}
    for e in events:
        if e.get("kind") != "command_experienced":
            continue
        step = e["t_monde"]
        assert step not in applied, "two physical commands in one world step"
        applied[step] = e["primitive"]
    assert len(applied) == len(receipts), "missing physical command receipt"
    assert set(applied) == {row["step"] for row in bodies}

    scored = {}
    evaluations = {}
    for e in events:
        d = e.get("data", {})
        if (e.get("kind") == "stage8_option_evaluation"
            and str(d.get("option_ref", "")).startswith("option:lived-site:")):
            key = (e["t_monde"], e["cycle"], d["option_ref"])
            assert key not in evaluations
            evaluations[key] = d
        elif e.get("kind") == "stage11_intrinsic_evaluation" and (
            str(d.get("option_ref", "")).startswith("option:lived-site:")
        ):
            key = (e["t_monde"], e["cycle"], d["option_ref"])
            assert key not in scored
            scored[key] = d
    assert set(scored) == set(evaluations)
    contextual = []
    for (step, cycle, ref), d in sorted(scored.items()):
        if "exploration:lived_site_context_not_causal" not in (
            d.get("intrinsic_producers", ())
        ):
            continue
        sources = [s for s in d.get("signal_ids", ())
                   if str(s).startswith("lived-site:")]
        assert sources, "contextual value without a first-person site witness"
        assert all(
            (match := search(r":observed-t([1-9][0-9]*)$", s))
            and int(match.group(1)) < step for s in sources
        ), "future site observation entered spatial evaluation"
        result = evaluations[(step, cycle, ref)]
        assert result["status"] == "evaluated"
        assert result["evidence"] is not None
        contextual.append({
            "step": step, "cycle": cycle, "ref": ref,
            "evidence": result["evidence"],
            "learned": result["learned_value_status"],
            "simulated": result["simulated_value_status"],
        })
    local_effects = state["lived_site_effects"]
    witnessed = [e for e in events
                 if e.get("kind") == "i1_lived_site_effect_observed"]
    return {
        "food_gain": food_gain,
        "world_physics_version": physics.version,
        "only_food_gain_intervened": True,
        "first_local": first_local,
        "steps": bodies,
        "physical_commands": [applied[t] for t in sorted(applied)],
        "first_manger_step": next(
            (t for t in sorted(applied) if applied[t] == "manger"), None),
        "owner_site_effects": local_effects,
        "witnessed_site_changes": len(witnessed),
        "contextual_values": contextual,
        "spatial_eval_count": len(evaluations),
        "td_update_counts": td_updates,
        "ledger_status": ledger.status,
        "m11_generation": ledger.generation,
        "head_verified": True,
    }

with TemporaryDirectory(prefix="i1-432-m11-") as directory:
    # Two independent, never recovered lives with identical born individual
    # temperament. The physical intervention is hidden from the individual's
    # first-person capture until a genuine ingestion produces its consequence.
    neutral = experiment(0, Path(directory) / "neutral.sqlite")
    nourishing = experiment(10, Path(directory) / "nourishing.sqlite")

assert neutral["first_local"] == nourishing["first_local"], (
    "hidden food assignment leaked into a first-person birth capture")
assert neutral["world_physics_version"] == nourishing["world_physics_version"]
assert neutral["only_food_gain_intervened"] and nourishing[
    "only_food_gain_intervened"]
assert neutral["m11_generation"] and nourishing["m11_generation"]
first = neutral["first_manger_step"]
other = nourishing["first_manger_step"]
if first is not None and other is not None and first == other:
    # No divergence may precede the first real exposure of hidden nutrition.
    assert neutral["physical_commands"][:first] == (
        nourishing["physical_commands"][:first]
    ), "physical controls diverged before the first hidden food outcome"
    before_neutral = neutral["steps"][first - 1]["before"]
    before_nourish = nourishing["steps"][first - 1]["before"]
    assert before_neutral == before_nourish, (
        "matched bodies differ before hidden nutrition was experienced")
    neutral_gain = (neutral["steps"][first - 1]["after"]["food"]
                    - before_neutral["food"])
    nourish_gain = (nourishing["steps"][first - 1]["after"]["food"]
                    - before_nourish["food"])
    # The physical nutrition intervention is authenticated in the post-step
    # body, not presumed from the operator's treatment label alone.
    assert 9.999999 < nourish_gain - neutral_gain < 10.000001
    authenticated_exposure = True
else:
    authenticated_exposure = False

def keyed(contextual):
    return {(e["step"], e["cycle"], e["ref"]):e for e in contextual}

a,b = keyed(neutral["contextual_values"]),keyed(nourishing["contextual_values"])
paired_contexts = []
for key in sorted(a.keys() & b.keys()):
    left,right = a[key],b[key]
    paired_contexts.append({
        "step": key[0], "cycle": key[1],
        "delta_evidence": right["evidence"] - left["evidence"],
        "both_unlearned": left["learned"] == right["learned"] == "unlearned",
        "both_unsimulated": (
            left["simulated"] != "computed" and
            right["simulated"] != "computed"),
    })
future_motor_divergence = (
    None if not authenticated_exposure else
    neutral["physical_commands"][first:] !=
        nourishing["physical_commands"][first:]
)
# A difference in bodily effect is not automatically a causal attribution to
# the action by I1, a preference for better food, or a return to a known site.
report = {
    "preset": "dry-valley",
    "preset_sha256": preset_digest,
    "physical_intervention": "berry_a_food_gain_only",
    "identical_physics_version": True,
    "same_first_person_birth_perception": True,
    "authentic_same_step_ingestion": authenticated_exposure,
    "first_ingestion_step": first if authenticated_exposure else None,
    "neutral": {k:v for k,v in neutral.items()
                if k not in ("first_local", "steps", "contextual_values")},
    "nourishing": {k:v for k,v in nourishing.items()
                  if k not in ("first_local", "steps", "contextual_values")},
    "common_postexperience_context_evaluations": len(paired_contexts),
    "paired_context_deltas": paired_contexts[:12],
    "context_shift_observed": any(
        abs(item["delta_evidence"]) > 1e-12
        for item in paired_contexts if (
            item["both_unlearned"] and item["both_unsimulated"])),
    "postexperience_motor_trajectories_differ": future_motor_divergence,
    "causal_action_attribution": "NOT_ESTABLISHED",
    "spatially_useful_decision": "NOT_ESTABLISHED",
    "scientific_l3": "NOT_ESTABLISHED",
}
print("I1_432_NATURAL_M11_PHYSIOLOGY_REVERSAL "
      + json.dumps(report, sort_keys=True), flush=True)
assert neutral["head_verified"] and nourishing["head_verified"]
print("I1_432_INDEPENDENT_MORTAL_WAL_OK", flush=True)
"""
            env = dict(os.environ, PYTHONPATH=os.pathsep.join((
                str(generated), str(ROOT / "src"), str(ROOT / "tools"))),
                PYTHONDONTWRITEBYTECODE="1")
            outcome = subprocess.run(
                [sys.executable, "-B", "-c", script],
                cwd=ROOT, env=env, text=True, capture_output=True)
            print(outcome.stdout, flush=True)
            if outcome.returncode:
                print(outcome.stderr, flush=True)
            self.assertEqual(outcome.returncode, 0, outcome.stderr)
            self.assertIn("I1_432_INDEPENDENT_MORTAL_WAL_OK", outcome.stdout)


if __name__ == "__main__":
    unittest.main()
