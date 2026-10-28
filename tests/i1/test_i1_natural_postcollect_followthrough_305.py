"""Prospectively bounded natural Oasis B M11 post-collection audit (#305)."""
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from build_i1_fork import generate


class NaturalPostcollection305(unittest.TestCase):
    def test_unforced_oasis_b_steps_19_to_24(self):
        with TemporaryDirectory(prefix="i1-305-followthrough-") as home:
            generated = Path(home) / "generated"
            generate(generated)
            program = r"""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from i1lab.i1_active_runtime import ExperimentalI1Stage12Runtime
from i1.modules.td_values import LinearTDValues
from i1lab.i1_birth import birth_i1_m11
from i1lab.sqlite_life_store import SQLiteLifeLedger
from run_i1_world_preset import load_preset, _birth_parameters

preset, digest = load_preset("oasis")
raw, initial_local = _birth_parameters(preset)
params = dict(raw, diagnostic_sample_cost_uc=1, module_occupancy_cost_uc=1)
IDENTITY = "i1:304:heldout:oasis:b"
original_consider = ExperimentalI1Stage12Runtime._consider_uncertain_affordance
original_read = LinearTDValues.learned_value
observed = []

def observe_consider(owner, *, capture, goal, st_version, cycle, exact):
    reads = []
    def q_read(td_owner, state, signature):
        value = original_read(td_owner, state, signature)
        if td_owner is owner.q_active:
            reads.append({
                "signature": signature, "status": value.status,
                "value": value.value, "evidence": value.evidence,
                "update_count": value.update_count,
            })
        return value
    with patch.object(LinearTDValues, "learned_value", q_read):
        result = original_consider(
            owner, capture=capture, goal=goal, st_version=st_version,
            cycle=cycle, exact=exact)
    if reads:
        assert result is not None
        observed.append({
            "step": capture.t_monde, "cycle": cycle,
            "option_ref": result.option.id, "reads": reads,
        })
    return result

with TemporaryDirectory(prefix="i1-305-m11-") as home:
    path = str(Path(home) / "life.sqlite")
    snapshots = []
    with patch.object(ExperimentalI1Stage12Runtime,
                      "_consider_uncertain_affordance", observe_consider):
        with birth_i1_m11(db_path=path, life_id=IDENTITY, **params) as actor:
            rt = actor._runtime
            assert "i1-living-physical-defaults-v4-metabolic-coupling" in rt.world.config.version
            assert rt.competition._config.noise_sigma == 0
            for _ in range(24):
                before = {
                    "body": dict(rt.world.body.as_dict()),
                    "inventory": dict(rt.world.inventory()),
                }
                receipt = actor.run_step()
                rt = actor._runtime
                assert rt.journal.verify()
                assert receipt.journal_head == rt.journal.head_hash
                snapshots.append({
                    "step": receipt.world_step, "status": receipt.status,
                    "before": before,
                    "after": {
                        "body": dict(rt.world.body.as_dict()),
                        "inventory": dict(rt.world.inventory()),
                    },
                })
                if receipt.status == "dead":
                    break
            events = [dict(e.causal_event) for e in rt.journal.entries_since(0)]
            head = rt.journal.head_hash
    audit = SQLiteLifeLedger.audit_read_only(
        path=path, expected_individual_id=IDENTITY)
    assert audit.generation == len(snapshots)
    assert audit.journal_head == head
    assert audit.status == snapshots[-1]["status"] and not audit.pending_intent
    proposals = [e for e in events
                 if e.get("kind") == "i1_unknown_affordance_proposed"]
    assert len(proposals) == len(observed), "mismatched proposal/read counts"
    joined = []
    for e, r in zip(proposals, observed):
        d = e["data"]
        assert (e["t_monde"], e["cycle"], d["option_ref"]) == (
            r["step"], r["cycle"], r["option_ref"])
        reads = r["reads"]
        assert len(reads) == d["candidate_count"]
        assert [x["signature"].split(":")[2] for x in reads] == d["candidate_primitives"]
        cmd = d["command"]
        suffix = ":".join(f"{k}={cmd['parameters'][k]}"
                          for k in sorted(cmd["parameters"])) or "here"
        winner = "i1:affordance:" + cmd["primitive"] + ":" + suffix
        win = [x for x in reads if x["signature"] == winner]
        assert len(win) == 1
        assert win[0]["status"] == d["learned_value_status"]
        assert win[0]["value"] == d["learned_value"]
        joined.append({
            "step": r["step"], "cycle": r["cycle"],
            "winner": winner, "candidate_count": len(reads),
            "reads": reads,
        })

    applied = {e["t_monde"]: {"primitive": e["primitive"],
                "parameters": e["parameters"]}
               for e in events if e.get("kind") == "command_experienced"}
    assert all(s in applied for s in range(1, len(snapshots)+1))
    assert applied[11]["primitive"] == "manger"
    assert all(applied[t]["primitive"] == "dormir" for t in range(12, 18))
    assert applied[18] == {
        "primitive": "collecter", "parameters": {"target": "berry_a"}}
    assert snapshots[17]["after"]["inventory"]["berry_a"] == 1

    followthrough = [r for r in joined if r["step"] >= 19]
    multiple = [r for r in followthrough if r["candidate_count"] >= 2]
    learned = [r for r in multiple if any(
        q["status"] == "learned" for q in r["reads"])]
    admissions = [
        {"step": e["t_monde"], "cycle": e.get("cycle"),
         "primitive": e["data"].get("primitive"),
         "option_ref": e["data"].get("option_ref")}
        for e in events if e.get("kind") == "command_admitted"
        and e["t_monde"] >= 19]
    stage8 = [
        {"step": e["t_monde"], "cycle": e.get("cycle"),
         "signature": e["data"]["learning_signature"],
         "status": e["data"]["status"],
         "learned": e["data"]["learned_value_status"],
         "q": e["data"]["learned_value"], "evidence": e["data"]["evidence"]}
        for e in events if e.get("kind") == "stage8_option_evaluation"
        and e["t_monde"] >= 19]
    charge = [
        {"step": e["t_monde"], "cycle": e.get("cycle"),
         "operation": e["data"].get("operation"),
         "module": e["data"].get("module"),
         "accepted": e["data"].get("accepted")}
        for e in events if e.get("kind") == "compute_charge"
        and e["t_monde"] >= 19]
    output = {
        "source": "new_pre_registered_unforced_oasis_b_m11_24_steps",
        "prefix_provenance_verified": True,
        "audit_verified": True,
        "m11_generation": audit.generation, "status": audit.status,
        "steps": len(snapshots), "first_postcollection_inventory": snapshots[17]["after"]["inventory"],
        "followthrough": followthrough, "multicandidate": multiple,
        "multi_with_learned_q": len(learned),
        "verdict": (
            "NO_POSTCOLLECT_UPSTREAM_PROPOSAL" if not followthrough else
            "ONLY_SINGLE_CANDIDATE" if not multiple else
            "MULTICANDIDATE_WITH_LEARNED_Q" if learned else
            "MULTICANDIDATE_ALL_Q_UNLEARNED"),
        "applied": [{"step": t, **v} for t, v in sorted(applied.items())
                    if t >= 19],
        "admissions": admissions,
        "stage8": stage8, "charges": charge,
        "physical": [r for r in snapshots if r["step"] >= 19],
        "causal_upstream_effect": "NOT_ESTABLISHED",
        "instrumental_benefit": "NOT_ESTABLISHED",
    }
    print("I1_305_POSTCOLLECT_FOLLOWTHROUGH=" + json.dumps(output, sort_keys=True))
"""
            env = dict(os.environ,
                       PYTHONPATH=os.pathsep.join((str(generated), str(ROOT / "src"),
                                                   str(ROOT / "tools"))),
                       PYTHONDONTWRITEBYTECODE="1")
            proc = subprocess.run([sys.executable, "-B", "-c", program], cwd=ROOT,
                                  env=env, capture_output=True, text=True, timeout=480)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertIn("I1_305_POSTCOLLECT_FOLLOWTHROUGH=", proc.stdout)
            print(proc.stdout, flush=True)


if __name__ == "__main__":
    unittest.main()
