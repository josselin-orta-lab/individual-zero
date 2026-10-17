"""Differential published-agency correction lookup test for generated I1."""
from pathlib import Path
from tempfile import TemporaryDirectory
import os
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


class PublishedAgencyIndexTests(unittest.TestCase):
    def test_indexed_corrections_match_preoptimization_algorithm(self):
        with TemporaryDirectory() as d:
            out = Path(d) / "built"
            build = subprocess.run([sys.executable, str(ROOT / "scripts/build_i1_fork.py"),
                "--output", str(out)], capture_output=True, text=True)
            self.assertEqual(build.returncode, 0, build.stderr)
            program = r"""
import inspect, textwrap, os, time, statistics, json, sys
from types import SimpleNamespace as NS
from i1.modules.causal_model import CausalModel, CausalModelConfig

config = CausalModelConfig(version="index-test", n1=1, n2=1, n_sec=1, m_sec=1)
source = inspect.getsource(CausalModel.established_prediction_corrections)
new_a = '''        # Ephemeral published evidence view. The first two admissible
        # lookups scan it directly; only a third lookup pays for an index.
        # No persistent cache, extra causal owner or hidden information.
        published_reports: tuple[AgencyEvidence, ...] | None = None
        published_by_action: dict[
            tuple[str, int, int], list[AgencyEvidence]
        ] | None = None
        eligible_lookups = 0

'''
old_b = '''            for report in self.published_agency_evidence():
                if (
                    report.option_ref != witness.option_ref
                    or report.sent_t_monde != witness.sent_t_monde
                    or report.observed_t_monde != witness.observed_t_monde
                ):
                    continue
                compatible = any('''
new_b = '''            if published_reports is None:
                published_reports = self.published_agency_evidence()
            eligible_lookups += 1
            if eligible_lookups == 3:
                published_by_action = {}
                for report in published_reports:
                    key = (
                        report.option_ref, report.sent_t_monde,
                        report.observed_t_monde,
                    )
                    published_by_action.setdefault(key, []).append(report)

            witness_key = (
                witness.option_ref, witness.sent_t_monde,
                witness.observed_t_monde,
            )
            matching_reports = (
                published_by_action.get(witness_key, ())
                if published_by_action is not None
                else (
                    report for report in published_reports
                    if (report.option_ref, report.sent_t_monde,
                        report.observed_t_monde) == witness_key
                )
            )
            for report in matching_reports:
                compatible = any('''
assert source.count(new_a) == source.count(new_b) == 1
former = source.replace(new_a, "", 1).replace(new_b, old_b, 1)
ns = dict(CausalModel.established_prediction_corrections.__globals__)
exec("from __future__ import annotations\n" + textwrap.dedent(former), ns)
baseline = ns["established_prediction_corrections"]

# No numeric witness should require any agency projection or index.
empty = CausalModel(config)
empty._agency_evidence["noise"] = object()
empty.published_agency_evidence = lambda: (_ for _ in ()).throw(
    AssertionError("unused agency evidence eagerly accessed")
)
assert empty.established_prediction_corrections() == ()

for noise in (0, 16, 128, 512):
    model = CausalModel(config)
    model._published["toxic:berry_b"] = NS(
        ref="toxic:berry_b", causal_status="etablie",
        predicate="toxic_item", subject_ref="berry_b", context_signature="global",
    )
    matching = NS(
        identifier="trial:0", contingency_ref="toxic:berry_b",
        comparator_ref="agency:matched", observed_effect=True,
        comparator_status="conforming", attribution="self_compatible",
        episode_ref="episode:0", command_ref="option:0",
        emitted_step=5, observed_step=6, context_signature="witness",
    )
    model._causal_interventions["trial:0"] = matching
    model._agency_evidence["agency:matched"] = NS(
        identifier="agency:matched", source="agency_comparator",
        episode_ref="episode:0", option_ref="option:0",
        sent_t_monde=5, observed_t_monde=6,
        status="conforming", attribution="self_compatible",
        effects=(("integrity","conforming",80.0,65.0,0.0,"v1"),),
    )
    for i in range(noise):
        model._agency_evidence[f"agency:noise:{i:04d}"] = NS(
            identifier=f"agency:noise:{i:04d}", source="agency_comparator",
            episode_ref="episode:other", option_ref=f"option:{i+10}",
            sent_t_monde=i+10, observed_t_monde=i+11,
            status="conforming", attribution="self_compatible",
            effects=(("integrity","conforming",80.0,65.0,0.0,"v1"),),
        )
    model._numeric_witnesses["witness:0"] = NS(
        contingency_ref="toxic:berry_b", command_target="berry_b",
        observed_t_monde=6, option_ref="option:0", sent_t_monde=5,
        variable="integrity", observed_after=65.0,
        command_primitive="manger",
        observed_before_body=(("energy",80.0),("food",80.0),
                              ("water",80.0),("integrity",80.0)),
        observed_before_position=(1,1),
        observed_before_state_digest="a"*64,
    )
    previous = baseline(model)
    current = model.established_prediction_corrections()
    assert previous == current, (noise, previous, current)
    assert len(current) == 1
    assert current[0].agency_evidence_ref == "agency:matched"
    # Refutation boundary must still prevent stale evidence from authorizing
    # corrections, irrespective of index size.
    model._causal_revision_boundaries["toxic:berry_b"] = (6,"revision")
    assert baseline(model) == model.established_prediction_corrections() == ()
def workload(noise_count, witness_count):
    # Purely synthetic published data; measures one read-only query, never
    # makes a scientific claim about the individual's causal knowledge.
    model = CausalModel(config)
    model._published["toxic:berry_b"] = NS(
        ref="toxic:berry_b", causal_status="etablie",
        predicate="toxic_item", subject_ref="berry_b",
        context_signature="global",
    )
    for i in range(noise_count):
        model._agency_evidence[f"agency:noise:{i:05d}"] = NS(
            identifier=f"agency:noise:{i:05d}", source="agency_comparator",
            episode_ref=f"episode:other:{i}", option_ref=f"option:other:{i}",
            sent_t_monde=i+2000, observed_t_monde=i+2001,
            status="conforming", attribution="self_compatible",
            effects=(("integrity", "conforming", 80.0, 65.0, 0.0, "v1"),),
        )
    for i in range(witness_count):
        ref, option = f"agency:match:{i:04d}", f"option:witness:{i}"
        sent, observed = 100+i, 101+i
        model._agency_evidence[ref] = NS(
            identifier=ref, source="agency_comparator",
            episode_ref=f"episode:witness:{i}", option_ref=option,
            sent_t_monde=sent, observed_t_monde=observed,
            status="conforming", attribution="self_compatible",
            effects=(("integrity", "conforming", 80.0, 65.0, 0.0, "v1"),),
        )
        model._causal_interventions[f"trial:{i:04d}"] = NS(
            identifier=f"trial:{i:04d}", contingency_ref="toxic:berry_b",
            comparator_ref=ref, observed_effect=True,
            comparator_status="conforming", attribution="self_compatible",
            episode_ref=f"episode:witness:{i}", command_ref=option,
            emitted_step=sent, observed_step=observed,
            context_signature=f"distinct-context:{i}",
        )
        model._numeric_witnesses[f"witness:{i:04d}"] = NS(
            contingency_ref="toxic:berry_b", command_target="berry_b",
            observed_t_monde=observed, option_ref=option,
            sent_t_monde=sent, variable="integrity", observed_after=65.0,
            command_primitive="manger",
            observed_before_body=(("energy", 80.0), ("food", 80.0),
                                  ("water", 80.0), ("integrity", 80.0)),
            observed_before_position=(1, 1),
            observed_before_state_digest="a"*64,
        )
    return model

# More than one witness, lexical ordering, and no-witness cases must preserve
# the complete returned correction tuple, not only the count.
for noise, witnesses in ((0, 0), (512, 0), (1024, 1),
                         (1024, 8), (1024, 48), (2048, 48)):
    model = workload(noise, witnesses)
    original, updated = baseline(model), model.established_prediction_corrections()
    assert original == updated, (noise, witnesses)
    assert len(updated) == witnesses

if os.environ.get("I1_AGENCY_INDEX_BENCH") == "1":
    timings = []
    for noise, witnesses in ((2048, 0), (2048, 1), (2048, 8), (2048, 48)):
        model = workload(noise, witnesses)
        former, current = [], []
        for i in range(7):
            runners = [(baseline, former),
                       (CausalModel.established_prediction_corrections, current)]
            if i % 2:
                runners.reverse()
            for run, samples in runners:
                start = time.perf_counter_ns()
                result = run(model)
                samples.append(time.perf_counter_ns() - start)
                assert len(result) == witnesses
        old = statistics.median(former)
        new = statistics.median(current)
        timings.append({
            "unrelated_agency_reports": noise,
            "numeric_witnesses": witnesses,
            "old_median_us": round(old/1000, 2),
            "new_median_us": round(new/1000, 2),
            "speedup": round(old/new, 2) if new else None,
        })
    print("I1_AGENCY_INDEX_BENCH_JSON " + json.dumps({
        "kind": "synthetic_read_only_CPU_benchmark_not_scientific_evidence",
        "python": sys.version.split()[0],
        "repetitions": 7,
        "workloads": timings,
    }, sort_keys=True))
print("I1_PUBLISHED_AGENCY_INDEX_PARITY_OK")
"""
            run = subprocess.run([sys.executable, "-c", program],
                env={"PYTHONPATH": str(out),
                     "I1_AGENCY_INDEX_BENCH": os.environ.get("I1_AGENCY_INDEX_BENCH", "0")},
                capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertIn("I1_PUBLISHED_AGENCY_INDEX_PARITY_OK", run.stdout)
            if os.environ.get("I1_AGENCY_INDEX_BENCH") == "1":
                self.assertIn("I1_AGENCY_INDEX_BENCH_JSON ", run.stdout)
                print(run.stdout.split("I1_AGENCY_INDEX_BENCH_JSON ", 1)[1].splitlines()[0],
                      flush=True)
