"""Differential published-agency correction lookup test for generated I1."""
from pathlib import Path
from tempfile import TemporaryDirectory
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
import inspect, textwrap
from types import SimpleNamespace as NS
from i1.modules.causal_model import CausalModel, CausalModelConfig

config = CausalModelConfig(version="index-test", n1=1, n2=1, n_sec=1, m_sec=1)
source = inspect.getsource(CausalModel.established_prediction_corrections)
new_a = '''        # Derived, read-only index of already published agency evidence.
        # Rebuild on every query: no stale cache, no new causal owner, and
        # preserve the original lexical evidence-ID ordering within keys.
        published_by_action: dict[tuple[str, int, int], list[AgencyEvidence]] = {}
        for report in self.published_agency_evidence():
            key = (report.option_ref, report.sent_t_monde, report.observed_t_monde)
            published_by_action.setdefault(key, []).append(report)

'''
old_b = '''            for report in self.published_agency_evidence():
                if (
                    report.option_ref != witness.option_ref
                    or report.sent_t_monde != witness.sent_t_monde
                    or report.observed_t_monde != witness.observed_t_monde
                ):
                    continue
                compatible = any('''
new_b = '''            for report in published_by_action.get(
                (witness.option_ref, witness.sent_t_monde,
                 witness.observed_t_monde), ()
            ):
                compatible = any('''
assert source.count(new_a) == source.count(new_b) == 1
former = source.replace(new_a, "", 1).replace(new_b, old_b, 1)
ns = dict(CausalModel.established_prediction_corrections.__globals__)
exec("from __future__ import annotations\n" + textwrap.dedent(former), ns)
baseline = ns["established_prediction_corrections"]

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
print("I1_PUBLISHED_AGENCY_INDEX_PARITY_OK")
"""
            run = subprocess.run([sys.executable, "-c", program],
                env={"PYTHONPATH": str(out)}, capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertIn("I1_PUBLISHED_AGENCY_INDEX_PARITY_OK", run.stdout)
