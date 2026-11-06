"""P5c: fail-closed prospective paid action-score-addend mechanism study.

No validation world is instantiated before Git SHA, schedule SHA, declared
protocol and frozen G2 custody pass. All source and allocation locks must be
independently registered in main before the single scientific exposure.
"""
from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys

from i3.lab import p2_ecologies, p4a_validation, p5a_screen, p5c_schedule
from i3.runtime.life import run_life
from i3.runtime.provenance import digest, world_snapshot

PROTOCOL = p5c_schedule.PROTOCOL
MODES = p5c_schedule.MODES
CHANNELS = ("energy", "vigilance")
PHASES = ("decision", "learning")
WORK = ("cycles", "simulated_steps", "memory_items", "replays")
TOL = 1e-7


def _source_sha() -> str:
    root = Path(__file__).resolve().parents[3]
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=root,
        check=True, capture_output=True, text=True, timeout=5
    ).stdout.strip()


def _preflight():
    if _source_sha() != os.environ.get("I3_P5B_SOURCE_SHA", ""):
        raise RuntimeError("P5c exact source is not prospectively locked")
    schedule = p5c_schedule.manifest()
    if schedule["sha256"] != os.environ.get("I3_P5B_SCHEDULE_SHA", ""):
        raise RuntimeError("P5c world allocation is not prospectively locked")
    if os.environ.get("I3_P5B_APPROVED_PROTOCOL", "") != PROTOCOL:
        raise RuntimeError("P5c protocol has no prospective authorization")
    genomes = p4a_validation.verify_frozen_genomes()
    return schedule, genomes


def _receipt(life: dict, *, mode: str, population: int, arm: str,
             slot: int, family: str, repeat: int, index: int,
             seed: int, world_hash: str, genome_hash: str) -> dict:
    acc, trace = life["cognitive_accounting"], life["trace"]
    steps = life["steps_lived"]
    if (life["score_addend_mode"] != mode or
        life["effect_score-addend"] != "full" or
        life["learning_intervention"] != "normal" or
        life["genome"] != genome_hash or
        life["manifest"]["world_sha256"] != world_hash or
        life["life_seed"] != seed or life["horizon"] != p5c_schedule.HORIZON or
        not life["manifest_id"] or not life["evidence_head"] or
        not life["trace_head"] or
        type(steps) is not int or not 1 <= steps <= p5c_schedule.HORIZON or
        len(trace) != steps):
        raise RuntimeError("P5c opportunity, source or trace mismatch")
    censored = life["terminal"] == "censored"
    if (life["terminal"] not in ("dead", "censored") or
        censored != (steps == p5c_schedule.HORIZON and
                     not life["death_causes"]) or
        ((not censored) and not life["death_causes"])):
        raise RuntimeError("invalid death/censored outcome")
    if (acc["status"] != "SETTLED_FOR_DECLARED_WORK" or
        acc["shortfall_steps"] or acc["pending_replays"] or
        abs(acc["pending_energy"]) > TOL or
        abs(acc["pending_vigilance"]) > TOL or
        life["shadow_discarded_outcome_updates"] != 0 or
        life["retained_outcome_learning_updates"] != acc["learning_updates"]):
        raise RuntimeError("incorrect paid learning/accounting")
    paid = {p: {ch: 0.0 for ch in CHANNELS} for p in PHASES}
    work = {p: {w: 0 for w in WORK} for p in PHASES}
    events = {"no_processing_budget": 0, "no_funded_score": 0,
              "control_rejected": 0, "action_admitted": 0}
    observed_replays = 0
    early = []
    for i, row in enumerate(trace):
        if row["t"] != i + 1 or (row["dead"] and i != steps - 1):
            raise RuntimeError("out-of-order or postmortem work")
        phases = row["funding_phases"]
        obs = row["info"]["observer"]
        state = obs["decision_outcome"]
        if state not in events:
            raise RuntimeError("unexpected decision state")
        events[state] += 1
        if (len(obs["score_witness"]) != obs["scored_options"] or
            len(obs["pre_body"]) != 5 or
            sum(obs["offered_families"].values()) != obs["offered_options"] or
            sum(obs["scored_families"].values()) != obs["scored_options"]):
            raise RuntimeError("observer reported unpaid/fictitious candidate")
        for item in obs["score_witness"]:
            if (abs(item["base_return"] +
                    item["curiosity_bonus_applied"] +
                    item["risk_penalty_applied"] -
                    item["total_score"]) > TOL or
                abs(item["curiosity_bonus_applied"] +
                    item["risk_penalty_applied"] -
                    item["curiosity_risk_bonus"]) > TOL or
                item["curiosity_bonus_computed"] < -TOL or
                item["risk_penalty_computed"] > TOL or
                abs(item["curiosity_bonus_applied"] -
                    (0.0 if mode in ("discard_curiosity_bonus",
                                     "discard_both_bonus_terms")
                     else item["curiosity_bonus_computed"])) > TOL or
                abs(item["risk_penalty_applied"] -
                    (0.0 if mode in ("discard_risk_penalty",
                                     "discard_both_bonus_terms")
                     else item["risk_penalty_computed"])) > TOL or
                not 0.0 <= item["uncertainty"] <= 1.0 or
                item["first_forecast"] is None):
                raise RuntimeError("unearned or malformed prospective score")
        for phase in PHASES:
            counters = phases[phase]["work"]
            if set(counters) != set(WORK):
                raise RuntimeError("wrong work schema")
            for key in WORK:
                if type(counters[key]) is not int or counters[key] < 0:
                    raise RuntimeError("non-integer executed cognitive work")
                work[phase][key] += counters[key]
            for ch in CHANNELS:
                bill = phases[phase]["accounting"][ch]
                if (bill["unpaid"] > TOL or
                    abs(bill["requested"] - bill["paid"]) > TOL or
                    bill["paid"] < -TOL):
                    raise RuntimeError("unpaid or forged phase work")
                paid[phase][ch] += bill["paid"]
        if row["dead"] and any(phases["learning"]["work"].values()):
            raise RuntimeError("learning after physical death")
        observed_replays += phases["learning"]["work"]["replays"]
        if i < p5c_schedule.MECHANISTIC_WINDOW:
            early.append({
                "t": row["t"], "action": row["action"], "param": row["param"],
                "pre_body": obs["pre_body"],
                "funding": row["info"]["funding"],
                "scores": [
                    {"option": w["option"], "base_return": w["base_return"],
                     "curiosity_calculated": w["curiosity_bonus_computed"],
                     "risk_calculated": w["risk_penalty_computed"],
                     "curiosity_applied": w["curiosity_bonus_applied"],
                     "risk_applied": w["risk_penalty_applied"],
                     "bonus": w["curiosity_risk_bonus"], "score": w["total_score"]}
                    for w in obs["score_witness"]],
            })
    if observed_replays != acc["replays_executed"] or sum(events.values()) != steps:
        raise RuntimeError("missing observer events or paid replays")
    for ch in CHANNELS:
        total = acc["totals"][ch]
        if (abs(total["unpaid"]) > TOL or
            abs(total["requested"] - total["paid"]) > TOL or
            abs(sum(paid[p][ch] for p in PHASES) - total["paid"]) > TOL):
            raise RuntimeError("actual phase charges disagree with life receipt")
    for status, n in events.items():
        if n != life["observer_decision_diagnostics"][status]:
            raise RuntimeError("observer aggregate differs from trace")
    return {
        "population": population, "arm": arm, "slot": slot,
        "family": family, "repeat": repeat, "mode": mode,
        "validation_world_index": index, "life_seed": seed,
        "world_sha256": world_hash, "genome_sha256": genome_hash,
        "source_sha256": life["manifest"]["source"]["sha256"],
        "manifest_id": life["manifest_id"], "trace_head": life["trace_head"],
        "evidence_head": life["evidence_head"],
        "terminal": life["terminal"], "censored": censored,
        "death_causes": life["death_causes"], "steps_lived": steps,
        "inactive_steps": acc["inactive_steps"],
        "paid": {ch: acc["totals"][ch]["paid"] for ch in CHANNELS},
        "phase_paid": paid, "phase_work": work,
        "learning_computations": acc["learning_updates"],
        "replays_executed": acc["replays_executed"],
        "decision_status": events, "early_witness": early,
        "outcome_model_sha256": life["outcome_model_sha256"],
        "spatial_beliefs_sha256": life["spatial_beliefs_sha256"],
    }


def _early_pair(full: dict, intervention: dict) -> dict:
    """Compare paid common options before first action divergence only.

    A matching body is NOT enough to assert identical hidden mind state.
    This mechanism score-addend is descriptive and cannot by itself establish
    a controlled information-only causal contrast.
    """
    first_action = first_score = first_base = None
    common_preaction_steps = 0
    a, b = full["early_witness"], intervention["early_witness"]
    for i in range(min(len(a), len(b))):
        left, right = a[i], b[i]
        if left["pre_body"] == right["pre_body"]:
            common_preaction_steps += 1
            aa = {item["option"]: item for item in left["scores"]}
            bb = {item["option"]: item for item in right["scores"]}
            for option in sorted(aa.keys() & bb.keys()):
                if first_score is None and abs(aa[option]["score"] - bb[option]["score"]) > 1e-9:
                    first_score = i + 1
                if first_base is None and abs(aa[option]["base_return"] - bb[option]["base_return"]) > 1e-9:
                    first_base = i + 1
        if (left["action"], left["param"]) != (right["action"], right["param"]):
            first_action = i + 1
            break
    if first_action is None:
        if len(a) != len(b):
            first_action = min(len(a), len(b)) + 1
        elif len(a) == p5c_schedule.MECHANISTIC_WINDOW:
            first_action = None  # censored at 12-step diagnostic window
    return {
        "first_action_difference_within_window": first_action,
        "first_shared_option_score_difference_before_action": first_score,
        "first_shared_option_base_return_difference_before_action": first_base,
        "matched_preaction_body_steps": common_preaction_steps,
    }


def run() -> dict:
    schedule, genotypes = _preflight()
    receipts, source_hashes, world_hashes = [], set(), set()
    for allocation in schedule["exposure"]:
        p, fam, repeat = (allocation["population"], allocation["family"],
                          allocation["repeat"])
        index, seed = allocation["index"], allocation["life_seed"]
        # First exposure is below all preregistration gates.
        spec = p2_ecologies.world_for(fam, "validation", index)
        world_hash = digest(world_snapshot(spec))
        world_hashes.add(world_hash)
        for arm in p5c_schedule.ARMS:
            for slot in range(p5c_schedule.GENOTYPES):
                gene = genotypes[(p, arm, slot)]
                for mode in MODES:
                    life = run_life(
                        gene["genome"], spec, seed, p5c_schedule.HORIZON,
                        protocol=PROTOCOL, keep_trace=True, learning_mode="normal",
                        effect_score-addend="full", score_addend_mode=mode,
                        observer_mind_digest=True,
                        observer_decision_diagnostics=True)
                    receipts.append(_receipt(
                        life, mode=mode, population=p, arm=arm, slot=slot,
                        family=fam, repeat=repeat, index=index, seed=seed,
                        world_hash=world_hash, genome_hash=gene["genome_sha256"]))
                    source_hashes.add(receipts[-1]["source_sha256"])
    if (len(receipts) != p5c_schedule.LIVES or
        len(source_hashes) != 1 or len(world_hashes) != 24):
        raise RuntimeError("incomplete or cross-source P5c evidence")
    raw = {
        "schema": PROTOCOL, "source_sha": _source_sha(),
        "schedule_sha256": schedule["sha256"],
        "frozen_g2_sha256": p5c_schedule.p4a_schedule.G2_CANONICAL_SHA256,
        "status": "P5C_SCORE_ADDENDS_HELDOUT_NO_RESERVE",
        "total_lives": len(receipts), "lives": receipts,
    }
    raw["sha256"] = sha256(json.dumps(
        raw, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return raw


def summarize(raw: dict) -> dict:
    """Preregistered primary n=4 survival and descriptive pre-choice signal."""
    populations = []
    people = raw["lives"]
    for p in range(p5c_schedule.POPULATIONS):
        modes = {}
        for mode in MODES:
            rows = [x for x in people if x["population"] == p and x["mode"] == mode]
            if len(rows) != 72:
                raise ValueError("missing independent population/mode lives")
            modes[mode] = {
                "censored": sum(x["censored"] for x in rows),
                "dead": sum(not x["censored"] for x in rows),
                "lived_steps": sum(x["steps_lived"] for x in rows),
                "inactive_steps": sum(x["inactive_steps"] for x in rows),
                "paid": {ch: round(sum(x["paid"][ch] for x in rows), 7)
                         for ch in CHANNELS},
                "phase_paid": {phase: {
                    ch: round(sum(x["phase_paid"][phase][ch] for x in rows), 7)
                    for ch in CHANNELS} for phase in PHASES},
                "decision_status": {status: sum(x["decision_status"][status] for x in rows)
                                    for status in ("no_processing_budget", "no_funded_score",
                                                   "control_rejected", "action_admitted")},
            }
        populations.append({
            "population": p, "modes": modes,
            "contrasts": {mode: modes["normal"]["censored"] - modes[mode]["censored"]
                          for mode in MODES[1:]},
        })
    differences = {mode: [p["contrasts"][mode] for p in populations]
                   for mode in MODES[1:]}
    raw_p = {mode: p5a_screen._two_sided_sign_flip_p(v)
             for mode, v in differences.items()}
    adjusted = p5a_screen._holm_adjust(raw_p)
    contrasts = {}
    for mode, values in differences.items():
        mean = sum(values) / len(values)
        from math import sqrt
        sd = sqrt(sum((v-mean)**2 for v in values)/3)
        margin = 3.182446305 * sd / 2
        contrasts[mode] = {
            "population_differences_lives_per_72": values,
            "mean_lives_per_population_of_72": mean,
            "exploratory_95pct_t_interval": [mean-margin, mean+margin],
            "exact_two_sided_sign_flip_p": raw_p[mode],
            "exploratory_holm_p": adjusted[mode],
        }
    pairing = {}
    for x in people:
        k = (x["population"], x["arm"], x["slot"], x["family"], x["repeat"])
        row = pairing.setdefault(k, {})
        if x["mode"] in row:
            raise ValueError("duplicated paired mode")
        row[x["mode"]] = x
    if len(pairing) != 288:
        raise ValueError("incomplete paired study")
    mechanistic = {mode: [] for mode in MODES[1:]}
    for modes in pairing.values():
        if set(modes) != set(MODES):
            raise ValueError("missing score-addend arm")
        first = modes["normal"]
        for mode in MODES[1:]:
            other = modes[mode]
            if (first["world_sha256"], first["genome_sha256"], first["life_seed"]) != (
                    other["world_sha256"], other["genome_sha256"], other["life_seed"]):
                raise ValueError("mismatched experimental opportunity")
            mechanistic[mode].append(_early_pair(first, other))
    mechanisms = {}
    for mode, pairs in mechanistic.items():
        mechanisms[mode] = {
            "pairs": len(pairs),
            "pairs_with_preaction_common_option_score_change": sum(
                x["first_shared_option_score_difference_before_action"] is not None
                for x in pairs),
            "pairs_with_preaction_common_option_base_return_change": sum(
                x["first_shared_option_base_return_difference_before_action"] is not None
                for x in pairs),
            "pairs_with_action_change_in_window": sum(
                x["first_action_difference_within_window"] is not None for x in pairs),
            "first_score_divergence_steps": [
                x["first_shared_option_score_difference_before_action"] for x in pairs],
            "first_action_divergence_steps": [
                x["first_action_difference_within_window"] for x in pairs],
            "epistemic_limit": "matched_body_not_matched_hidden_state",
        }
    return {
        "schema": PROTOCOL, "source_sha": raw["source_sha"],
        "schedule_sha256": raw["schedule_sha256"],
        "original_sha256": raw["sha256"],
        "total_lives": raw["total_lives"],
        "populations": populations, "contrasts": contrasts,
        "mechanistic": mechanisms,
        "interpretation": "exploratory_n4_addend_retention_with_downstream_energy_mediation_no_GO",
    }


if __name__ == "__main__":
    if sys.argv[1:] == ["--preflight"]:
        allocation = p5c_schedule.manifest()
        genes = p4a_validation.verify_frozen_genomes()
        print(json.dumps({
            "protocol": PROTOCOL, "status": "NO_P5B_VALIDATION_WORLD_OPENED",
            "allocation_sha256": allocation["sha256"],
            "worlds": len(allocation["exposure"]),
            "genomes": len(genes), "planned_lives": allocation["lives"],
            "modes": list(MODES)}, sort_keys=True, indent=2))
    elif len(sys.argv) == 3 and sys.argv[1] == "--run":
        target = Path(sys.argv[2])
        if target.exists():
            raise FileExistsError("never overwrite P5c original evidence")
        result = run()
        target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        print(json.dumps(summarize(result), indent=2, sort_keys=True))
    else:
        raise SystemExit("usage: python -m i3.lab.p5c_heldout --preflight | --run ORIGINAL.json")
