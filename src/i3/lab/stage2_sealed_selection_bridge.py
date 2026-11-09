"""Read-only Stage-2.1 sealed selection -> validation preflight, NO World.

The two-phase generator already exists. This module only verifies archives
against EXTERNALLY SUPPLIED expected digests and fixed F0 cell identities.
A caller may forge all pins: equality is NOT independent owner attestation,
scientific source authorization, statistical validity or permission to run.
"""
from __future__ import annotations

from collections.abc import Mapping
from hashlib import sha256
import json
from math import isfinite
from pathlib import Path

from . import stage0_design as F0
from . import stage2_finite_panel as PANEL
from . import two_phase_panel as TP

LOCK_SCHEMA = "i3-stage2-1-selected-sealed-preflight/v1"
STATUS = "MATCHES_CALLER_SUPPLIED_DIGEST_PINS_ONLY"
PIN_KEYS = frozenset(("manifest_sha256", "source_sha", "plan_sha256",
                      "transport_fingerprint"))
SELECTION_KEYS = frozenset(("cohort", "population", "family", "world_index",
                            "world_seed", "genome_seed", "life_seed", "policy"))
VALIDATION_KEYS = (SELECTION_KEYS - {"policy"}) | {"condition"}
POLICIES = {
    "FIXED": "reference",
    "GATE": "p13_replay_gate_v1",
    "FIXED_on_FIXED_selected": "reference",
    "GATE_on_GATE_selected": "p13_replay_gate_v1",
    "FIXED_on_GATE_selected": "reference",
    "RANDOM_on_GATE_selected": "p13_replay_gate_random_equal_mean_v1",
    "ZERO_PERCEIVED_COST_on_GATE_selected": "p13_replay_gate_zero_perceived_cost_v1",
}


def _hex(value, n):
    return type(value) is str and len(value) == n and all(c in "0123456789abcdef" for c in value)


def _pins(pins):
    if not isinstance(pins, Mapping) or set(pins) != PIN_KEYS:
        raise ValueError("all four independent expected digest/source pins required")
    if not (_hex(pins["source_sha"], 40) and all(
            _hex(pins[k], 64) for k in PIN_KEYS - {"source_sha"})):
        raise ValueError("invalid expected source/digest pin")


def _sealed(archive_dir, plan_path, pins, cohort, count):
    """Only read sealed evidence, never mint tickets or construct WorldSpecs."""
    _pins(pins)
    root = Path(archive_dir)
    plan = Path(plan_path)
    if not root.is_dir() or root.is_symlink() or plan.is_symlink():
        raise ValueError("regular archive directory and plan required")
    if sha256(plan.read_bytes()).hexdigest() != pins["plan_sha256"]:
        raise ValueError("source-pinned plan bytes mismatch")
    for name in ("MANIFEST.json", "MANIFEST.sha256", "SOURCE_LOCK.json"):
        if (root / name).is_symlink() or not (root / name).is_file():
            raise ValueError("missing or symlinked sealed custody file")
    body = (root / "MANIFEST.json").read_bytes()
    if sha256(body).hexdigest() != pins["manifest_sha256"]:
        raise ValueError("expected manifest pin mismatch")
    if (root / "MANIFEST.sha256").read_text().strip() != pins["manifest_sha256"]:
        raise ValueError("self-seal differs from prospective manifest pin")
    lock = json.loads((root / "SOURCE_LOCK.json").read_bytes())
    expected_lock = {
        "schema": LOCK_SCHEMA, "cohort": cohort, "planned": count,
        "generated": count, "no_retry": True, **dict(pins),
    }
    if type(lock) is not dict or lock != expected_lock:
        raise ValueError("source lock differs from caller-supplied expected anchors")
    manifest = json.loads(body)
    if (type(manifest) is not dict or set(manifest) !=
            {"schema", "status", "planned", "generated", "files", "failure"} or
            manifest["schema"] != TP.SCHEMA or manifest["status"] != "GENERATED" or
            type(manifest["planned"]) is not int or manifest["planned"] != count or
            type(manifest["generated"]) is not int or manifest["generated"] != count or
            manifest["failure"] is not None or type(manifest["files"]) is not list or
            len(manifest["files"]) != count):
        raise ValueError("incomplete, failed or noncanonical phase G")
    filenames = set()
    for i, entry in enumerate(manifest["files"]):
        name = f"life-{i:03d}.json.gz"
        if (type(entry) is not dict or set(entry) !=
                {"file", "sha256", "uncompressed_sha256", "identity"} or
                entry["file"] != name or
                not _hex(entry["sha256"], 64) or
                not _hex(entry["uncompressed_sha256"], 64) or
                not isinstance(entry["identity"], Mapping)):
            raise ValueError("invalid original entry, filename or order")
        path = root / name
        if not path.is_file() or path.is_symlink():
            raise ValueError("missing or symlinked original")
        filenames.add(name)
    if {p.name for p in root.glob("life-*.json.gz")} != filenames:
        raise ValueError("undeclared or extra original file")
    # TP.load_sealed verifies every original packed/uncompressed SHA and
    # embedded identity. It never invokes a scientific runner.
    records = list(TP.load_sealed(root))
    if len(records) != count:
        raise ValueError("missing verified originals")
    return records


def _identity(identity, world, keys, cohort):
    if (not isinstance(identity, Mapping) or set(identity) != keys or
            identity["cohort"] != cohort or
            any(type(identity[k]) is not int for k in (
                "population", "world_index", "world_seed", "genome_seed", "life_seed")) or
            identity["population"] != world["population"] or
            identity["family"] != world["family"] or
            identity["world_index"] != world["index"] or
            identity["world_seed"] != world["world_seed"] or
            identity["life_seed"] != world["life_seed"]):
        raise ValueError("identity fails fixed F0 population/world/seed allocation")


def _actual_life(identity, life, policy, pins, seen_genomes, seen_worlds):
    """Verify observable full-life fields and cross-arm genotype/world parity."""
    if not isinstance(life, Mapping):
        raise ValueError("original payload has no life mapping")
    n = life.get("steps_lived")
    terminal = life.get("terminal")
    if (type(n) is not int or not 1 <= n <= F0.HORIZON or
            terminal not in ("dead", "censored") or
            (terminal == "censored" and n != F0.HORIZON) or
            life.get("horizon") != F0.HORIZON or
            type(life.get("life_seed")) is not int or
            life["life_seed"] != identity["life_seed"]):
        raise ValueError("invalid or missing death/censoring original life")
    if (type(life.get("world")) is not str or not life["world"] or
            not isinstance(life.get("manifest"), Mapping)):
        raise ValueError("missing World or manifest")
    world_hash = life["manifest"].get("world_sha256")
    genome_hash = life.get("genome")
    if not _hex(world_hash, 64) or not _hex(genome_hash, 64):
        raise ValueError("missing original world/genome digest")
    world_key = (identity["cohort"], identity["world_index"])
    if world_key in seen_worlds and seen_worlds[world_key] != (
            life["world"], world_hash):
        raise ValueError("world digest/name drift inside paired cohort")
    seen_worlds[world_key] = (life["world"], world_hash)
    seed = identity["genome_seed"]
    if seed in seen_genomes and seen_genomes[seed] != genome_hash:
        raise ValueError("genome digest changed across paired originals")
    seen_genomes[seed] = genome_hash
    actual_policy = life["manifest"].get("experimental_policy", {}).get("name", "reference")
    if actual_policy != policy:
        raise ValueError("original policy differs from declared identity")
    ticket = life.get("admission_receipt")
    if (not isinstance(ticket, Mapping) or
            ticket.get("cohort") != identity["cohort"] or
            ticket.get("world_name") != life["world"] or
            ticket.get("world_sha256") != world_hash or
            ticket.get("transport_fingerprint") != pins["transport_fingerprint"] or
            type(ticket.get("world_seed")) is not int or
            ticket["world_seed"] != identity["world_seed"]):
        raise ValueError("original ticket is not bound to declared World")
    ca = life.get("cognitive_accounting")
    if (not isinstance(ca, Mapping) or
            ca.get("status") != "SETTLED_FOR_DECLARED_WORK" or
            type(ca.get("shortfall_steps")) is not int or ca["shortfall_steps"] != 0 or
            not isinstance(ca.get("totals"), Mapping)):
        raise ValueError("unsettled or absent cognitive account")
    for resource in ("energy", "vigilance"):
        ch = ca["totals"].get(resource)
        if not isinstance(ch, Mapping):
            raise ValueError("missing real paid cognitive channel")
        for field in ("paid", "unpaid"):
            v = ch.get(field)
            if type(v) not in (float, int) or not isfinite(v) or v < 0:
                raise ValueError("invalid actual cognitive account")
        if ch["unpaid"] > 1e-12:
            raise ValueError("unpaid cognitive work")
    if type(ca.get("replays_executed")) is not int or ca["replays_executed"] < 0:
        raise ValueError("invalid original replays")
    if (type(ca.get("inactive_steps")) is not int or
            not 0 <= ca["inactive_steps"] <= n):
        raise ValueError("invalid original inactive time")
    actions = life.get("actions")
    if not isinstance(actions, Mapping):
        raise ValueError("missing lived action counts")
    sleep = actions.get("dormir", 0)
    if type(sleep) is not int or not 0 <= sleep <= n:
        raise ValueError("invalid actual sleep count")
    if ca["replays_executed"] > 16 * sleep:
        raise ValueError("replays exceed lived sleep capacity")
    return sleep, ca


def selection_from_originals(archive_dir, plan_path, pins):
    """Rank both architectures from exactly 3840 complete sealed originals."""
    count = F0.POPULATIONS * F0.CANDIDATES * F0.WORLDS_PER_POPULATION * 2
    originals = _sealed(archive_dir, plan_path, pins, "selection", count)
    worlds = {r["index"]: r for r in F0.world_rows("selection")}
    expected = {(arm, w["population"], w["index"], F0.founder_seed(w["population"], j))
                for w in worlds.values() for arm in ("FIXED", "GATE")
                for j in range(F0.CANDIDATES)}
    outcomes = {(arm, p): [] for arm in ("FIXED", "GATE") for p in range(F0.POPULATIONS)}
    seen, genomes, world_hashes = set(), {}, {}
    for identity, life in originals:
        if not isinstance(identity, Mapping):
            raise ValueError("missing original identity")
        arm = identity.get("policy")
        p, index, seed = (identity.get(k) for k in
                          ("population", "world_index", "genome_seed"))
        if (arm not in ("FIXED", "GATE") or
                any(type(x) is not int for x in (p, index, seed))):
            raise ValueError("unrecognized original selection arm/ID")
        key = (arm, p, index, seed)
        if key not in expected or key in seen:
            raise ValueError("duplicate or foreign selection life")
        _identity(identity, worlds[index], SELECTION_KEYS, "selection")
        _actual_life(identity, life, POLICIES[arm], pins, genomes, world_hashes)
        seen.add(key)
        outcomes[(arm, p)].append({
            "candidate_seed": seed, "world_index": index,
            "terminal": life["terminal"], "steps_lived": life["steps_lived"]})
    if seen != expected:
        raise ValueError("incomplete original selection receipts")
    selected = {
        arm: {p: F0.rank_candidates(p, outcomes[(arm, p)])
              for p in range(F0.POPULATIONS)}
        for arm in ("FIXED", "GATE")
    }
    PANEL.selected_founders(selected)
    return {
        "selected": selected,
        "genome_digests_by_birth_seed": genomes,
        "source_custody": STATUS,
        "selection_originals": count,
        "selected_rank_source": "FULL_SEALED_ORIGINAL_OUTCOMES",
        "scientific_verdict": "NOT_ISSUED",
        "world_opening_authorized": False,
    }


def readout_from_originals(selection_archive, selection_plan, selection_pins,
                           validation_archive, validation_plan, validation_pins):
    """Read and reduce 1200 sealed validation originals after actual selection.

    Digests are compared to caller-provided pins. Their independent custody,
    population independence and the prospective owner's approval remain
    OUTSIDE this module and cannot be inferred from its result.
    """
    selection = selection_from_originals(
        selection_archive, selection_plan, selection_pins)
    selected = selection["selected"]
    expected = PANEL.expected_cells(selected)
    originals = _sealed(validation_archive, validation_plan, validation_pins,
                        "validation", len(expected))
    worlds = {r["index"]: r for r in F0.world_rows("validation")}
    rows, seen, world_hashes = [], set(), {}
    genomes = dict(selection["genome_digests_by_birth_seed"])
    for identity, life in originals:
        if not isinstance(identity, Mapping):
            raise ValueError("missing validation identity")
        condition = identity.get("condition")
        p, index, seed = (identity.get(k) for k in
                          ("population", "world_index", "genome_seed"))
        if (condition not in PANEL.CONDITIONS or
                any(type(x) is not int for x in (p, index, seed))):
            raise ValueError("invalid validation condition/cell")
        key = (condition, p, index, seed)
        if key not in expected or key in seen:
            raise ValueError("duplicate/foreign/unselected validation life")
        _identity(identity, worlds[index], VALIDATION_KEYS, "validation")
        sleep, ca = _actual_life(
            identity, life, POLICIES[condition], validation_pins, genomes,
            world_hashes)
        random = condition == "RANDOM_on_GATE_selected"
        if random:
            gate = life.get("replay_gate")
            schedule = gate.get("random_schedule") if isinstance(gate, Mapping) else None
            if not isinstance(schedule, Mapping):
                raise ValueError("RANDOM lacks actual paid draw receipts")
            keys = ("draws_funded", "nominal_replays_scheduled",
                    "eligible_replays_scheduled", "actual_replays_paid",
                    "lived_sleep_ordinals")
            if any(type(schedule.get(k)) is not int for k in keys):
                raise ValueError("invalid RANDOM actual draw receipts")
            if (schedule["actual_replays_paid"] != ca["replays_executed"] or
                    schedule["lived_sleep_ordinals"] > sleep or
                    schedule["draws_funded"] > schedule["lived_sleep_ordinals"] or
                    schedule.get("mean_numerator") != 5532 or
                    schedule.get("mean_denominator") != 867):
                raise ValueError("RANDOM funding or frozen mean mismatch")
        else:
            schedule = None
            if isinstance(life.get("replay_gate"), Mapping) and (
                    "random_schedule" in life["replay_gate"]):
                raise ValueError("non-RANDOM original contains RANDOM schedule")
        seen.add(key)
        rows.append({
            **{k: identity[k] for k in (
                "condition", "population", "family", "world_index",
                "world_seed", "genome_seed", "life_seed")},
            "terminal": life["terminal"], "steps_lived": life["steps_lived"],
            "cognitive_energy_paid": ca["totals"]["energy"]["paid"],
            "cognitive_vigilance_paid": ca["totals"]["vigilance"]["paid"],
            "inactive_steps": ca["inactive_steps"], "sleep_steps": sleep,
            "replays_paid": ca["replays_executed"],
            "random_draws": schedule["draws_funded"] if random else 0,
            "random_nominal_replays": (
                schedule["nominal_replays_scheduled"] if random else 0),
            "random_eligible_replays": (
                schedule["eligible_replays_scheduled"] if random else 0),
        })
    if seen != set(expected):
        raise ValueError("missing validation originals")
    out = PANEL.reduce_finite_panel(selected, rows)
    return {
        "status": STATUS,
        "selection_originals_checked": selection["selection_originals"],
        "validation_originals_checked": len(rows),
        "selected_rank_source": selection["selected_rank_source"],
        "selected": selected,
        "readout": out,
        "original_custody": "MATCHES_SUPPLIED_PINS_NOT_INDEPENDENTLY_AUTHENTICATED",
        "scientific_verdict": "NOT_ISSUED",
        "scientific_worlds_opened": False,
        "owner_authorization_inferred": False,
        "population_independence_established": False,
    }
