"""Parity audit for genome-v4 omega -> Candidate-F first-contact wiring.

The explicit-omega #1125 falsifier is the immutable comparison. This lab only
checks that the new opt-in genomic adapter supplies the same omega internally.
No World, life or study index.
"""
from __future__ import annotations

import json
import sys

from ..modules.body import BodyLaws, CognitiveBudget, CognitiveFundingError, CognitiveWork
from ..modules.genome import midpoint, validate
from ..modules.genomic_omega_candidate_f import GenomicOmegaCandidateFMind
from . import stage1_omega_candidate_f_falsifier as F
from . import stage1_omega_falsifier as W

SCHEMA = "i3-genomic-omega-candidate-f-wiring-parity/v1"


def _record(memory, key, delta):
    after = tuple(a + b for a, b in zip(W.BASE, delta))
    memory.observe(
        key, W.BASE, CognitiveWork(),
        CognitiveBudget(after, BodyLaws()))


def make_genomic_mind(omega):
    genome = midpoint()
    genome["genes"]["omega"] = omega
    validate(genome)
    mind = GenomicOmegaCandidateFMind(genome, 97)
    mind.map = {}
    for effect_key, branch_key, delta in (
        (("se_deplacer",), ("se_deplacer", None), (-2., -.2, -.4, 0., 0.)),
        (("attendre",), ("attendre", None), (-.35, -.2, -.4, .2, 0.)),
        (("dormir",), ("dormir", None), (3., -.35, -.4, 0., 4.)),
    ):
        mind.effects.observe(effect_key, delta)
        _record(mind.branch_memory, branch_key, delta)
    mind._drift = mind.drift()
    return mind


def evaluate_genomic(omega):
    rows = []
    for channel, level, body, horizon in W.grid():
        mind = make_genomic_mind(omega)
        try:
            result = mind.paid_water_first_contact(
                W.EXPLORE,
                W.STOP_AFTER_PREFIX,
                horizon,
                CognitiveBudget(body, BodyLaws()))
        except CognitiveFundingError:
            rows.append({
                "channel": channel,
                "level": level,
                "horizon": horizon,
                "status": "UNFUNDED",
            })
            continue
        rows.append({
            "channel": channel,
            "level": level,
            "horizon": horizon,
            "status": "EVALUATED",
            "choices": list(result["target_node_best_choices"]),
            "trial_information_value":
                result["trial_information_value"],
            "trial_advantage": result["trial_advantage"],
            "water_revelation_advantage":
                result["water_revelation_advantage"],
            "work": dict(result["work"]),
            "forecast_work_ceiling":
                dict(result["forecast_work_ceiling"]),
        })
    return rows


def run(out_path):
    arms = {}
    all_equal = True
    mismatches = []
    for omega in W.OMEGAS:
        explicit_rows, explicit_summary = F.evaluate(omega)
        genomic_rows = evaluate_genomic(omega)
        equal = genomic_rows == explicit_rows
        all_equal = all_equal and equal
        if not equal:
            for index, (g, e) in enumerate(zip(genomic_rows, explicit_rows)):
                if g != e:
                    mismatches.append({
                        "omega": omega,
                        "index": index,
                        "genomic": g,
                        "explicit": e,
                    })
                    break
        arms[str(omega)] = {
            "rows_equal": equal,
            "states": len(genomic_rows),
            "explicit_summary": explicit_summary,
        }

    report = {
        "schema": SCHEMA,
        "world_access": False,
        "lives": 0,
        "arms": arms,
        "total_states_compared": len(W.OMEGAS) * len(tuple(W.grid())),
        "exact_statewise_parity": all_equal,
        "first_mismatch_per_arm": mismatches,
        "genomic_adapter_reads_omega": True,
        "reference_mind_reads_omega": False,
        "runtime_policy_registered": False,
        "verdict": (
            "GENOMIC_OMEGA_WIRING_EXACTLY_REPRODUCES_FROZEN_EXPLICIT_OMEGA"
            if all_equal
            else "GENOMIC_OMEGA_WIRING_PARITY_FAILED"),
        "selection_authorized": False,
        "reference_adoption_authorized": False,
    }
    with open(out_path, "w") as fh:
        json.dump(report, fh, indent=1, sort_keys=True)
    return report


if __name__ == "__main__":
    print(json.dumps(run(sys.argv[1]), indent=1, sort_keys=True))
