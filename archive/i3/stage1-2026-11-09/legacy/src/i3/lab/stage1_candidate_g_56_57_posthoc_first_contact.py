"""Stage-1 Candidate-G 56/57: read-only first-contact audit; never runs a life.

Reduces only the immutable 56/57 originals (36 gzip lives plus cases.json)
after checking every SHA-256 against the archive's own SHA256.json and
cases.json. It reads already-paid option scores from the external
full-competition witness and the archived behavior summaries.

No Mind, World, replay, counterfactual score or new decision is computed.
The only module import is the pure genome constructor, used to verify each
archived genome digest and to read that genome's own water threshold.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from hashlib import sha256
import gzip
import json
from math import isfinite
from pathlib import Path
from statistics import median
import sys

from i3.modules.genome import digest, generation_zero

SCHEMA = "i3-stage1-candidate-g-56-57-posthoc-first-contact/v1"
EXECUTION_SHA = "6ce6fbc2025f9f6e6b34b779142f90c10c28a1e0"
EVIDENCE_COMMIT = "22d60edeeef09248a7f7786a4b5e284e4b94ce1b"
EVIDENCE_BRANCH = "evidence/i3-stage1-candidate-g-56-57-6ce6fbc2025f"
EXPECTED_LIVES = 36
ARCHIVE_METADATA = frozenset(
    {"cases.json", "registration.json", "results.json", "source.json"})
ARMS = {
    "reference": "P1.3",
    "personal_recurrence_candidate_g_v1": "Candidate-G",
    "genomic_omega_frontier_information_v1": "Candidate-F",
}
ARM_ORDER = ("P1.3", "Candidate-G", "Candidate-F")
FLAT_SPREAD = 1e-9
POSITIVE_INFORMATION = 1e-12
WATER = 2
POST_CONTACT_WATER_CEILING = 80.0
WITNESS_P13 = ("depletion-57-g901", "reference", 1)
WITNESS_G = ("depletion-57-g901", "personal_recurrence_candidate_g_v1", 3)


def _file_digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def is_water_option(name: str) -> bool:
    return name == "boire" or name.startswith("goto-boire")


def _finite(value, label):
    if type(value) not in (int, float) or not isfinite(value):
        raise ValueError(f"nonfinite archived value: {label}")
    return float(value)


def load_archive(directory):
    """Yield (case, life, genome) only after complete digest and identity checks.

    Every archive-level check runs before the first life is yielded.
    """
    root = Path(directory)
    listed = json.loads((root / "SHA256.json").read_text())
    if type(listed) is not dict or "cases.json" not in listed:
        raise ValueError("archive digest list must cover cases.json")
    for name, expected in sorted(listed.items()):
        if _file_digest(root / name) != expected:
            raise ValueError(f"digest mismatch: {name}")
    registration = json.loads((root / "registration.json").read_text())
    transport = json.loads((root / "TRANSPORT.json").read_text())
    if (registration.get("execution_sha") != EXECUTION_SHA or
            transport.get("execution_sha") != EXECUTION_SHA or
            transport.get("evidence_branch") != EVIDENCE_BRANCH):
        raise ValueError("archive does not belong to the frozen 56/57 execution")
    cases = json.loads((root / "cases.json").read_text())
    if type(cases) is not list or len(cases) != EXPECTED_LIVES:
        raise ValueError("exactly 36 archived cases required")
    files = [case["original_file"] for case in cases]
    if len(set(files)) != len(files):
        raise ValueError("duplicate original file")
    if set(listed) - set(files) != ARCHIVE_METADATA:
        raise ValueError("archive digest list differs from cases and metadata")
    for case in cases:
        if listed.get(case["original_file"]) != case["original_sha256"]:
            raise ValueError(
                f"case digest differs from archive list: {case['original_file']}")
        if case["identity"]["policy"] not in ARMS:
            raise ValueError(f"unknown archived policy: {case['identity']['policy']}")

    for case in cases:
        name = case["original_file"]
        raw = gzip.decompress((root / name).read_bytes())
        if sha256(raw).hexdigest() != case["original_uncompressed_sha256"]:
            raise ValueError(f"uncompressed digest mismatch: {name}")
        payload = json.loads(raw)
        if payload["identity"] != case["identity"]:
            raise ValueError(f"life identity differs from case: {name}")
        genome = generation_zero(case["identity"]["genome_seed"])
        if (digest(genome) != case["energy"]["genome_sha256"] or
                payload["life"]["genome"] != case["energy"]["genome_sha256"]):
            raise ValueError(f"genome digest mismatch: {name}")
        yield case, payload["life"], genome


def projection_label(arm, life, score):
    """Projector that produced an archived score, from archived fields only."""
    if arm == "Candidate-G":
        mode = score.get("decision_projection_mode")
        if mode not in ("reference", "candidate_f"):
            raise ValueError("Candidate-G score without projector witness")
        return mode
    if arm == "Candidate-F":
        mode = life["manifest"]["experimental_policy"]["simulation_mode"]
        if mode != "candidate_f":
            raise ValueError("Candidate-F archive is not candidate_f")
        return mode
    if life["manifest"].get("experimental_policy") is not None:
        raise ValueError("reference archive carries an experimental policy")
    return "reference"


def drink_base_gap(scores):
    """Base value of drinking minus best other base value, or None."""
    by_option = {s["option"]: s for s in scores}
    if "boire" not in by_option or len(by_option) < 2:
        return None
    drink = _finite(by_option["boire"]["base_return"], "boire base")
    other = max(_finite(s["base_return"], "base") for name, s in
                by_option.items() if name != "boire")
    return drink - other


def analyze_archive(directory):
    behavior = defaultdict(lambda: defaultdict(list))
    spread = defaultdict(list)
    explorers = defaultdict(Counter)
    pre_contact = defaultdict(list)
    post_contact = defaultdict(list)
    unsupported_drink = Counter()
    blocks = defaultdict(dict)
    g_lives = []
    witnesses = {}
    lives = 0

    for case, life, genome in load_archive(directory):
        lives += 1
        ident = case["identity"]
        arm = ARMS[ident["policy"]]
        steps_lived = case["energy"]["steps_lived"]
        actions = case["behavior"]["actions"]
        if type(steps_lived) is not int or steps_lived < 1:
            raise ValueError("positive lived steps required")
        steps = life["observer_full_competition"]["steps"]
        if len(steps) != steps_lived:
            raise ValueError("one full-competition witness per lived step required")
        first_drink = life["first_drink_step"]
        if first_drink is not None:
            contact = steps[first_drink - 1]
            if (contact["chosen_option"] != "boire" or
                    contact["physical_action"] != "boire"):
                raise ValueError("first drink step is not an admitted drink")
        theta_water = genome["genes"]["theta.water"]

        b = behavior[arm]
        b["sleep_fraction"].append(actions.get("dormir", 0) / steps_lived)
        b["move_fraction"].append(actions.get("se_deplacer", 0) / steps_lived)
        b["wait_fraction"].append(actions.get("attendre", 0) / steps_lived)
        b["mapped_cells"].append(case["behavior"]["personally_mapped_cells"])
        b["drank_at_least_once"].append(
            int(case["behavior"]["positive_water_uptakes"] > 0))
        b["mean_step_ms"].append(_finite(life["mean_step_ms"], "mean_step_ms"))

        first_water_seen = None
        water_offers = 0
        for k, step in enumerate(steps):
            scores = step.get("paid_option_scores") or []
            names = [s["option"] for s in scores]
            if any(is_water_option(n) for n in names):
                water_offers += 1
                if first_water_seen is None:
                    first_water_seen = k
            if len(scores) >= 2:
                modes = {projection_label(arm, life, s) for s in scores}
                if len(modes) != 1:
                    raise ValueError("incommensurate projectors in one decision")
                base = [_finite(s["base_return"], "base") for s in scores]
                spread[(arm, modes.pop())].append(max(base) - min(base))
            for s in scores:
                if not s["option"].startswith("explorer"):
                    continue
                explorers[arm]["scored"] += 1
                if arm == "P1.3":
                    if (s.get("curiosity_bonus_applied") or 0.0) > 0.0:
                        explorers[arm]["positive_curiosity_applied"] += 1
                elif (s.get("information_value") or 0.0) > POSITIVE_INFORMATION:
                    explorers[arm]["positive_information_value"] += 1
            gap = drink_base_gap(scores)
            if gap is not None:
                water = step["body_before_decision"][WATER]
                drank = step["chosen_option"] == "boire"
                if first_drink is None or k < first_drink:
                    pre_contact[arm].append(gap)
                    if arm == "Candidate-G":
                        drink = next(s for s in scores if s["option"] == "boire")
                        unsupported_drink[(
                            round(drink["first_forecast"]["delta"][WATER], 12),
                            drink["uncertainty"],
                            drink["information_value"],
                            drink["personal_drink_support"])] += 1
                elif water < POST_CONTACT_WATER_CEILING:
                    post_contact[arm].append({
                        "water_minus_genome_theta_water": water - theta_water,
                        "drink_base_gap": gap,
                        "drank": drank,
                    })
            key = (ident["block"], ident["policy"], k)
            if key == WITNESS_P13:
                by = {s["option"]: s for s in scores}
                witnesses["p13_depletion_57_g901_decision_1"] = {
                    "water": step["body_before_decision"][WATER],
                    "genome_theta_water": theta_water,
                    "base_boire": by["boire"]["base_return"],
                    "base_attendre": by["attendre"]["base_return"],
                    "curiosity_applied_boire": by["boire"]["curiosity_bonus_applied"],
                    "curiosity_applied_attendre": by["attendre"]["curiosity_bonus_applied"],
                    "chosen_option": step["chosen_option"],
                }
            if key == WITNESS_G:
                frontier = [s for s in scores
                            if s.get("score_kind") == "frontier_water_expected_distress"]
                best = max(frontier, key=lambda s: s["total_score"])
                drink = next(s for s in scores if s["option"] == "boire")
                witnesses["candidate_g_depletion_57_g901_decision_3"] = {
                    "water": step["body_before_decision"][WATER],
                    "genome_theta_water": theta_water,
                    "best_frontier_option": best["option"],
                    "best_frontier_total": best["total_score"],
                    "best_frontier_information_value": best["information_value"],
                    "boire_total": drink["total_score"],
                    "boire_forecast_water_delta": drink["first_forecast"]["delta"][WATER],
                    "boire_information_value": drink["information_value"],
                    "chosen_option": step["chosen_option"],
                }

        blocks[ident["block"]][arm] = {
            "first_decision_with_water_option": first_water_seen,
            "decisions_with_water_option": water_offers,
            "first_drink_step": first_drink,
            "mapped_cells": case["behavior"]["personally_mapped_cells"],
            "steps_lived": steps_lived,
            "death_causes": case["energy"]["death_causes"],
        }
        if arm == "Candidate-G":
            paid = case["energy"]["paid"]
            active = case["behavior"]["trace_candidate_f_projection_decisions"]
            resting = actions.get("dormir", 0) + actions.get("physical_inactivity", 0)
            g_lives.append({
                "block": ident["block"],
                "information_active_decisions": active,
                "information_active_fraction": active / steps_lived,
                "sleep_plus_inactive_fraction": resting / steps_lived,
                "paid_energy_per_lived_step": paid["energy"] / steps_lived,
                "paid_vigilance_per_lived_step": paid["vigilance"] / steps_lived,
                "positive_water_uptakes": case["behavior"]["positive_water_uptakes"],
            })

    if lives != EXPECTED_LIVES:
        raise ValueError("archive must reduce exactly 36 lives")
    if set(witnesses) != {"p13_depletion_57_g901_decision_1",
                          "candidate_g_depletion_57_g901_decision_3"}:
        raise ValueError("frozen witness decisions missing")

    arms = {}
    for arm in ARM_ORDER:
        b = behavior[arm]
        arms[arm] = {
            "median_sleep_fraction": median(b["sleep_fraction"]),
            "median_move_fraction": median(b["move_fraction"]),
            "median_wait_fraction": median(b["wait_fraction"]),
            "median_mapped_cells": median(b["mapped_cells"]),
            "lives_with_positive_water_uptake": sum(b["drank_at_least_once"]),
            "median_mean_step_ms": median(b["mean_step_ms"]),
            "explorer_options": dict(explorers[arm]),
        }
    spreads = {}
    for (arm, mode), values in sorted(spread.items()):
        spreads[f"{arm}|{mode}"] = {
            "decisions": len(values),
            "median_base_value_spread": median(values),
            "flat_decisions": sum(v < FLAT_SPREAD for v in values),
        }
    pre = {
        arm: {
            "decisions": len(gaps),
            "drink_base_gap_positive": sum(g > 0.0 for g in gaps),
            "max_drink_base_gap": max(gaps),
        } for arm, gaps in sorted(pre_contact.items())
    }
    post = {
        arm: {
            "decisions_below_water_80": len(rows),
            "below_genome_theta_water": sum(
                r["water_minus_genome_theta_water"] < 0.0 for r in rows),
            "drink_base_gap_positive": sum(
                r["drink_base_gap"] > 0.0 for r in rows),
            "rows_sorted_by_need": sorted(
                rows, key=lambda r: r["water_minus_genome_theta_water"]),
        } for arm, rows in sorted(post_contact.items())
    }
    return {
        "schema": SCHEMA,
        "status": "POSTHOC_IMMUTABLE_ORIGINALS_ZERO_NEW_LIVES_NO_REPLAY",
        "execution_sha": EXECUTION_SHA,
        "evidence_branch": EVIDENCE_BRANCH,
        "evidence_commit": EVIDENCE_COMMIT,
        "lives": lives,
        "arms": arms,
        "base_value_spread_by_projector": spreads,
        "on_water_pre_contact": pre,
        "on_water_post_contact": post,
        "candidate_g_unsupported_drink_forecasts": [
            {"water_delta": k[0], "uncertainty": k[1],
             "information_value": k[2], "personal_drink_support": k[3],
             "decisions": n}
            for k, n in sorted(unsupported_drink.items(), key=str)],
        "candidate_g_lives": sorted(g_lives, key=lambda r: r["block"]),
        "water_perception_by_block": {k: blocks[k] for k in sorted(blocks)},
        "witnesses": witnesses,
        "limitations": {
            "design": "12 matched DEVELOPMENT blocks, two G0 genomes; engineering fixtures, not independent populations",
            "counterfactual_scores": "NOT_COMPUTED: no projector swap, no replay of exposed worlds",
            "post_contact_need": "no post-contact on-water decision lies below the genome's own water threshold",
            "use": "exposed 56/57 evidence only; must not tune any rule, seed, threshold or ceiling",
        },
    }


def main(argv):
    if len(argv) != 2:
        raise SystemExit(
            "usage: python -m i3.lab.stage1_candidate_g_56_57_posthoc_first_contact "
            "<evidence-directory>")
    print(json.dumps(analyze_archive(argv[1]), sort_keys=True, indent=2))


if __name__ == "__main__":
    main(sys.argv)
