"""Declared descriptive diagnostic: Candidate-G decision-relevance vs projection.

Protocol: docs/STAGE1_CANDIDATE_G_PROJECTION_DEPENDENCE.md. Reuses the frozen
#1146 fixtures unchanged; only the model's simulation/projection differs by arm.
No World, no life, no study index.

    python -m i3.lab.stage1_candidate_g_projection_dependence OUTPUT.json
"""
from __future__ import annotations

import json
import sys

from . import stage1_candidate_g_reference_recurrence_falsifier as G
from ..modules.body import BodyLaws, CognitiveBudget
from ..modules.mind import W
from ..modules.genome import midpoint
from ..modules.mind import Mind
from ..modules.water_recurrence_opportunity import paid_water_personal_recurrence_value

SCHEMA = "i3-stage1-candidate-g-projection-dependence/v1"
ARMS = ("reference", "candidate_f_projection", "per_step")
REFERENCE_1146 = {"selected_epistemic": 1, "declined": 27,
                  "max_information_value": 0.002384135709742774,
                  "best_trial_advantage": 0.10848337088618987}


def make_mind(arm):
    if arm == "candidate_f_projection":
        mind = Mind(midpoint(), 197, simulation_mode="candidate_f")
        mind.projection_accounting = "event_local_quadratic4"
    else:
        mind = Mind(midpoint(), 197)
    mind.map = {}
    mind.effects.observe(("se_deplacer",), (-2., -.2, -.4, 0., 0.))
    mind.effects.observe(("attendre",), (-.35, -.2, -.4, .2, 0.))
    mind.effects.observe(("dormir",), (3., -.35, -.4, 0., 4.))
    mind._drift = mind.drift()
    if arm == "per_step":
        mind.proj_chunks = (1,) * 255
    if hasattr(mind, "first_contact_omega"):
        raise RuntimeError("diagnostic must not read genomic omega")
    return mind


def evaluate(arm):
    recurrence, memory = G.recurrence_2_6_10(), G.effect_memory()
    rows = []
    for channel, name in enumerate(G.CHANNEL_NAMES):
        for level in G.LEVELS:
            body = list(G.BASE_BODY)
            body[channel] = level
            body = tuple(body)
            for horizon in G.HORIZONS:
                r = paid_water_personal_recurrence_value(
                    make_mind(arm), memory, recurrence, G.EXPLORE, G.ORDINARY,
                    horizon, CognitiveBudget(body, BodyLaws()))
                for key, value in r["work"].items():
                    if value > r["forecast_work_ceiling"][key]:
                        raise RuntimeError("actual work exceeded common ceiling")
                rows.append({
                    "channel": name, "channel_index": channel, "level": level,
                    "horizon": horizon,
                    "information_value": r["trial_information_value"],
                    "trial_advantage": r["trial_advantage"],
                    "target_choices": list(r["target_node_best_choices"]),
                    "work": dict(r["work"]),
                })
    selected = [x for x in rows if "TRIAL" in x["target_choices"]
                and x["information_value"] > 1e-12 and x["trial_advantage"] > 1e-12]
    work_keys = rows[0]["work"].keys()
    return rows, {
        "evaluated": len(rows),
        "selected_epistemic": len(selected),
        "selected_water_deficit": sum(x["channel_index"] == W for x in selected),
        "selected_other_deficit": sum(x["channel_index"] != W for x in selected),
        "declined": sum(x["target_choices"] == ["DECLINE_TRIAL"] for x in rows),
        "max_information_value": max(x["information_value"] for x in rows),
        "best_trial_advantage": max(x["trial_advantage"] for x in rows),
        "mean_work": {k: sum(x["work"][k] for x in rows) / len(rows) for k in work_keys},
        "max_work": {k: max(x["work"][k] for x in rows) for k in work_keys},
    }


def run(out_path):
    arms = {arm: evaluate(arm) for arm in ARMS}
    ref = arms["reference"][1]
    valid = (ref["selected_epistemic"] == REFERENCE_1146["selected_epistemic"]
             and ref["declined"] == REFERENCE_1146["declined"]
             and abs(ref["max_information_value"] - REFERENCE_1146["max_information_value"]) < 1e-12
             and abs(ref["best_trial_advantage"] - REFERENCE_1146["best_trial_advantage"]) < 1e-12)
    for arm in ARMS:
        s = arms[arm][1]
        s["mean_work_ratio_to_reference"] = {
            k: (s["mean_work"][k] / ref["mean_work"][k] if ref["mean_work"][k] else None)
            for k in s["mean_work"]}
    report = {"schema": SCHEMA, "protocol": "STAGE1_CANDIDATE_G_PROJECTION_DEPENDENCE.md",
              "world_access": False, "lives": 0, "omega_read": False,
              "reference_reproduces_1146": valid,
              "summary": {arm: s for arm, (_, s) in arms.items()},
              "rows": {arm: rows for arm, (rows, _) in arms.items()}}
    with open(out_path, "w") as fh:
        json.dump(report, fh, indent=1, sort_keys=True)
    return report


if __name__ == "__main__":
    rep = run(sys.argv[1])
    print("reference reproduces #1146:", rep["reference_reproduces_1146"])
    for arm, s in rep["summary"].items():
        print(arm, {k: v for k, v in s.items() if k not in ("mean_work", "max_work")})
        print("   mean work", {k: round(v, 1) for k, v in s["mean_work"].items()})
