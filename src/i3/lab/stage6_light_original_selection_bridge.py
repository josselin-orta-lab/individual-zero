"""Read-only Stage-6-light binding: sealed native originals -> claimed parents.

This is an offline audit of a *supplied* archive, not a G/S/R transport, a
source authenticator, a preregistration timestamp, or an admission to run lives.
No runtime/genome/World/birth imports are allowed here. Full native custody and
lineage checks MUST pass before any parent-draw comparison. Even then, a caller
can fit draw seeds to choices after seeing results: do not claim selection was
independently precommitted or scientifically observed.
"""
from __future__ import annotations

from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path
import random

from i3.lab import stage6_light_native_custody_preflight as custody
from i3.lab import stage6_light_genome_lineage_preflight as ancestry

ARMS = ("selected", "random_parent")
DRAW_SCHEMA = "i3-stage6-parent-draw-supplied-claim/v1"
DRAW_FIELDS = frozenset((
    "schema", "population", "generation", "arm", "slot", "parent_slot",
    "draw_seed", "prior_generation_manifest_sha256", "parent_genome_sha256",
    "offspring_genome_sha256",
))


def _read_manifest(root: Path, expected_sha: str) -> list[dict]:
    """Rebind the exact manifest bytes previously checked by native custody."""
    if not root.is_dir() or root.is_symlink():
        raise ValueError("unsafe or missing archive directory")
    manifest_path, seal_path = root / "MANIFEST.json", root / "MANIFEST.sha256"
    if (not manifest_path.is_file() or manifest_path.is_symlink() or
            not seal_path.is_file() or seal_path.is_symlink()):
        raise ValueError("archive manifest must be regular, not redirected")
    raw = manifest_path.read_bytes()
    if len(raw) > custody.MAX_MANIFEST_BYTES:
        raise ValueError("oversize archive manifest")
    digest = sha256(raw).hexdigest()
    if (digest != expected_sha or
            seal_path.read_text(encoding="ascii").strip() != expected_sha):
        raise ValueError("manifest changed after native preflight")
    obj = json.loads(raw)
    if not isinstance(obj, dict) or obj.get("schema") != custody.SCHEMA or not isinstance(obj.get("files"), list):
        raise ValueError("wrong post-audit manifest shape")
    return obj["files"]


def _read_persistence_original(root: Path, entry: dict, *, generation: int,
                               protocol: str, source_pin: str,
                               source_head: str) -> tuple[tuple, bool, int]:
    """Verify *one* original again, then extract only the two allowed scalars.

    This helper is a unit-testable receipt verifier; it is never a substitute for
    the full-generation sealed-archive guard in inspect_original_selection().
    """
    if type(entry) is not dict or set(entry) != {
            "file", "identity", "sha256", "uncompressed_sha256"}:
        raise ValueError("unknown original manifest entry")
    identity = entry["identity"]
    key = custody._case_key(identity, generation)
    name = entry["file"]
    if (type(name) is not str or not custody.FILENAME.fullmatch(name) or
            not custody._hash(entry["sha256"]) or
            not custody._hash(entry["uncompressed_sha256"])):
        raise ValueError("unsafe original receipt")
    if not root.is_dir() or root.is_symlink():
        raise ValueError("archive directory is unsafe")
    path = root / name
    if not path.is_file() or path.is_symlink():
        raise ValueError("archive original absent or redirected")
    packed = path.read_bytes()
    if sha256(packed).hexdigest() != entry["sha256"]:
        raise ValueError("compressed original changed after custody audit")
    raw = custody._gzip_limited(packed)
    if sha256(raw).hexdigest() != entry["uncompressed_sha256"]:
        raise ValueError("uncompressed original changed after custody audit")
    payload = json.loads(raw)
    if (type(payload) is not dict or set(payload) != {"identity", "life"} or
            payload["identity"] != identity):
        raise ValueError("payload identity is not the audited original")
    life = payload["life"]
    custody._check_native_life(identity, life, source_pin, source_head, protocol)
    return key, life["terminal"] == "censored", life["steps_lived"]


def _verify_draws(*, draws: list[dict], offspring: list[dict],
                  native_index: list[dict], persistence: dict[tuple, dict],
                  sealed_sha: dict[int, str]) -> None:
    """Recompute supplied draws using native-derived persistence, never mock scores."""
    if type(draws) is not list or len(draws) != 16 * 2 * 2 * 24:
        raise ValueError("complete declared G1/G2 parent draw table required")
    genomes = {(x["population"], x["generation"], x["arm"], x["slot"]): x["genome_sha256"]
               for x in native_index}
    children = {(x["population"], x["generation"], x["arm"], x["slot"]): x
                for x in offspring}
    seen, seeds = set(), set()
    for draw in draws:
        if (type(draw) is not dict or set(draw) != DRAW_FIELDS or
                draw["schema"] != DRAW_SCHEMA or
                not custody._integer(draw["population"], 0, 15) or
                not custody._integer(draw["generation"], 1, 2) or
                draw["arm"] not in ARMS or
                not custody._integer(draw["slot"], 0, 23) or
                not custody._integer(draw["parent_slot"], 0, 23) or
                not custody._integer(draw["draw_seed"], 0, 2**63 - 1) or
                not all(custody._hash(draw[k]) for k in (
                    "prior_generation_manifest_sha256", "parent_genome_sha256",
                    "offspring_genome_sha256"))):
            raise ValueError("invalid supplied native-linked parent draw")
        p, g, arm, slot = (draw[k] for k in ("population", "generation", "arm", "slot"))
        key = (p, g, arm, slot)
        if key in seen or draw["draw_seed"] in seeds:
            raise ValueError("duplicate parent draw identity or stream")
        seen.add(key)
        seeds.add(draw["draw_seed"])
        if draw["prior_generation_manifest_sha256"] != sealed_sha[g-1]:
            raise ValueError("parent draw not bound to audited prior-generation seal")
        prev_arm = "shared" if g == 1 else arm
        rng = random.Random(draw["draw_seed"])
        if arm == "selected":
            previous = [persistence[p, g-1, prev_arm, s] for s in range(24)]
            ranked = sorted(range(24), key=lambda s: (
                -sum(value[0] for value in previous[s].values()),
                -sum(value[1] for value in previous[s].values()), s))
            parent_slot = rng.choices(ranked, weights=range(24, 0, -1), k=1)[0]
        else:
            # The control does not inspect rank, survival, steps or distress.
            parent_slot = rng.randrange(24)
        parent_key = (p, g-1, prev_arm, parent_slot)
        child = children.get(key)
        if (draw["parent_slot"] != parent_slot or
                draw["parent_genome_sha256"] != genomes[parent_key] or
                draw["offspring_genome_sha256"] != genomes[key] or
                child is None or child["parent_slot"] != parent_slot or
                child["parent_genome_sha256"] != genomes[parent_key] or
                child["genome_sha256"] != genomes[key]):
            raise ValueError("parent choice, genotype or mutation receipt contradicts originals")
    expected = {(p, g, arm, slot) for p in range(16) for g in (1, 2)
                for arm in ARMS for slot in range(24)}
    if seen != expected:
        raise ValueError("missing or foreign parent draw")


def inspect_original_selection(archive_dirs: dict[int, str | Path],
                               expected_cases: dict[int, list[dict]],
                               founders: list[dict], offspring: list[dict],
                               draws: list[dict], *, expected_protocol: str,
                               source_pin: str, source_head: str) -> dict:
    """Audit a FULL supplied Stage6 archive, no live execution or science permit.

    All 11,520 originals must first pass native custody. We then extract
    persistence from the 6,912 *original* G0/G1 gzip payloads, derive the
    genotype-index from all three sealed generation manifests, and reproduce
    the claimed G1/G2 draws and genome mutations. Source/seed authority and
    chronological G/S delivery remain unverified even on full success.
    """
    custody._assert_inert()  # before even opening an archive or trusting a pin
    if (type(archive_dirs) is not dict or set(archive_dirs) != {0, 1, 2} or
            type(expected_cases) is not dict or set(expected_cases) != {0, 1, 2}):
        raise ValueError("complete G0/G1/G2 archive and identity claims required")
    roots = {g: Path(archive_dirs[g]) for g in (0, 1, 2)}
    if any(not r.is_dir() or r.is_symlink() for r in roots.values()):
        raise ValueError("unsafe archive root")
    if len({str(r.resolve()) for r in roots.values()}) != 3:
        raise ValueError("repeated generation archive root")
    original_report = custody.inspect_three_generation_shape(
        roots, expected_cases, expected_protocol=expected_protocol,
        source_pin=source_pin, source_head=source_head)
    seals = original_report["original_manifest_sha256_by_generation"]
    if (type(seals) is not dict or set(seals) != {"G0", "G1", "G2"} or
            not all(custody._hash(v) for v in seals.values())):
        raise ValueError("source-native sealed manifest receipts unavailable")
    seal_by_gen = {g: seals[f"G{g}"] for g in (0, 1, 2)}
    people, index = defaultdict(dict), {}
    for g in (0, 1, 2):
        entries = _read_manifest(roots[g], seal_by_gen[g])
        for entry in entries:
            identity = entry["identity"]
            p, _, arm, slot, family, repeat = custody._case_key(identity, g)
            key = (p, g, arm, slot)
            digest = identity["genome_sha256"]
            if key in index and index[key] != digest:
                raise ValueError("six native originals disagree on genome identity")
            index[key] = digest
            if g <= 1:
                actual_key, censored, steps = _read_persistence_original(
                    roots[g], entry, generation=g, protocol=expected_protocol,
                    source_pin=source_pin, source_head=source_head)
                if actual_key != (p, g, arm, slot, family, repeat):
                    raise ValueError("post-audit original coordinate mismatch")
                opportunity = (family, repeat)
                if opportunity in people[key]:
                    raise ValueError("duplicate native persistence opportunity")
                people[key][opportunity] = (censored, steps)
        # A swapped manifest after the audit cannot be used for a new selection.
        _read_manifest(roots[g], seal_by_gen[g])
    expected_people = {(p, g, arm, slot) for p in range(16) for g in (0, 1)
                       for arm in (("shared",) if g == 0 else ARMS)
                       for slot in range(24)}
    opportunities = {(family, repeat) for family in custody.FAMILIES for repeat in (0, 1)}
    if (set(people) != expected_people or
            any(set(row) != opportunities for row in people.values()) or
            len(index) != 16 * 5 * 24):
        raise ValueError("not every original supplies six matching personal outcomes")
    native_index = [{"population": p, "generation": g, "arm": arm,
                     "slot": slot, "genome_sha256": digest}
                    for (p, g, arm, slot), digest in sorted(index.items())]
    genotype_result = ancestry.inspect_claimed_lineage(founders, offspring, native_index)
    _verify_draws(draws=draws, offspring=offspring, native_index=native_index,
                  persistence=people, sealed_sha=seal_by_gen)
    return {
        "schema": "i3-stage6-original-selection-binding-preauth/v1",
        "status": "SUPPLIED_NATIVE_ORIGINAL_SELECTION_SHAPE_MATCH_NOT_ADMITTED",
        "original_lives_structurally_checked": original_report["checked_fabricated_or_supplied_records"],
        "selection_inputs_read_from_original_gzip": sum(len(row) for row in people.values()),
        "genotypes_joined_to_originals": len(native_index),
        "offspring_mutations_reproduced": genotype_result["offspring_mutations_checked"],
        "claimed_parent_draws_reproduced": len(draws),
        "native_original_archive_content_checked": True,
        "external_git_pin_authenticity_attested": False,
        "originals_independently_timestamped": False,
        "draw_seeds_independently_precommitted": False,
        "g_s_r_chronology_attested": False,
        "live_native_actions_replayed_or_verified": False,
        "independent_population_sampling_verified": False,
        "owner_authorization": False,
        "new_worlds_opened": 0,
        "new_lives_created": 0,
        "science_verdict": "NOT_ISSUED",
    }


def open_world(*_args, **_kwargs):
    raise PermissionError("read-only archive binder cannot open a World")


def run_life(*_args, **_kwargs):
    raise PermissionError("read-only archive binder cannot create a life")


def authorize_science(*_args, **_kwargs):
    raise PermissionError("archive binder cannot authorize science")
