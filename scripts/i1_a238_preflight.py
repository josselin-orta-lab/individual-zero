"""A2.38 prebirth lock. This module creates no I1 individuals."""
from __future__ import annotations

from hashlib import sha1, sha256
import json
from pathlib import Path

from i1_a238_fixtures import ARMS, STRATA, COSTS, LOCK_SHA, TRAIN_SHA, references, world_case
from i1_a238_model import sealed_model

ROOT = Path(__file__).resolve().parents[1]
PREREG_BLOB = "772cae150ac3d8a638f647ac176180bd35f23f1b"
MAIN_ANCHOR = "bf59eceaf97805f04a18b0b28f1396f2e98bfa89"
ORDER = ("BASE", "ALTERNATE_NEED", "BOUNDED_MOVE", "BOTH")
GROUPS = ("BLOCKED_THIRST_LOCAL_BERRY", "WATER_LOCAL_BERRY_E_SAFE",
          "WATER_LOCAL_BERRY_E_INVISIBLE_LETHAL", "MIXED_NEEDS_KNOWN_SAFE",
          "MIXED_NEEDS_CHANGED_INVISIBLE_LETHAL")


def blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def digest(value) -> str:
    from i1lab.determinism import canonical_causal_bytes
    return sha256(canonical_causal_bytes(value)).hexdigest()


def birth_order():
    return [(stratum, index, arm)
            for stratum in GROUPS for index in range(8)
            for arm in (ORDER if index % 2 == 0 else ORDER[::-1])]


def life_id(stratum: str, index: int, arm: str) -> str:
    return f"i1:a238:{stratum}:{index:02d}:{arm}"


def preflight(output: Path, *, source_sha: str):
    """Fail closed before any A2.38 birth, including the first."""
    from i1lab.world import WorldBody
    if (type(source_sha) is not str or len(source_sha) != 40
            or any(c not in "0123456789abcdef" for c in source_sha)):
        raise ValueError("source commit must be a full lowercase SHA")
    if (ARMS != ORDER or STRATA != GROUPS or LOCK_SHA !=
            "e1f276ffdc086c80a0360c3df7bd60fc2b7652dd"
            or TRAIN_SHA !=
            "7c5e9634090741aff5d7b3110f888b9d81a11b978e349463d66b4cc5d4f97551"):
        raise RuntimeError("A2.38 protocol symbols diverged from locked allocation")
    prereg = ROOT / "docs/research/i1-a238-goal-starvation-bounded-exploration-prereg-2026-10-16.en.md"
    lock = ROOT / "docs/research/i1-a238-input-lock-v1-2026-10-16.en.md"
    if blob_sha(prereg) != PREREG_BLOB or blob_sha(lock) != LOCK_SHA:
        raise RuntimeError("A2.38 preregistration or numerical input lock was modified")
    cost_ref = dict(se_deplacer=2.0, collecter=1.0, manger=0.5, boire=0.5,
                    attendre=0.35, dormir=0.25, poser_une_pierre=1.5,
                    fabriquer_outil=1.5)
    if COSTS != cost_ref:
        raise RuntimeError("A2.38 energy prices changed after preregistration")
    # Reexecute the external PHYSICAL training and build the actual I1 model
    # from its deltas. A matching annotation alone is not a model.
    model, seal = sealed_model(output)
    if model.corpus_sha256 != TRAIN_SHA or model.source_scope != "external_lab":
        raise RuntimeError("wrong sealed external model")
    s11, c11, c10, policy = references()
    birth_rows = []
    for stratum, i, arm in birth_order():
        physics, layout, configured, events, east = world_case(s11, c11, stratum, i)
        expected_origin = (6 + i % 4, 6 + i // 4)
        if ((physics.initial_position.x, physics.initial_position.y) != expected_origin
                or physics.initial_body.as_dict() != {
                    "energy": float(64+i%2), "food": float(13+i%4),
                    "water": float(18+i%3), "integrity": 100.0}
                or physics.action_energy_costs != cost_ref
                or physics.food_decay_per_step != .20
                or physics.water_decay_per_step != .40
                or physics.drink_water_gain != 40.0
                or physics.sleep_energy_gain != 0.0
                or physics.rest_integrity_gain != 0.0
                or physics.danger_zone_damage != 10.0
                or physics.creature_damage != 0.0
                or physics.berry_effects["berry_b"].food_gain != 6
                or physics.berry_effects["berry_a"].integrity_delta != -100
                or physics.width != 32 or physics.height != 32
                or physics.day_steps != 300 or physics.night_steps != 100
                or physics.night_start_step != 200
                or bool(configured.geographic) != (stratum in GROUPS[3:])
                or (len(events) != 1) != (stratum == GROUPS[4])):
            raise RuntimeError(f"physical input mismatch {stratum}/{i}")
        if stratum == GROUPS[4] and (events[0].t_monde != 9 or
                                    events[0].operation != "set_lethal_zone"):
            raise RuntimeError("unregistered external event")
        physics.validate()
        layout.validate(physics)
        birth_rows.append({
            "ordinal": len(birth_rows), "life_id": life_id(stratum, i, arm),
            "stratum": stratum, "case_index": i, "arm": arm,
            "h1": arm in ("ALTERNATE_NEED", "BOTH"),
            "h2": arm in ("BOUNDED_MOVE", "BOTH"),
            "physical_sha256": digest(physics.as_dict()),
            "layout_sha256_operator_only": digest(layout.as_dict()),
            "external_inputs_sha256_operator_only": digest([e.as_dict() for e in events]),
        })
    ids = [r["life_id"] for r in birth_rows]
    if len(ids) != 160 or len(set(ids)) != 160:
        raise RuntimeError("not exactly 160 distinct locked birth IDs")
    for j in range(0, 160, 4):
        pair = birth_rows[j:j+4]
        if (len({x["physical_sha256"] for x in pair}) != 1
                or len({x["layout_sha256_operator_only"] for x in pair}) != 1
                or len({x["external_inputs_sha256_operator_only"] for x in pair}) != 1):
            raise RuntimeError("factorial arms do not share physical conditions")
    for i in range(8):
        safe_p, safe_l, _, _, _ = world_case(s11, c11, GROUPS[1], i)
        deadly_p, deadly_l, _, _, _ = world_case(s11, c11, GROUPS[2], i)
        if safe_p.as_dict() != deadly_p.as_dict():
            raise RuntimeError("safe/lethal physical parameter discrepancy")
        safe_view = WorldBody(config=safe_p, layout=safe_l).capture_local(t_monde=1).as_dict()
        lethal_view = WorldBody(config=deadly_p, layout=deadly_l).capture_local(t_monde=1).as_dict()
        if safe_view != lethal_view:
            raise RuntimeError("perceptual leakage between safe and hidden lethal cases")
    manifest = {"schema": "i1-a238-birth-manifest-v1",
                "source_sha": source_sha, "base_main_sha": MAIN_ANCHOR,
                "prereg_blob": PREREG_BLOB, "input_lock_blob": LOCK_SHA,
                "training_corpus_sha256": TRAIN_SHA, "model_version": model.version,
                "max_attempted_world_steps_per_life": 20, "births": birth_rows}
    (output / "birth-manifest.json").write_text(
        json.dumps(manifest, sort_keys=True, indent=2) + "\n")
    pre = {"schema": "i1-a238-preflight-v1", "valid": True,
           "source_sha": source_sha, "birth_count": len(ids),
           "perceptually_indiscernible_pair_cases": 8,
           "factorial_physical_pairings": 40,
           "training": seal, "prereg_blob": PREREG_BLOB,
           "input_lock_blob": LOCK_SHA,
           "birth_manifest_sha256": sha256((output / "birth-manifest.json").read_bytes()).hexdigest()}
    (output / "preflight.json").write_text(
        json.dumps(pre, sort_keys=True, indent=2) + "\n")
    return model, s11, c11, c10, policy, manifest, pre
