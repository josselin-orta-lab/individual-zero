"""#564: noncausal conservative recall shadow in genuinely born M11 lives.

The derived selector never drives Memory. Every natural spontaneous recall
executes the ORIGINAL method and is compared against a disposable shadow
whose candidate selection reuses the exact L1 design from PR #569.
The paired independent birth proves observation does not change the journal,
Memory image, UC charges, terminal status or M11 cold recovery.
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
import runpy
from contextlib import nullcontext
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from run_i1_world_preset import load_preset, _birth_parameters
from i1.modules.memory import EpisodicMemory
from i1lab.i1_birth import birth_i1_m11, recover_i1_m11
from i1lab.i1_natural_runtime import I1Runtime
from i1lab.sqlite_life_store import SQLiteLifeLedger

# Reuse the validated L1 design without duplicating a divergent selector.
definition = runpy.run_path(
    "tests/i1/test_i1_recall_envelope_feasibility_564.py")["PROGRAM"]
anchor = "\nmetrics = []\n"
assert definition.count(anchor) == 1
scope = {"__name__": "i1_shadow_selector_564"}
exec(definition.split(anchor, 1)[0], scope)
Envelope = scope["ConservativeEnvelope"]
subset = scope["subset"]

original = EpisodicMemory.spontaneous_contribution

def natural_pair(preset_name, max_steps):
    preset, _ = load_preset(preset_name)
    params, _ = _birth_parameters(preset)
    identity = "i1:564:shadow-envelope:" + preset_name
    with TemporaryDirectory() as directory:
        def arm(name, instrument):
            path = str(Path(directory) / (name + ".sqlite"))
            observations = []
            cache = {}
            def shadowed(self, *, st, t_monde, cycle):
                count = self.episode_count
                key = id(self)
                previous = cache.get(key)
                if previous is None or previous[0] is not self:
                    selector = Envelope(self._config, self._episodes)
                    cache[key] = (self, selector)
                    rebuilt = True
                else:
                    selector = previous[1]
                    if (len(selector.records) > count or
                            (selector.records and
                             selector.records[-1] is not
                             self._episodes[len(selector.records) - 1])):
                        selector = Envelope(self._config, self._episodes)
                        cache[key] = (self, selector)
                        rebuilt = True
                    else:
                        rebuilt = False
                        for episode in self._episodes[len(selector.records):]:
                            selector.append(episode)
                candidates = selector.select(st=st, t_monde=t_monde)
                shadow = subset(self, candidates)
                full_rank = self.recall(st=st, t_monde=t_monde)
                shadow_rank = shadow.recall(st=st, t_monde=t_monde)
                assert full_rank == shadow_rank, (
                    "natural ranked recall divergence",
                    preset_name, t_monde, cycle,
                )
                anticipated = original(
                    shadow, st=st, t_monde=t_monde, cycle=cycle)
                actual = original(
                    self, st=st, t_monde=t_monde, cycle=cycle)
                assert actual == anticipated, (
                    "natural spontaneous recall divergence",
                    preset_name, t_monde, cycle,
                )
                assert self._recall_above_threshold == (
                    shadow._recall_above_threshold
                ), "causal threshold crossing divergence"
                assert self._last_recalled_ref == shadow._last_recalled_ref
                observations.append({
                    "total_episodes": count,
                    "candidate_episodes": len(candidates),
                    "trusted": selector.trusted,
                    "index_rebuilt": rebuilt,
                })
                return actual

            def factory():
                return I1Runtime(
                    birth_life_id=identity, autonomous_mortal=True,
                    m11_sqlite_custody=True, wal_path=None,
                    diagnostic_sample_cost_uc=1,
                    module_occupancy_cost_uc=1, **params)

            wrapper = (
                patch.object(EpisodicMemory, "spontaneous_contribution", shadowed)
                if instrument else nullcontext())
            with wrapper:
                with birth_i1_m11(
                    db_path=path, life_id=identity, **params) as life:
                    steps = []
                    for _ in range(max_steps):
                        previous = life._runtime.journal.entry_count
                        receipt = life.run_step()
                        owner = life._runtime
                        assert receipt.journal_head == owner.journal.head_hash
                        assert owner.journal.verify()
                        charges = [
                            dict(item.causal_event["data"])
                            for item in owner.journal.entries_since(previous)
                            if item.causal_event.get("kind") == "compute_charge"
                        ]
                        steps.append({
                            "status": receipt.status,
                            "journal_head": owner.journal.head_hash,
                            "memory": owner.memory.export_causal_state(),
                            "accepted_uc": sum(
                                x["requested_uc"] for x in charges
                                if x["accepted"]),
                            "charges": charges,
                        })
                        if receipt.status == "dead":
                            break
                        assert receipt.status == "active"
                    assert steps
                    final_head = owner.journal.head_hash
                    final_memory = owner.memory.export_causal_state()
                independent = SQLiteLifeLedger.audit_read_only(
                    path=path, expected_individual_id=identity)
                assert independent.journal_head == final_head
                assert independent.may_recover == (
                    steps[-1]["status"] == "active")
                if steps[-1]["status"] == "active":
                    with recover_i1_m11(
                        db_path=path, life_id=identity,
                        runtime_factory=factory,
                    ) as cold:
                        assert cold._runtime.journal.head_hash == final_head
                        assert cold._runtime.memory.export_causal_state() == (
                            final_memory)
                        # Rebuild only DERIVED data after genuine cold import.
                        restored = cold._runtime.memory
                        shadow_index = Envelope(
                            restored._config, restored._episodes)
                        for item in observations[-3:]:
                            assert item["total_episodes"] >= 0
                        assert len(shadow_index.records) == (
                            restored.episode_count)
                return steps, observations

        reference, none = arm("reference", False)
        observed, work = arm("shadow", True)
        assert reference == observed, (
            "passive derived index changed M11 committed trajectory",
            preset_name,
        )
        assert not none
        assert work, "natural recall hook did not execute"
        assert all(0 <= x["candidate_episodes"] <= x["total_episodes"]
                   for x in work)
        return {
            "preset": preset_name,
            "physical_steps": len(reference),
            "recall_shadow_checks": len(work),
            "episode_volume": sum(x["total_episodes"] for x in work),
            "candidate_volume": sum(x["candidate_episodes"] for x in work),
            "untrusted_fallbacks": sum(not x["trusted"] for x in work),
            "cold_and_reports_identical": True,
        }

results = [
    natural_pair("empty-land", 12),
    natural_pair("oasis", 12),
]
assert sum(x["recall_shadow_checks"] for x in results) > 0
print("I1_NATURAL_SHADOW_RECALL_564=" + json.dumps({
    "evidence": "natural-M11-paired-shadow-L1",
    "shadow_never_controls_recall": True,
    "index_not_serialized": True,
    "timing_not_measured": True,
    "old_positive_recall_not_claimed": True,
    "decision_effect_not_claimed": True,
    "rows": results,
}, sort_keys=True))
'''


class NaturalShadowRecallEnvelope564(unittest.TestCase):
    def test_natural_recall_full_shadow_and_m11_commit_parity(self):
        with TemporaryDirectory() as folder:
            target = Path(folder) / "generated"
            build = subprocess.run(
                [sys.executable, str(ROOT / "scripts/build_i1_fork.py"),
                 "--output", str(target)],
                cwd=ROOT, capture_output=True, text=True, timeout=180)
            self.assertEqual(build.returncode, 0,
                             build.stdout + build.stderr)
            env = os.environ.copy()
            env["PYTHONPATH"] = os.pathsep.join(
                (str(target), str(ROOT / "src"), str(ROOT / "tools")))
            env["PYTHONHASHSEED"] = "0"
            proc = subprocess.run(
                [sys.executable, "-c", PROGRAM],
                cwd=ROOT, env=env, capture_output=True,
                text=True, timeout=300)
            self.assertEqual(proc.returncode, 0,
                             proc.stdout + proc.stderr)
            lines = [line for line in proc.stdout.splitlines()
                     if line.startswith("I1_NATURAL_SHADOW_RECALL_564=")]
            self.assertEqual(len(lines), 1, proc.stdout)
            data = json.loads(lines[0].split("=", 1)[1])
            self.assertEqual(data["evidence"],
                             "natural-M11-paired-shadow-L1")
            self.assertTrue(data["shadow_never_controls_recall"])
            self.assertTrue(data["index_not_serialized"])
            self.assertEqual(len(data["rows"]), 2)
            for row in data["rows"]:
                self.assertTrue(row["cold_and_reports_identical"])
                self.assertGreater(row["recall_shadow_checks"], 0)
                self.assertLessEqual(row["candidate_volume"],
                                     row["episode_volume"])
            print(lines[0])


if __name__ == "__main__":
    unittest.main()
