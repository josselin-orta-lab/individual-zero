"""Candidate-G Stage-1 software falsifier: P1.3 projection + personal recurrence.

No World, no runtime policy and no scientific life. The fixed characterization
reuses the already-established personal-recurrence fixture but reports every
decision-boundary state explicitly.

Candidate-G hypothesis:
- P1.3 reference simulator/projection remains unchanged;
- no omega or inherited first-contact expectation;
- future matching-water availability comes only from paid personal recurrence;
- the existing Stage-1 water kernel remains physically paid.
"""
from __future__ import annotations

from dataclasses import asdict
import json

from ..modules.body import BodyLaws, CognitiveBudget, CognitiveWork
from ..modules.genome import midpoint
from ..modules.mind import Mind, W
from ..modules.opportunity_recurrence import OpportunityRecurrenceMemory
from ..modules.reference_branches import ReferenceBranchMemory
from ..modules.water_recurrence_opportunity import (
    paid_water_personal_recurrence_value)

SCHEMA = "i3-stage1-candidate-g-reference-recurrence-falsifier/v1"
EXPLORE = (("se_deplacer",),)
ORDINARY = (("stop-after-prefix", ()),)
LEVELS = (20.0, 30.0, 40.0, 50.0)
HORIZONS = (4, 6, 8, 12)
BASE_BODY = (80.0, 80.0, 80.0, 80.0, 80.0)
CHANNEL_NAMES = ("energy", "food", "water", "integrity", "vigilance")


def _record(memory, key, delta):
    after = tuple(a + b for a, b in zip((50.,) * 5, delta))
    memory.observe(
        key, (50.,) * 5, CognitiveWork(),
        CognitiveBudget(after, BodyLaws()))


def effect_memory():
    memory = ReferenceBranchMemory()
    for key, delta in (
            (("se_deplacer", None), (-2., -.2, -.4, 0., 0.)),
            (("attendre", None), (-.35, -.2, -.4, .2, 0.)),
            (("dormir", None), (3., -.35, -.4, 0., 4.))):
        _record(memory, key, delta)
    return memory


def recurrence_2_6_10():
    memory = OpportunityRecurrenceMemory()
    onsets = {1, 3, 9, 19}
    for step in range(1, 20):
        memory.observe(
            (step in onsets, False),
            CognitiveBudget((80.,) * 5, BodyLaws()))
    return memory


def make_mind():
    mind = Mind(midpoint(), 197)
    mind.map = {}
    mind.effects.observe(
        ("se_deplacer",), (-2., -.2, -.4, 0., 0.))
    mind.effects.observe(
        ("attendre",), (-.35, -.2, -.4, .2, 0.))
    mind.effects.observe(
        ("dormir",), (3., -.35, -.4, 0., 4.))
    mind._drift = mind.drift()
    if mind.simulation_mode != "reference":
        raise RuntimeError("Candidate-G must keep P1.3 reference simulation")
    if mind.projection_accounting != "chunk_end":
        raise RuntimeError("Candidate-G must keep P1.3 projection accounting")
    if hasattr(mind, "first_contact_omega"):
        raise RuntimeError("Candidate-G must not read genomic omega")
    return mind


def characterize() -> dict:
    recurrence = recurrence_2_6_10()
    memory = effect_memory()
    rows = []

    for channel, channel_name in enumerate(CHANNEL_NAMES):
        for level in LEVELS:
            body = list(BASE_BODY)
            body[channel] = level
            body = tuple(body)
            for horizon in HORIZONS:
                allowance = CognitiveBudget(body, BodyLaws())
                result = paid_water_personal_recurrence_value(
                    make_mind(), memory, recurrence,
                    EXPLORE, ORDINARY, horizon, allowance)
                if not result["trial_evaluated"]:
                    raise RuntimeError(
                        "fixed recurrence support unexpectedly skipped trial")
                ceiling = result["forecast_work_ceiling"]
                for key, value in result["work"].items():
                    if value > ceiling[key]:
                        raise RuntimeError(
                            "Candidate-G actual work exceeded common ceiling")
                rows.append({
                    "channel": channel_name,
                    "channel_index": channel,
                    "level": level,
                    "horizon": horizon,
                    "future_probability":
                        result["future_water_opportunity_probability"],
                    "information_value": result["trial_information_value"],
                    "trial_advantage": result["trial_advantage"],
                    "target_choices":
                        tuple(result["target_node_best_choices"]),
                    "water_revelation_advantage":
                        result["water_revelation_advantage"],
                    "work": dict(result["work"]),
                    "forecast_work_ceiling":
                        dict(result["forecast_work_ceiling"]),
                    "source":
                        result["future_opportunity_probability_source"],
                })

    selected = [
        row for row in rows
        if "TRIAL" in row["target_choices"]
        and row["information_value"] > 1e-12
    ]
    declined = [
        row for row in rows
        if row["target_choices"] == ("DECLINE_TRIAL",)
    ]
    water_selected = [
        row for row in selected if row["channel_index"] == W
    ]
    nonwater_selected = [
        row for row in selected if row["channel_index"] != W
    ]
    all_personal = all(
        row["source"] == "PAID_PERSONAL_ONSET_RECURRENCE"
        for row in rows)
    all_paid = all(
        all(row["work"][key] <= row["forecast_work_ceiling"][key]
            for key in row["work"])
        for row in rows)

    rules = {
        "R0_exact_80_states": len(rows) == 80,
        "R1_reference_projection_only": True,
        "R2_personal_recurrence_only": all_personal,
        "R3_actual_work_within_common_ceiling": all_paid,
        "R4_some_selected_and_some_declined":
            bool(selected) and bool(declined),
        "R5_no_selected_nonwater_state": not nonwater_selected,
    }
    verdict = (
        "CANDIDATE_G_REFERENCE_RECURRENCE_SOFTWARE_GATE_PASS"
        if all(rules.values()) else
        "CANDIDATE_G_REFERENCE_RECURRENCE_SOFTWARE_GATE_FAIL")
    return {
        "schema": SCHEMA,
        "lives": 0,
        "world_access": False,
        "simulation_mode": "reference",
        "projection_accounting": "chunk_end",
        "omega_read": False,
        "fixture": {
            "levels": LEVELS,
            "horizons": HORIZONS,
            "recurrence_gaps": (2, 6, 10),
            "effect_memory_records": 3,
        },
        "summary": {
            "evaluated": len(rows),
            "selected_epistemic": len(selected),
            "selected_water_states": len(water_selected),
            "selected_nonwater_states": len(nonwater_selected),
            "declined": len(declined),
            "max_information_value":
                max(row["information_value"] for row in rows),
            "best_trial_advantage":
                max(row["trial_advantage"] for row in rows),
            "worst_trial_advantage":
                min(row["trial_advantage"] for row in rows),
            "future_probabilities": sorted(set(
                row["future_probability"] for row in rows)),
        },
        "selected_states": selected,
        "declined_states": declined,
        "rules": rules,
        "verdict": verdict,
    }


def main():
    print("CANDIDATE_G_REFERENCE_RECURRENCE " + json.dumps(
        characterize(), sort_keys=True))


if __name__ == "__main__":
    main()
