"""#564: natural M11 Memory recall work versus charged UC, without intervention.

Two independently born, identically configured mortal lives are compared at
EVERY committed generation boundary. The observation arm adds only a class
method wrapper recording work volume and elapsed time in the operator process.
It does not alter Memory state, contribute evidence, or pay/grant UC.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[2]

PROGRAM = r'''
import json
from contextlib import nullcontext
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter_ns
from unittest.mock import patch
from run_i1_world_preset import load_preset, _birth_parameters
from i1.modules.memory import EpisodicMemory
from i1lab.i1_birth import birth_i1_m11, recover_i1_m11
from i1lab.i1_natural_runtime import I1Runtime
from i1lab.sqlite_life_store import SQLiteLifeLedger

original = EpisodicMemory.spontaneous_contribution

def experiment(preset_name, max_steps):
    preset, _ = load_preset(preset_name)
    params, _ = _birth_parameters(preset)
    identity = "i1:564:natural-recall-work:" + preset_name
    with TemporaryDirectory() as folder:
        def arm(label, instrument):
            path = str(Path(folder) / (label + ".sqlite"))
            work = []
            def observed(self, *, st, t_monde, cycle):
                # Passive read of the authentic Memory owner, immediately
                # before the unchanged scoring call. No episode is injected.
                n = self.episode_count
                start = perf_counter_ns()
                contribution = original(
                    self, st=st, t_monde=t_monde, cycle=cycle)
                work.append({
                    "world_step": t_monde, "cycle": cycle,
                    "candidate_episodes": n,
                    "elapsed_ns": perf_counter_ns() - start,
                    "published": contribution is not None,
                })
                return contribution

            def fresh():
                return I1Runtime(
                    birth_life_id=identity, autonomous_mortal=True,
                    m11_sqlite_custody=True, wal_path=None,
                    diagnostic_sample_cost_uc=1,
                    module_occupancy_cost_uc=1, **params)

            context = (patch.object(EpisodicMemory, "spontaneous_contribution",
                                    observed) if instrument else nullcontext())
            with context:
                with birth_i1_m11(db_path=path, life_id=identity,
                                      **params) as life:
                    steps = []
                    last_status = None
                    for _ in range(max_steps):
                        before_count = life._runtime.journal.entry_count
                        result = life.run_step()
                        committed = life._runtime
                        assert result.journal_head == committed.journal.head_hash
                        assert committed.journal.verify()
                        charges = []
                        recall_receipts = 0
                        for entry in committed.journal.entries_since(before_count):
                            event = entry.causal_event
                            if event.get("kind") == "compute_charge":
                                charges.append(dict(event["data"]))
                            if event.get("kind") == "memory_recall_proposed":
                                recall_receipts += 1
                        assert all(type(item["requested_uc"]) is int
                                   and type(item["accepted"]) is bool
                                   for item in charges)
                        steps.append({
                            "status": result.status,
                            "head": committed.journal.head_hash,
                            "memory": committed.memory.export_causal_state(),
                            "episode_count": committed.memory.episode_count,
                            "recall_proposals": recall_receipts,
                            "charges": charges,
                            "charged_uc": sum(item["requested_uc"]
                                              for item in charges
                                              if item["accepted"]),
                        })
                        last_status = result.status
                        if result.status == "dead":
                            break
                        assert result.status == "active"
                    assert steps
                    final_head = committed.journal.head_hash
                    final_memory = committed.memory.export_causal_state()
                custody = SQLiteLifeLedger.audit_read_only(
                    path=path, expected_individual_id=identity)
                assert custody.journal_head == final_head
                assert custody.may_recover == (last_status == "active")
                if last_status == "active":
                    with recover_i1_m11(
                        db_path=path, life_id=identity,
                        runtime_factory=fresh,
                    ) as cold:
                        assert cold._runtime.journal.head_hash == final_head
                        assert cold._runtime.memory.export_causal_state() == final_memory
                return steps, work

        reference, no_work = arm("reference", False)
        observed_steps, work = arm("passive-observer", True)
        assert reference == observed_steps, (
            "M11 causal/UC/Memory drift under passive recall instrumentation",
            preset_name,
        )
        assert not no_work
        assert all(item["candidate_episodes"] >= 0 for item in work)
        assert all(item["world_step"] >= 1 and item["cycle"] >= 1
                   for item in work)
        # A missing positive old recall is an observation, not a failed test.
        return {
            "preset": preset_name, "world_steps": len(reference),
            "natural_memory_hook_calls": len(work),
            "candidate_episode_volume": sum(x["candidate_episodes"]
                                             for x in work),
            "max_episode_count": max(x["episode_count"] for x in reference),
            "memory_recall_proposals": sum(x["recall_proposals"]
                                           for x in reference),
            "accepted_waking_uc": sum(x["charged_uc"] for x in reference),
            "observer_elapsed_ns": sum(x["elapsed_ns"] for x in work),
            "m11_same_journal_memory_and_uc": True,
            "cold_restore_verified": True,
        }

rows = [experiment("empty-land", 3), experiment("oasis", 5)]
assert sum(row["world_steps"] for row in rows) >= 2
assert sum(row["natural_memory_hook_calls"] for row in rows) > 0, (
    "no naturally exercised Memory scoring observed", rows)
print("I1_NATURAL_RECALL_WORK_UC_564=" + json.dumps({
    "evidence": "natural-M11-observer-only",
    "cpu_is_not_uc": True,
    "no_l2_old_recall_claim": True,
    "no_l3_claim": True,
    "rows": rows,
}, sort_keys=True))
'''


class NaturalM11MemoryRecallWorkUC564(unittest.TestCase):
    def test_observation_never_changes_m11_causal_or_uc_custody(self):
        with TemporaryDirectory() as folder:
            generated = Path(folder) / "generated"
            built = subprocess.run(
                [sys.executable, str(ROOT / "scripts/build_i1_fork.py"),
                 "--output", str(generated)],
                cwd=ROOT, text=True, capture_output=True, timeout=180)
            self.assertEqual(built.returncode, 0,
                             built.stdout + built.stderr)
            env = os.environ.copy()
            env["PYTHONPATH"] = os.pathsep.join((
                str(generated), str(ROOT / "src"), str(ROOT / "tools")))
            run = subprocess.run(
                [sys.executable, "-c", PROGRAM], cwd=ROOT,
                env=env, text=True, capture_output=True, timeout=300)
            self.assertEqual(run.returncode, 0,
                             run.stdout + run.stderr)
            lines = [line for line in run.stdout.splitlines()
                     if line.startswith("I1_NATURAL_RECALL_WORK_UC_564=")]
            self.assertEqual(len(lines), 1, run.stdout)
            payload = json.loads(lines[0].split("=", 1)[1])
            self.assertEqual(payload["evidence"], "natural-M11-observer-only")
            self.assertEqual([x["preset"] for x in payload["rows"]],
                             ["empty-land", "oasis"])
            for row in payload["rows"]:
                self.assertTrue(row["m11_same_journal_memory_and_uc"])
                self.assertTrue(row["cold_restore_verified"])
                self.assertGreaterEqual(row["natural_memory_hook_calls"], 0)
                self.assertGreaterEqual(row["candidate_episode_volume"], 0)
                self.assertGreaterEqual(row["accepted_waking_uc"], 0)
            print(lines[0])


if __name__ == "__main__":
    unittest.main()
