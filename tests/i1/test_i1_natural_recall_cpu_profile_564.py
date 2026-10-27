"""#564: operator-only CPU accounting during real paired M11 recall lives.

This test extends the already validated #573 natural paired protocol, without
activating an index in I1. It reports costs of maintaining the derived index,
candidate selection, shadow construction, exhaustive and candidate ranking,
and both full/selected spontaneous recall. Timings are informational only;
only equality of causal results is a gate. In particular, the disposable
shadow-owner construction is NOT an estimate of a production index cost.
"""
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[2]

# Explicit markers prevent silent drift if the approved natural protocol
# changes. Every edit changes only the diagnostic wrapper, never I1 source.
REPLACEMENTS = (
    (
        "from contextlib import nullcontext\n",
        "from contextlib import nullcontext\n"
        "from statistics import median\n"
        "from time import perf_counter_ns\n",
    ),
    (
        "                count = self.episode_count\n",
        "                count = self.episode_count\n"
        "                index_maintenance_t0 = perf_counter_ns()\n",
    ),
    (
        "                candidates = selector.select(st=st, t_monde=t_monde)\n",
        "                index_maintenance_ns = ("
        "perf_counter_ns() - index_maintenance_t0)\n"
        "                selection_t0 = perf_counter_ns()\n"
        "                candidates = selector.select(st=st, t_monde=t_monde)\n"
        "                selection_ns = perf_counter_ns() - selection_t0\n",
    ),
    (
        "                shadow = subset(self, candidates)\n",
        "                setup_t0 = perf_counter_ns()\n"
        "                shadow = subset(self, candidates)\n"
        "                shadow_setup_ns = perf_counter_ns() - setup_t0\n",
    ),
    (
        "                full_rank = self.recall(st=st, t_monde=t_monde)\n",
        "                full_rank_t0 = perf_counter_ns()\n"
        "                full_rank = self.recall(st=st, t_monde=t_monde)\n"
        "                full_rank_ns = perf_counter_ns() - full_rank_t0\n",
    ),
    (
        "                shadow_rank = shadow.recall(st=st, t_monde=t_monde)\n",
        "                shadow_rank_t0 = perf_counter_ns()\n"
        "                shadow_rank = shadow.recall(st=st, t_monde=t_monde)\n"
        "                shadow_rank_ns = perf_counter_ns() - shadow_rank_t0\n",
    ),
    (
        "                anticipated = original(\n"
        "                    shadow, st=st, t_monde=t_monde, cycle=cycle)\n"
        "                actual = original(\n"
        "                    self, st=st, t_monde=t_monde, cycle=cycle)\n",
        "                shadow_spont_t0 = perf_counter_ns()\n"
        "                anticipated = original(\n"
        "                    shadow, st=st, t_monde=t_monde, cycle=cycle)\n"
        "                shadow_spont_ns = perf_counter_ns() - shadow_spont_t0\n"
        "                true_spont_t0 = perf_counter_ns()\n"
        "                actual = original(\n"
        "                    self, st=st, t_monde=t_monde, cycle=cycle)\n"
        "                true_spont_ns = perf_counter_ns() - true_spont_t0\n",
    ),
    (
        '                    "index_rebuilt": rebuilt,\n',
        '                    "index_rebuilt": rebuilt,\n'
        '                    "index_maintenance_ns": index_maintenance_ns,\n'
        '                    "candidate_selection_ns": selection_ns,\n'
        '                    "disposable_shadow_setup_ns": shadow_setup_ns,\n'
        '                    "exhaustive_rank_ns": full_rank_ns,\n'
        '                    "selected_rank_ns": shadow_rank_ns,\n'
        '                    "exhaustive_spontaneous_ns": true_spont_ns,\n'
        '                    "selected_spontaneous_ns": shadow_spont_ns,\n',
    ),
    (
        '            "cold_and_reports_identical": True,\n',
        '            "cold_and_reports_identical": True,\n'
        '            "cpu_ns": {\n'
        '                name: {\n'
        '                    "total": sum(item[name] for item in work),\n'
        '                    "median": median(item[name] for item in work),\n'
        '                }\n'
        '                for name in (\n'
        '                    "index_maintenance_ns",\n'
        '                    "candidate_selection_ns",\n'
        '                    "disposable_shadow_setup_ns",\n'
        '                    "exhaustive_rank_ns",\n'
        '                    "selected_rank_ns",\n'
        '                    "exhaustive_spontaneous_ns",\n'
        '                    "selected_spontaneous_ns",\n'
        '                )\n'
        '            },\n'
        '            "index_rebuilds": sum(item["index_rebuilt"]\n'
        '                                  for item in work),\n',
    ),
    (
        'results = [\n'
        '    natural_pair("empty-land", 12),\n'
        '    natural_pair("oasis", 12),\n'
        ']',
        'results = [\n'
        '    natural_pair("empty-land", 48),\n'
        '    natural_pair("oasis", 32),\n'
        ']',
    ),
    (
        '"I1_NATURAL_SHADOW_RECALL_564="',
        '"I1_NATURAL_RECALL_CPU_PROFILE_564="',
    ),
    (
        '    "timing_not_measured": True,\n',
        '    "timing_not_measured": False,\n'
        '    "timing_is_informational_not_a_ci_threshold": True,\n'
        '    "candidate_shadow_setup_is_disposable_operator_cost": True,\n'
        '    "no_production_speedup_claim": True,\n',
    ),
)

CPU_FIELDS = (
    "index_maintenance_ns",
    "candidate_selection_ns",
    "disposable_shadow_setup_ns",
    "exhaustive_rank_ns",
    "selected_rank_ns",
    "exhaustive_spontaneous_ns",
    "selected_spontaneous_ns",
)


class NaturalRecallCPUCustody564(unittest.TestCase):
    def test_paired_natural_m11_cpu_profile_is_noncausal(self):
        original = runpy.run_path(
            str(ROOT / "tests/i1/test_i1_natural_shadow_recall_564.py")
        )["PROGRAM"]
        program = original
        for before, after in REPLACEMENTS:
            self.assertEqual(
                program.count(before), 1,
                "source natural shadow protocol changed: " + repr(before),
            )
            program = program.replace(before, after)
        # Check Python syntax BEFORE running the generated engine.
        compile(program, "<i1-natural-cpu-observer-564>", "exec")

        with TemporaryDirectory() as temp:
            generated = Path(temp) / "generated"
            build = subprocess.run(
                [sys.executable, str(ROOT / "scripts/build_i1_fork.py"),
                 "--output", str(generated)], cwd=ROOT, text=True,
                capture_output=True, timeout=180)
            self.assertEqual(build.returncode, 0, build.stdout + build.stderr)
            env = os.environ.copy()
            env["PYTHONPATH"] = os.pathsep.join(
                (str(generated), str(ROOT / "src"), str(ROOT / "tools")))
            env["PYTHONHASHSEED"] = "0"
            actual = subprocess.run(
                [sys.executable, "-c", program], cwd=ROOT,
                env=env, text=True, capture_output=True, timeout=300)
            self.assertEqual(actual.returncode, 0,
                             actual.stdout + actual.stderr)

            output = [line for line in actual.stdout.splitlines()
                      if line.startswith("I1_NATURAL_RECALL_CPU_PROFILE_564=")]
            self.assertEqual(len(output), 1, actual.stdout)
            result = json.loads(output[0].split("=", 1)[1])
            self.assertEqual(result["evidence"], "natural-M11-paired-shadow-L1")
            self.assertFalse(result["timing_not_measured"])
            self.assertTrue(result["timing_is_informational_not_a_ci_threshold"])
            self.assertTrue(result["candidate_shadow_setup_is_disposable_operator_cost"])
            self.assertTrue(result["no_production_speedup_claim"])
            self.assertTrue(result["shadow_never_controls_recall"])
            self.assertTrue(result["index_not_serialized"])
            self.assertEqual([item["preset"] for item in result["rows"]],
                             ["empty-land", "oasis"])
            for row, ceiling in zip(result["rows"], (48, 32)):
                self.assertGreater(row["physical_steps"], 0)
                self.assertLessEqual(row["physical_steps"], ceiling)
                self.assertTrue(row["cold_and_reports_identical"])
                self.assertGreater(row["recall_shadow_checks"], 0)
                self.assertGreaterEqual(row["episode_volume"],
                                        row["candidate_volume"])
                self.assertGreaterEqual(row["index_rebuilds"], 1)
                self.assertLessEqual(row["index_rebuilds"],
                                     row["recall_shadow_checks"])
                self.assertEqual(set(row["cpu_ns"]), set(CPU_FIELDS))
                for measurement in row["cpu_ns"].values():
                    # Timing and speedup are NOT pass/fail criteria.
                    self.assertGreaterEqual(measurement["total"], 0)
                    self.assertGreaterEqual(measurement["median"], 0)
            print(output[0])


if __name__ == "__main__":
    unittest.main()
