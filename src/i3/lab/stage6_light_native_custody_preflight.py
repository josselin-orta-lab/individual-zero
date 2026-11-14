"""Read-only Stage-6-light native *shape* and original-custody preflight.

This is NOT a study transport, admission guard, evidence authentication, or
lineage runner. It only inspects immutable I3 two_phase_panel/v1 gzip originals
from an explicitly supplied archive and checks their native life-v2 fields.
There are NO I3 module imports, World construction, seed allocation or births.
No reduction result, persistence score, parent decision, or GO is emitted.

The still-inert Stage-6 method is checked before any archive is opened. The
source and exact case bindings supplied by a caller are untrusted *claims*,
not a proprietor's scientific authorization or an external timestamp.
"""
from __future__ import annotations

from collections import defaultdict
from hashlib import sha256
import gzip
import json
from math import isfinite
from pathlib import Path
import re

STUDY = Path(__file__).resolve().parents[1] / "docs/studies/stage6-light-preparation"
METHOD = STUDY / "STAGE6_LIGHT_PROTOCOL_METHOD_V1.json"
SCHEMA = "i3-two-phase-panel/v1"
PROVENANCE_SCHEMA = "i3-life-manifest/v2"
FUNDING_SCHEMA = "i3-cognitive-funding/v2"
ARMS = ("selected", "random_parent")
FAMILIES = ("stable", "depletion", "pulse")
MAX_ORIGINAL_BYTES = 2_000_000  # fail closed on oversized decompression
MAX_MANIFEST_BYTES = 12_000_000
DIGEST64 = re.compile(r"[0-9a-f]{64}\Z")
FILENAME = re.compile(r"life-[0-9]+\.json\.gz\Z")
GENE_KEYS = (
    *(f"{name}.{channel}" for name in ("theta", "p", "w")
      for channel in ("energy", "food", "water", "integrity", "vigilance")),
    "gamma1", "gamma2", "gamma3", "alpha", "beta_u", "lambda_r",
    "n_base", "h_max", "m_max", "belief_rate",
    *(f"temperament.{name}" for name in (
        "reward_sensitivity", "threat_sensitivity", "exploration",
        "goal_protection", "affiliation")),
    "omega",
)

# Snapshot of the genome-v4 contract: never import mutable runtime biology.
# If genome.py changes, this audited preflight must be explicitly revised.
BOUNDS = {
    **{f"{name}.{channel}": rng
       for name, rng in (("theta", (30.0, 90.0)), ("p", (1.0, 3.0)),
                         ("w", (0.2, 2.0)))
       for channel in ("energy", "food", "water", "integrity", "vigilance")},
    "gamma1": (0.60, 0.90), "gamma2": (0.90, 0.98),
    "gamma3": (0.98, 0.998), "alpha": (0.01, 0.20),
    "beta_u": (0.0, 2.0), "lambda_r": (0.0, 1.0),
    "n_base": (2.0, 8.0), "h_max": (4.0, 24.0),
    "m_max": (32.0, 512.0), "belief_rate": (0.02, 0.50),
    **{f"temperament.{name}": (-1.0, 1.0)
       for name in ("reward_sensitivity", "threat_sensitivity", "exploration",
                    "goal_protection", "affiliation")},
    "omega": (-1.0, 1.0),
}


def _canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def _digest(value: object) -> str:
    return sha256(_canonical(value)).hexdigest()


def _hash(value: object) -> bool:
    return type(value) is str and DIGEST64.fullmatch(value) is not None


def _integer(value: object, lower: int, upper: int) -> bool:
    return type(value) is int and lower <= value <= upper


def _nonnegative(value: object) -> bool:
    return type(value) in (float, int) and isfinite(value) and value >= 0


def _assert_inert() -> dict:
    m = json.loads(METHOD.read_text(encoding="utf-8"))
    if (m.get("schema") != "i3-stage6-light-method-preauth/v1" or
            m.get("status") != "METHOD_FIXED_PREAUTH_NOT_EXECUTABLE" or
            m.get("phase") != "design_only"):
        raise PermissionError("Stage6-light method must remain non-executable")
    auth = m.get("authorization", {})
    denied = ("worlds_allowed", "cohorts_allowed", "engineering_rehearsal_allowed",
              "science_admission_allowed", "auto_start_allowed",
              "adr0017_lineage_exception_accepted")
    unbound = ("owner_decision_sha", "owner_authorized_world_indices",
               "assigned_world_seeds", "assigned_founder_seeds", "execution_source_sha",
               "execution_transport_fingerprint", "independent_allocation_manifest_sha256",
               "full_scale_python311_rehearsal_sha", "full_scale_python312_rehearsal_sha")
    if (set(auth) != set(denied + unbound) or
            any(auth[k] is not False for k in denied) or
            any(auth[k] is not None for k in unbound)):
        raise PermissionError("Stage6 science or rehearsal is not admitted")
    custody = m.get("custody", {})
    if (custody.get("scientific_worlds_and_lives_now_allowed") is not False or
            custody.get("rehearsal_worlds_and_lives_now_allowed") is not False or
            custody.get("per_generation_selection_requires_separate_adr0017_acceptance") is not True):
        raise PermissionError("Stage6 lineage-specific ADR-0017 approval is absent")
    return m


def logical_world(p: int, g: int, family: str, repeat: int) -> int:
    if (not _integer(p, 0, 15) or not _integer(g, 0, 2) or
            family not in FAMILIES or not _integer(repeat, 0, 1)):
        raise ValueError("invalid Stage6 logical coordinate")
    return ((p * 3 + g) * 3 + FAMILIES.index(family)) * 2 + repeat


def _case_key(identity: dict, generation: int) -> tuple:
    required = {"population", "generation", "arm", "slot", "family", "repeat",
                "logical_world", "world_seed", "life_seed", "genome_sha256",
                "world_sha256", "source_sha256"}
    if not isinstance(identity, dict) or set(identity) != required:
        raise ValueError("unrecognized case identity or leaky fields")
    p, g, arm, slot, family, repeat = (identity[k] for k in
        ("population", "generation", "arm", "slot", "family", "repeat"))
    if (not _integer(p, 0, 15) or type(g) is not int or g != generation or
            arm not in (("shared",) if g == 0 else ARMS) or
            not _integer(slot, 0, 23) or family not in FAMILIES or
            not _integer(repeat, 0, 1)):
        raise ValueError("invalid Stage6 case coordinate")
    if identity["logical_world"] != logical_world(p, g, family, repeat):
        raise ValueError("logical World mapping inconsistent")
    if not _integer(identity["world_seed"], 0, 2**63-1):
        raise ValueError("unbound or invalid World seed")
    if not _integer(identity["life_seed"], 0, 2**63-1):
        raise ValueError("unbound or invalid life seed")
    if not all(_hash(identity[k]) for k in ("genome_sha256", "world_sha256", "source_sha256")):
        raise ValueError("missing 64-hex source/world/genome identity")
    return (p, g, arm, slot, family, repeat)


def _check_genome(genome: dict, identity: dict) -> None:
    if (type(genome) is not dict or set(genome) != {"schema", "genes"} or
            genome["schema"] != "i3-genome-v4" or
            type(genome["genes"]) is not dict or
            set(genome["genes"]) != set(GENE_KEYS)):
        raise ValueError("native genome v4 shape changed, or world facts inherited")
    if set(BOUNDS) != set(GENE_KEYS) or not all(
        type(x) in (float, int) and isfinite(x) and
        BOUNDS[k][0] <= x <= BOUNDS[k][1]
        for k, x in genome["genes"].items()
    ) or not (genome["genes"]["gamma1"] <= genome["genes"]["gamma2"] <=
              genome["genes"]["gamma3"]):
        raise ValueError("invalid native genome-v4 gene bounds/horizons")
    if _digest(genome) != identity["genome_sha256"]:
        raise ValueError("native genome digest differs from identity")


def _check_funding(ca: dict, steps: int) -> None:
    if (not isinstance(ca, dict) or ca.get("schema") != FUNDING_SCHEMA or
            ca.get("status") != "SETTLED_FOR_DECLARED_WORK"):
        raise ValueError("cognitive-work funding is not settled")
    totals = ca.get("totals")
    if not isinstance(totals, dict) or set(totals) != {"energy", "vigilance"}:
        raise ValueError("both physical cognitive currencies required")
    for account in totals.values():
        if not isinstance(account, dict) or set(account) != {"requested", "paid", "unpaid"}:
            raise ValueError("incomplete physical cognitive accounting")
        if not all(_nonnegative(account[k]) for k in account):
            raise ValueError("invalid physical cognitive counter")
        if account["unpaid"] > 1e-12:
            raise ValueError("unfunded cognition cannot be a settled Stage6 life")
        if abs(account["requested"] - account["paid"] - account["unpaid"]) > 1e-6:
            raise ValueError("paid cognition receipts do not reconcile")
    for field in ("shortfall_steps", "pending_replays", "pending_energy", "pending_vigilance"):
        if ca.get(field) != 0 or type(ca[field]) not in (float, int):
            raise ValueError("unpaid or unconsumed cognitive work")
    for field in ("learning_updates", "replays_executed", "inactive_steps"):
        if not _integer(ca.get(field), 0, steps * 512):
            raise ValueError("invalid cognition update count")
    if ca["inactive_steps"] > steps:
        raise ValueError("more inactivity than lived steps")


def _check_native_life(identity: dict, life: dict, source_pin: str,
                       source_head: str, protocol: str) -> None:
    if not isinstance(life, dict):
        raise ValueError("missing native life object")
    manifest = life.get("manifest")
    if not isinstance(manifest, dict) or manifest.get("schema") != PROVENANCE_SCHEMA:
        raise ValueError("missing native v2 life manifest")
    if manifest.get("execution_model") != "i3-funded-v2" or manifest.get("protocol") != protocol:
        raise ValueError("wrong native model/protocol")
    if not isinstance(manifest.get("source"), dict) or manifest["source"].get("sha256") != source_pin:
        raise ValueError("life source digest does not match the prospectively claimed pin")
    files = manifest["source"].get("files")
    if not isinstance(files, dict) or not files or not all(type(k) is str and _hash(v) for k,v in files.items()):
        raise ValueError("missing native on-disk source file fingerprints")
    if _digest(files) != source_pin:
        raise ValueError("source content hash is not self-consistent")
    if (manifest["source"].get("git_head") != source_head or
            manifest["source"].get("working_tree_dirty") is not False):
        raise ValueError("execution did not originate in the claimed clean checkout")
    python = manifest.get("python")
    if (not isinstance(python, dict) or
            python.get("implementation") != "CPython" or
            type(python.get("version")) is not str or
            not python["version"].startswith(("3.11.", "3.12."))):
        raise ValueError("unrecognized execution interpreter provenance")
    if manifest.get("horizon") != 400 or life.get("horizon") != 400:
        raise ValueError("Stage6 fixed horizon violated")
    if manifest.get("life_seed") != identity["life_seed"] or life.get("life_seed") != identity["life_seed"]:
        raise ValueError("different life seed in original and envelope")
    world = manifest.get("world")
    if (not isinstance(world, dict) or
            set(world) != {"name", "width", "height", "spawn", "body", "laws",
                           "water", "food", "token_effects", "changes"} or
            world.get("name") != life.get("world") or
            not _integer(world.get("width"), 3, 30) or
            not _integer(world.get("height"), 3, 30) or
            not isinstance(world.get("body"), list) or
            len(world["body"]) != 5 or
            not all(_nonnegative(x) for x in world["body"]) or
            not isinstance(world.get("spawn"), list) or
            len(world["spawn"]) != 2 or
            not all(type(x) is int for x in world["spawn"]) or
            not isinstance(world.get("laws"), dict) or
            not all(isinstance(world.get(k), list)
                    for k in ("water", "food", "token_effects", "changes"))):
        raise ValueError("native WorldSpec snapshot shape inconsistent")
    if not _hash(manifest.get("world_sha256")) or _digest(world) != manifest["world_sha256"]:
        raise ValueError("WorldSpec snapshot digest mismatch")
    if manifest["world_sha256"] != identity["world_sha256"]:
        raise ValueError("WorldSpec not bound to planned case")
    _check_genome(manifest.get("genome"), identity)
    if life.get("genome") != identity["genome_sha256"]:
        raise ValueError("life genome digest mismatch")
    if not _hash(life.get("manifest_id")) or _digest(manifest) != life["manifest_id"]:
        raise ValueError("native manifest_id mismatch")
    if not _hash(life.get("evidence_head")) or not _hash(life.get("trace_head")):
        raise ValueError("missing native terminal evidence/trace head")
    if "experimental_policy" in manifest or "experimental_policy" in life or "replay_gate" in life:
        raise ValueError("P1.3 reference only, no policy replacement")
    steps = life.get("steps_lived")
    if not _integer(steps, 1, 400):
        raise ValueError("invalid native lifetime horizon")
    terminal, causes = life.get("terminal"), life.get("death_causes")
    if terminal not in ("dead", "censored") or not isinstance(causes, list):
        raise ValueError("invalid native terminal status")
    if terminal == "censored" and (steps != 400 or causes):
        raise ValueError("censored life must reach horizon alive")
    if terminal == "dead" and not causes:
        raise ValueError("dead life without recorded causes")
    _check_funding(life.get("cognitive_accounting"), steps)


def _gzip_limited(packed: bytes) -> bytes:
    import io
    with gzip.GzipFile(fileobj=io.BytesIO(packed)) as stream:
        raw = stream.read(MAX_ORIGINAL_BYTES + 1)
        if len(raw) > MAX_ORIGINAL_BYTES or stream.read(1):
            raise ValueError("gzip original exceeds structural audit limit")
        return raw


def inspect_sealed_generation(archive_dir: str | Path, generation: int,
                              expected_cases: list[dict], *,
                              expected_protocol: str, source_pin: str,
                              source_head: str) -> dict:
    """Audit native-shaped originals, without reading a survival contrast.

    expected_cases must originate from a future independently audited allocation.
    Here the caller only supplies untrusted claims: this does not certify that
    a study source, World or seed was independently allocated or approved.
    """
    _assert_inert()  # fail before touching any archive
    if not _integer(generation, 0, 2):
        raise ValueError("invalid generation")
    if (not isinstance(expected_protocol, str) or not expected_protocol or
            not _hash(source_pin) or type(source_head) is not str or
            re.fullmatch(r"[0-9a-f]{40}", source_head) is None):
        raise ValueError("invalid prospective provenance claims")
    target_count = 2304 if generation == 0 else 4608
    if type(expected_cases) is not list or len(expected_cases) != target_count:
        raise ValueError("expected native identities incomplete")
    expected = {}
    for case in expected_cases:
        k = _case_key(case, generation)
        if k in expected or case["source_sha256"] != source_pin:
            raise ValueError("duplicate case or wrong source in claimed plan")
        expected[k] = case

    root = Path(archive_dir)
    raw_manifest = (root / "MANIFEST.json").read_bytes()
    if len(raw_manifest) > MAX_MANIFEST_BYTES:
        raise ValueError("oversized generation manifest")
    outer_sha = (root / "MANIFEST.sha256").read_text(encoding="ascii").strip()
    if not _hash(outer_sha) or sha256(raw_manifest).hexdigest() != outer_sha:
        raise ValueError("manifest seal has changed")
    manifest = json.loads(raw_manifest)
    if (not isinstance(manifest, dict) or manifest.get("schema") != SCHEMA or
        manifest.get("status") != "GENERATED" or manifest.get("failure") is not None or
        manifest.get("generated") != target_count or manifest.get("planned") != target_count):
        raise ValueError("generation incomplete or not sealed")
    files = manifest.get("files")
    if not isinstance(files, list) or len(files) != target_count:
        raise ValueError("native archive file list incomplete")
    # Forbid unexpected names and path escapes, including symlinks.
    declared_names = set()
    seen = set()
    opportunity = {}
    genotypes = {}
    for i, entry in enumerate(files):
        if not isinstance(entry, dict) or set(entry) != {"file", "identity", "sha256", "uncompressed_sha256"}:
            raise ValueError("incomplete original receipt")
        name = entry["file"]
        if type(name) is not str or not FILENAME.fullmatch(name) or name != f"life-{i:03d}.json.gz" or name in declared_names:
            raise ValueError("duplicate, reordered or unsafe original filename")
        declared_names.add(name)
        if not _hash(entry["sha256"]) or not _hash(entry["uncompressed_sha256"]):
            raise ValueError("invalid original digests")
        identity = entry["identity"]
        k = _case_key(identity, generation)
        if k in seen or k not in expected or identity != expected[k]:
            raise ValueError("archive originals do not match exact claimed cases")
        seen.add(k)
        file_path = root / name
        if not file_path.is_file() or file_path.is_symlink():
            raise ValueError("unreadable or redirected original")
        packed = file_path.read_bytes()
        if sha256(packed).hexdigest() != entry["sha256"]:
            raise ValueError("compressed original changed")
        raw = _gzip_limited(packed)
        if sha256(raw).hexdigest() != entry["uncompressed_sha256"]:
            raise ValueError("uncompressed original changed")
        payload = json.loads(raw)
        if not isinstance(payload, dict) or set(payload) != {"identity", "life"} or payload["identity"] != identity:
            raise ValueError("original payload identity changed")
        life = payload["life"]
        _check_native_life(identity, life, source_pin, source_head, expected_protocol)
        p, g, arm, slot, family, repeat = k
        coord = identity["logical_world"]
        opp = opportunity.setdefault(coord, (identity["world_seed"], identity["life_seed"], identity["world_sha256"]))
        if opp != (identity["world_seed"], identity["life_seed"], identity["world_sha256"]):
            raise ValueError("unpaired opportunities inside a World coordinate")
        genokey = (p, g, arm, slot)
        prior = genotypes.setdefault(genokey, identity["genome_sha256"])
        if prior != identity["genome_sha256"]:
            raise ValueError("genome varied between a person's six lived contexts")
    if seen != set(expected):
        raise ValueError("missing native original identities")
    if len(opportunity) != 96:  # each generation: 16 populations * 3 families * 2 repeats
        raise ValueError("wrong number of distinct World opportunities")
    if len(genotypes) != (384 if generation == 0 else 768):
        raise ValueError("wrong number of genome identities")
    actual_names = {x.name for x in root.iterdir() if x.is_file()}
    if actual_names != declared_names | {"MANIFEST.json", "MANIFEST.sha256"}:
        raise ValueError("undeclared material in native original archive")
    return {
        "schema": "i3-stage6-native-original-preflight/v1",
        "status": "STRUCTURAL_SHAPE_PASS_ONLY_NOT_ADMITTED",
        "generation": generation,
        "expected_native_records": target_count,
        "checked_native_records": len(seen),
        "paired_opportunities_checked": len(opportunity),
        "genome_contexts_checked": len(genotypes),
        "original_manifest_sha256": outer_sha,
        "source_pin_claim_is_external_authority": False,
        "source_bytes_against_checkout_verified": False,
        "originals_are_independently_time_stamped": False,
        "genome_mutation_chain_verified": False,
        "scientific_independence_verified": False,
        "science_verdict": "NOT_ISSUED",
        "new_worlds_opened": 0,
        "new_lives_created": 0,
        "owner_authorization": False,
    }


def open_world(*_args, **_kwargs):
    raise PermissionError("read-only native original preflight cannot open a World")


def run_life(*_args, **_kwargs):
    raise PermissionError("read-only native original preflight cannot create a life")


def authorize_science(*_args, **_kwargs):
    raise PermissionError("preflight is never a scientific admission ticket")


# Only known, documented historical ranges. This check is a necessary shape
# condition, not evidence of unused physical seeds or independent ecologies.
KNOWN_EXCLUDED_WORLD_SEEDS = (
    range(100, 130), range(2_000, 2_100), range(10_000, 10_400),
    range(30_000, 30_200), range(90_000, 91_000),
    range(1_000_200, 1_000_300), range(1_200_000, 1_200_200),
)


def inspect_three_generation_shape(archives: dict[int, str | Path],
                                   expected_cases: dict[int, list[dict]], *,
                                   expected_protocol: str, source_pin: str,
                              source_head: str) -> dict:
    """Check an *untrusted* proposed 288-world mapping and 3 native archives.

    Missing independent authority, genuine current-source pin, ownership of
    index allocations and the mutation/parent lineage remain explicit blockers.
    This check never approves a seed or validates G/S/R execution timing.
    """
    _assert_inert()
    if (not isinstance(archives, dict) or set(archives) != {0, 1, 2} or
            not isinstance(expected_cases, dict) or set(expected_cases) != {0, 1, 2}):
        raise ValueError("exactly three non-authorized native archive claims required")
    world_seeds, life_seeds, world_digests = {}, {}, {}
    for generation in (0, 1, 2):
        rows = expected_cases[generation]
        if not isinstance(rows, list):
            raise ValueError("non-list native case data")
        for row in rows:
            _case_key(row, generation)
            coord = row["logical_world"]
            now = (row["world_seed"], row["life_seed"], row["world_sha256"])
            if coord in world_seeds and world_seeds[coord] != now:
                raise ValueError("inconsistent pairing of two arms in one world")
            world_seeds[coord] = now
    if set(world_seeds) != set(range(288)):
        raise ValueError("missing or extra logical world coordinate")
    seeds = [w[0] for w in world_seeds.values()]
    lseeds = [w[1] for w in world_seeds.values()]
    spec_hashes = [w[2] for w in world_seeds.values()]
    if len(set(seeds)) != 288 or len(set(lseeds)) != 288:
        raise ValueError("a proposed physical World or life seed repeats")
    if len(set(spec_hashes)) != 288:
        raise ValueError("two proposed WorldSpec snapshots have the same digest")
    if any(seed in forbidden for seed in seeds for forbidden in KNOWN_EXCLUDED_WORLD_SEEDS):
        raise ValueError("physical World seed proposal overlaps a known historical range")

    reports = [inspect_sealed_generation(archives[g], g, expected_cases[g],
                                        expected_protocol=expected_protocol,
                                        source_pin=source_pin, source_head=source_head)
               for g in (0, 1, 2)]
    return {
        "schema": "i3-stage6-three-generation-native-shape-preflight/v1",
        "status": "THREE_GENERATION_SHAPE_PASS_ONLY_NOT_ADMITTED",
        "record_counts": [x["checked_native_records"] for x in reports],
        "checked_fabricated_or_supplied_records": sum(x["checked_native_records"] for x in reports),
        "symbolic_world_coordinates_checked": 288,
        "claimed_seed_collisions_in_known_ranges": 0,
        "known_range_check_is_exhaustive": False,
        "scientific_independence_verified": False,
        "true_source_checkout_attested": False,
        "parent_selection_and_mutations_verified": False,
        "adr0017_lineage_exception_accepted": False,
        "owner_authorization": False,
        "new_worlds_opened": 0,
        "new_lives_created": 0,
        "science_verdict": "NOT_ISSUED",
    }
