"""Independent, read-only Stage8-C ORIGINAL gzip audit; no World or birth.

Recomputes population-level S-M persistence from 32,256 original JSON gzip
bodies, not the prospective scientific reducer or its reduced artefacts.
Rechecks native v4 parental mutation provenance and exact S/M multiplicities.
No lifetime simulation, motor replay, external attestations or reruns.

Run only AFTER the single prospective science workflow has completed and
published both its preexposure plan and complete scientific original ZIP.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import gzip
from hashlib import sha256
import hmac
import io
import json
import math
from pathlib import Path
import random
import re
import sys

from i3.modules import genome as G
from i3.lab import stage6_light_native_custody_preflight as N

SCHEMA = "i3-stage8c-independent-original-gzip-audit/v1"
ORIGINAL_HEAD = "a32b7bf50981e0bbaf688e3caf9973525888c05d"
ORIGINAL_RUN_ID = 44320492293
TECH_PASS = "STAGE8C_THREE_ARM_FULL_ENGINEERING_SEALED_NO_SCIENCE"
SUCCESS = "STAGE8C_G2_SCORE_IDENTITY_ADVANTAGE_F0"
NEGATIVE = "STAGE8C_G2_SCORE_IDENTITY_ADVANTAGE_NOT_DEMONSTRATED_F0"
FAMILIES = ("stable", "depletion", "pulse")
ARMS = ("selected", "matched_multiplicity", "random_parent")
PHASES = ("G0", "SEAL_G0", "SELECT_G1", "G1", "SEAL_G1",
          "SELECT_G2", "G2", "SEAL_G2", "R_FINAL")
GEN_COUNTS = (2304, 6912, 6912)
POPULATIONS = 32
LIVES = 32256
MUTATIONS = 4608
T_CRIT_31 = 2.0395134463964077
# SHA-256 of the exact Stage8-C METHOD committed BEFORE both engineering campaigns.
FROZEN_METHOD_SHA256 = "c63ef4730795f54d6fba282010a70e7fa32760717967af280ac4169d9bced8c4"
HEX = re.compile(r"[0-9a-f]{64}\Z")
NAME = re.compile(r"life-[0-9]{3,5}\.json\.gz\Z")
MAX_RAW_LIFE = 2_000_000


def canonical(data: object) -> bytes:
    return json.dumps(data, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def digest(data: object) -> str:
    return sha256(canonical(data)).hexdigest()


def file_sha(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def parse(path: Path) -> dict:
    if path.is_symlink() or not path.is_file():
        raise ValueError("unavailable, missing or redirected archive file: " + str(path))
    return json.loads(path.read_bytes())


def require_plan(plan: object, schema: str) -> dict:
    if (type(plan) is not dict or plan.get("schema") != schema
            or type(plan.get("allocation_sha256")) is not str
            or not HEX.fullmatch(plan["allocation_sha256"])
            or digest({k: v for k, v in plan.items()
                       if k != "allocation_sha256"}) != plan["allocation_sha256"]):
        raise ValueError("foreign or unsealed prospective allocation")
    return plan


def original_packet(packed: bytes, entry: dict) -> tuple[dict, dict]:
    """Bound decompression and verify BOTH gzip and decoded-body digests."""
    if (type(entry) is not dict or
            set(entry) != {"file", "identity", "sha256", "uncompressed_sha256"}
            or not all(type(entry[k]) is str and HEX.fullmatch(entry[k])
                       for k in ("sha256", "uncompressed_sha256"))):
        raise ValueError("incomplete native original manifest row")
    if sha256(packed).hexdigest() != entry["sha256"]:
        raise ValueError("gzip SHA differs from frozen original manifest")
    with gzip.GzipFile(fileobj=io.BytesIO(packed)) as stream:
        raw = stream.read(MAX_RAW_LIFE + 1)
        if len(raw) > MAX_RAW_LIFE or stream.read(1):
            raise ValueError("oversized gzip life")
    if sha256(raw).hexdigest() != entry["uncompressed_sha256"]:
        raise ValueError("decoded original SHA differs from frozen manifest")
    packet = json.loads(raw)
    if (type(packet) is not dict or set(packet) != {"identity", "life"}
            or packet["identity"] != entry["identity"]
            or type(packet["life"]) is not dict):
        raise ValueError("gzip original identity or body is foreign")
    return packet["identity"], packet["life"]


def _worlds(panel: dict) -> dict:
    p = {}
    for row in panel["worlds"]:
        key = (row["population"], row["generation"], row["family"], row["repeat"])
        if key in p:
            raise ValueError("duplicate allocated World opportunity")
        p[key] = row
    expected = {(pop, gen, fam, rep)
                for pop in range(16) for gen in range(3)
                for fam in FAMILIES for rep in (0, 1)}
    if set(p) != expected:
        raise ValueError("incomplete frozen World opportunities")
    return p


def verify_new_science_entropy(
        science_root_hex: str, native: dict, receipts: dict,
        science_archive: str) -> None:
    """Rebuild domain-separated planned roots without opening a World.

    Engineering receipts cannot provide science's third root, World holdouts
    or a parent archive root.  A prepublished plan cannot rewrite these roots.
    """
    if (type(science_root_hex) is not str or
            not HEX.fullmatch(science_root_hex) or
            type(science_archive) is not str or
            not science_archive.startswith("/") or
            type(native) is not dict or
            type(receipts) is not dict or
            set(receipts) != {"3.11", "3.12"}):
        raise ValueError("invalid third-root evidence")
    root = hmac.new(
        bytes.fromhex(science_root_hex),
        b"i3-stage8c-new-prospective-science-data-generator/v1",
        sha256).hexdigest()
    if native.get("root_hex") != root:
        raise ValueError("science native root not derived from allocated third root")
    panels = native.get("panels")
    if type(panels) is not list or len(panels) != 2:
        raise ValueError("two science panels not frozen")
    expected_panels = [
        hmac.new(bytes.fromhex(root),
                 f"i3-stage8c-disjoint-panel-v1/{i}".encode("ascii"),
                 sha256).hexdigest()
        for i in range(2)
    ]
    if [p.get("root_hex") for p in panels] != expected_panels:
        raise ValueError("science panel root domain or ordering changed")
    science_holdout = native.get("g2_heldout_worlds_sha256")
    parent_root_sha = digest(expected_panels)
    for receipt in receipts.values():
        if (type(receipt) is not dict or
                receipt.get("g2_holdout_worlds_sha256") == science_holdout or
                receipt.get("root_commitment_sha256") == parent_root_sha):
            raise ValueError("science root or G2 World holdout reused from engineering")
        previous = receipt.get("archive_root")
        if type(previous) is not str or not previous.startswith("/"):
            raise ValueError("missing previous technical archive root")
        old = Path(previous)
        new = Path(science_archive)
        if (old == new or old.is_relative_to(new)
                or new.is_relative_to(old)):
            raise ValueError("science and technical archive roots overlap")


def _plan_controls(plan: dict, originals: Path) -> tuple[dict, list[dict]]:
    require_plan(plan, "i3-stage8c-new-prospective-science-envelope/v1")
    native = require_plan(
        plan["native_original_data_generator_plan"],
        "i3-stage8c-three-arm-native-technical-plan/v1")
    if (plan.get("status") != "STAGE8C_SCIENCE_ALLOCATED_NOT_EXPOSED"
            or plan.get("scientific_admission") is not True
            or plan.get("source_git_head") != ORIGINAL_HEAD
            or native.get("source_git_head") != ORIGINAL_HEAD
            or plan.get("source_files_sha256") != native.get("source_files_sha256")
            or plan.get("preexposure_scientific_result") != "NOT_ISSUED"
            or plan.get("scientific_lives_existing_at_allocation") != 0
            or plan.get("planned_native_original_lives") != LIVES
            or native.get("planned_original_lives") != LIVES
            or plan.get("planned_g2_heldout_worlds") != 192
            or plan.get("planned_mutations") != MUTATIONS
            or plan.get("g2_heldout_worlds_sha256") !=
            native.get("g2_heldout_worlds_sha256")
            or plan.get("nested_plan_sha256") != native["allocation_sha256"]
            or plan.get("no_retry") is not True or
            type(plan.get("archive_root")) is not str
            or not plan["archive_root"].startswith("/")
            or native.get("archive_root") != plan["archive_root"] + "/NATIVE_ORIGINALS"):
        raise ValueError("science was not admitted on source-locked full allocation")
    method = plan.get("frozen_method")
    inference = plan.get("frozen_scientific_inference")
    if (method != native.get("frozen_method") or
            method.get("population_units") != POPULATIONS or
            method.get("alpha_one_sided") != 0.025 or
            digest(method) != FROZEN_METHOD_SHA256 or
            method.get("t_critical") != T_CRIT_31 or
            method.get("primary_estimand") !=
            "mean_over_32_population_G2_mean_steps_selected_minus_matched" or
            inference.get("n_population_units") != POPULATIONS or
            inference.get("alpha_one_sided") != 0.025 or
            inference.get("t_critical_df31") != T_CRIT_31):
        raise ValueError("altered unique Stage8-C scientific criterion")
    if parse(originals / "INNER_PLAN.json") != native:
        raise ValueError("native original allocation not sealed to science plan")
    if len(native.get("panels", [])) != 2:
        raise ValueError("not 2 native 16-population panels")
    hold = native.get("g2_heldout_worlds_reserved")
    if (type(hold) is not list or len(hold) != 192
            or digest(hold) != plan["g2_heldout_worlds_sha256"]):
        raise ValueError("G2 World holdouts not prepublished")
    known = set()
    perms = set()
    for i, panel in enumerate(native["panels"]):
        require_plan(panel, "i3-stage8c-three-arm-native-panel-engineering/v1")
        if (panel["archive_root"] != native["archive_root"] + f"/PANEL_{i}"
                or panel["source_git_head"] != ORIGINAL_HEAD
                or panel.get("frozen_method_sha256") != FROZEN_METHOD_SHA256
                or panel["source_files_sha256"] != plan["source_files_sha256"]
                or panel["lives_per_generation"] != list(GEN_COUNTS)
                or panel["planned_lives"] != sum(GEN_COUNTS)
                or panel["scientific_admission"] is not False
                or len(panel.get("founders", [])) != 384
                or len(panel.get("draws", [])) != 2304
                or len(panel.get("worlds", [])) != 288
                or len(panel.get("matched_permutations", [])) != 32):
            raise ValueError("incomplete or foreign panel preexposure allocation")
        _worlds(panel)
        drawn = [r[k] for r in panel["worlds"]
                 for k in ("world_index", "world_seed", "life_seed")]
        drawn += [r["genome_seed"] for r in panel["founders"]]
        drawn += [r[k] for r in panel["draws"]
                  for k in ("parent_draw_seed", "mutation_seed")]
        if (len(set(drawn)) != len(drawn) or set(drawn)&known):
            raise ValueError("duplicate native seeds across same science cohort")
        known.update(drawn)
        for row in panel["matched_permutations"]:
            key = row["key_hex"]
            if key in perms or type(key) is not str or not HEX.fullmatch(key):
                raise ValueError("reused HMAC parental permutation key")
            perms.add(key)
    if len(known) != 11712 or len(perms) != 64:
        raise ValueError("wrong preexposure native seed/perm entropy budget")
    receipts = plan.get("engineering_receipts")
    if type(receipts) is not dict or set(receipts) != {"3.11", "3.12"}:
        raise ValueError("missing two source-exact technical receipts")
    for version, claim in receipts.items():
        if (type(claim) is not dict or
                claim.get("python_version") != version or
                claim.get("status") != TECH_PASS or
                claim.get("workflow_run_id") != ORIGINAL_RUN_ID or
                claim.get("no_retry") is not True or
                claim.get("source_git_head") != ORIGINAL_HEAD or
                claim.get("source_files_sha256") != plan["source_files_sha256"] or
                claim.get("native_original_lives_rehashed") != LIVES or
                claim.get("native_mutations_reproduced") != MUTATIONS or
                claim.get("phase_count") != 18 or
                claim.get("scientific_admission") is not False):
            raise ValueError("technical precondition not source exact")
    if (receipts["3.11"]["allocation_sha256"] ==
            receipts["3.12"]["allocation_sha256"] or
            receipts["3.11"]["g2_holdout_worlds_sha256"] ==
            receipts["3.12"]["g2_holdout_worlds_sha256"] or
            receipts["3.11"]["archive_root"] ==
            receipts["3.12"]["archive_root"]):
        raise ValueError("reused engineering allocation")
    joint_receipt = {
        "schema": "i3-stage8c-both-complete-technical-rehearsals/v1",
        "status": "STAGE8C_TWO_TECHNICAL_REPETITIONS_COMPLETE_NO_SCIENCE",
        "source_git_head": ORIGINAL_HEAD,
        "source_files_sha256": plan["source_files_sha256"],
        "workflow_run_id": receipts["3.11"]["workflow_run_id"],
        "engineering_rehearsal_receipts_sha256": digest(receipts),
        "native_original_lives_rehashed": 64512,
        "scientific_admission": False,
        "science_lives_generated": 0,
        "stage2_scientific_verdict": "NOT_ISSUED",
        "provenance": "INTERNAL_PROSPECTIVE_NOT_EXTERNALLY_ATTESTED",
    }
    if plan.get("engineering_gate_sha256") != digest(joint_receipt):
        raise ValueError("incomplete sealed double-technical gate")
    verify_new_science_entropy(
        plan.get("root_hex"), native, receipts, plan["archive_root"])
    g2 = {(r["panel"], r["population"], r["family"], r["repeat"])
          for r in hold}
    if len(g2) != 192:
        raise ValueError("repeated G2 reserved world")
    for row in hold:
        i = row["panel"]
        p = row["population"] - i*16
        x = _worlds(native["panels"][i])[p, 2, row["family"], row["repeat"]]
        if any(row[k] != x[k] for k in ("world_index", "world_seed", "life_seed")):
            raise ValueError("G2 holdout was not reserved before G0")
    return native, native["panels"]


def scan_generation(panel: dict, folder: Path, g: int) -> tuple[dict, dict, dict]:
    """Read only compressed originals, no native or scientific reducer."""
    source = panel["source_files_sha256"]
    worlds = _worlds(panel)
    allowed = ("shared",) if g == 0 else ARMS
    expected = {(p, arm, slot, fam, rep) for p in range(16)
                for arm in allowed for slot in range(24)
                for fam in FAMILIES for rep in (0, 1)}
    manifest_path = folder / f"G{g}" / "MANIFEST.json"
    archive = manifest_path.parent
    raw_manifest = manifest_path.read_bytes()
    if (len(raw_manifest) > 32_000_000 or
            file_sha(manifest_path) !=
            (archive / "MANIFEST.sha256").read_text().strip()):
        raise ValueError("original manifest SHA or size violated")
    manifest = json.loads(raw_manifest)
    if (manifest.get("schema") != "i3-two-phase-panel/v1"
            or manifest.get("status") != "GENERATED"
            or manifest.get("failure") is not None
            or manifest.get("planned") != GEN_COUNTS[g]
            or manifest.get("generated") != GEN_COUNTS[g]
            or len(manifest.get("files", [])) != GEN_COUNTS[g]):
        raise ValueError("partial or foreign original generation")
    seen = set()
    scores = defaultdict(lambda: [0, 0, 0])
    genotypes = {}
    paired_worlds = {}
    file_names = set()
    for idx, row in enumerate(manifest["files"]):
        fname = row.get("file")
        if (type(fname) is not str or not NAME.fullmatch(fname)
                or fname != f"life-{idx:03d}.json.gz" or fname in file_names):
            raise ValueError("unlisted, reordered or unsafe original gzip name")
        file_names.add(fname)
        path = archive / fname
        if not path.is_file() or path.is_symlink():
            raise ValueError("missing or redirected original gzip body")
        identity, life = original_packet(path.read_bytes(), row)
        if (type(identity) is not dict
                or set(identity) != {"population", "generation", "arm", "slot",
                                     "family", "repeat", "logical_world",
                                     "world_seed", "life_seed", "genome_sha256",
                                     "world_sha256", "source_sha256"}):
            raise ValueError("unsafe native original identity")
        p, generation, arm, slot, family, repeat = (
            identity[k] for k in ("population", "generation", "arm", "slot",
                                  "family", "repeat"))
        coords = (p, arm, slot, family, repeat)
        if (type(p) is not int or type(slot) is not int or
                type(generation) is not int or type(repeat) is not int or
                generation != g or coords not in expected or coords in seen):
            raise ValueError("missing/duplicate original life identity")
        seen.add(coords)
        w = worlds[p, g, family, repeat]
        if (any(identity[k] != w[k] for k in
                ("logical_world", "world_seed", "life_seed")) or
                identity["source_sha256"] != source):
            raise ValueError("native original World/seed/source not preallocated")
        N._check_native_life(
            identity, life, source, ORIGINAL_HEAD, panel["protocol"])
        if (type(life.get("trace")) is not list or
                len(life["trace"]) != life["steps_lived"]):
            raise ValueError("original native trace not complete")
        # Each World opportunity must be exactly shared across S/M/U.
        opportunity = (p, family, repeat)
        triple = (identity["world_seed"], identity["life_seed"],
                  identity["world_sha256"])
        if opportunity in paired_worlds and paired_worlds[opportunity] != triple:
            raise ValueError("World identities vary between three arms")
        paired_worlds[opportunity] = triple
        individual = (p, arm, slot)
        actual_genome = life["manifest"]["genome"]
        previous = genotypes.setdefault(individual, actual_genome)
        if previous != actual_genome or G.digest(actual_genome) != identity["genome_sha256"]:
            raise ValueError("person inherits a different genome across F0 contexts")
        cell = scores[individual]
        cell[0] += life["terminal"] == "censored"
        cell[1] += life["steps_lived"]
        cell[2] += 1
    if (seen != expected or len(paired_worlds) != 96 or
            len(genotypes) != len(allowed)*16*24 or
            set(scores) != set(genotypes) or
            any(v[2] != 6 for v in scores.values())):
        raise ValueError("incomplete 6-life individual/World matrix")
    if {path.name for path in archive.iterdir()} != file_names | {
            "MANIFEST.json", "MANIFEST.sha256"}:
        raise ValueError("unrecorded original files found in sealed archive")
    return dict(scores), genotypes, {
        "lives": len(seen), "censored": sum(x[0] for x in scores.values()),
        "dead": len(seen)-sum(x[0] for x in scores.values()),
        "manifest_sha256": file_sha(manifest_path)}


def _rand_index(key: bytes, domain: bytes, upper: int) -> int:
    ceiling = (1 << 256) - ((1 << 256) % upper)
    counter = 0
    while True:
        h = hmac.digest(key, domain + b"/" + str(counter).encode(), "sha256")
        value = int.from_bytes(h, "big")
        if value < ceiling:
            return value % upper
        counter += 1


def permutation(pop: int, generation: int, hexkey: str) -> tuple[int, ...]:
    if (type(pop) is not int or type(generation) is not int or
            not 0 <= pop < 16 or generation not in (1, 2) or
            type(hexkey) is not str or not HEX.fullmatch(hexkey)):
        raise ValueError("bad precommitted independent parental key")
    key = bytes.fromhex(hexkey)
    domain = (
        f"i3-stage8c-parent-multiplicity-control/v0/population={pop}/generation={generation}"
    ).encode("ascii")
    slots = list(range(24))
    for index in range(23, 0, -1):
        j = _rand_index(key, domain + b"/index=" + str(index).encode(), index + 1)
        slots[index], slots[j] = slots[j], slots[index]
    return tuple(slots)


def verify_parentage(panel: dict, folder: Path, generation: int,
                     parental_scores: dict, parents: dict,
                     children: dict, prior_manifest_sha: str) -> int:
    """Independent read-only reconstruction of 1,152 G1 or G2 genotypes."""
    event = parse(folder / f"SELECT_G{generation}.json")
    if (event.get("generation") != generation or
            event.get("schema") != "i3-stage8c-sealed-three-arm-parentage/v1" or
            event.get("prior_generation_manifest_sha256") != prior_manifest_sha or
            len(event.get("draws", [])) != 1152 or
            len(event.get("offspring", [])) != 1152):
        raise ValueError("partial or foreign parentage seal")
    receipts = {}
    for r in event["draws"]:
        key = (r["population"], r["arm"], r["slot"])
        if key in receipts:
            raise ValueError("duplicate parent receipt")
        receipts[key] = r
    declared = {}
    for r in event["offspring"]:
        key = (r["population"], r["arm"], r["slot"])
        if key in declared:
            raise ValueError("duplicate born offspring")
        declared[key] = r
    expected = {(p, arm, s) for p in range(16) for arm in ARMS
                for s in range(24)}
    if set(receipts) != expected or set(declared) != expected:
        raise ValueError("partial 3-arm S/M/U pedigree")
    allocations = {(r["population"], r["arm"], r["slot"]): r
                   for r in panel["draws"] if r["generation"] == generation}
    if set(allocations) != expected:
        raise ValueError("unfrozen parent/mutation allocation")
    keys = {r["population"]: r["key_hex"] for r in panel["matched_permutations"]
            if r["generation"] == generation}
    if set(keys) != set(range(16)):
        raise ValueError("missing independent population permutation")
    for p in range(16):
        selected_slots = []
        for arm in ("selected", "random_parent"):
            prev_arm = "shared" if generation == 1 else arm
            if arm == "selected":
                rank = sorted(
                    range(24), key=lambda s: (
                        -parental_scores[p, prev_arm, s][0],
                        -parental_scores[p, prev_arm, s][1], s))
            for child_slot in range(24):
                row = allocations[p, arm, child_slot]
                rng = random.Random(row["parent_draw_seed"])
                parent_slot = (
                    rng.choices(rank, weights=range(24, 0, -1), k=1)[0]
                    if arm == "selected" else rng.randrange(24))
                if arm == "selected":
                    selected_slots.append(parent_slot)
                r = receipts[p, arm, child_slot]
                if (r.get("schema") != "i3-stage8c-parent-receipt/v1" or
                        r.get("population") != p or
                        r.get("generation") != generation or
                        r.get("arm") != arm or r.get("slot") != child_slot or
                        r.get("parent_slot") != parent_slot or
                        r.get("parent_generation_arm") != prev_arm or
                        r.get("draw_seed") != row["parent_draw_seed"]):
                    raise ValueError("score ranking or uniform parent draw mismatched")
        mapping = permutation(p, generation, keys[p])
        occupied_m = []
        for child_slot in range(24):
            parent_slot = mapping[selected_slots[child_slot]]
            occupied_m.append(parent_slot)
            r = receipts[p, "matched_multiplicity", child_slot]
            canonical_slots = json.dumps(
                selected_slots, separators=(",", ":")).encode("ascii")
            if (r.get("parent_slot") != parent_slot or
                    r.get("parent_generation_arm") !=
                    ("shared" if generation == 1 else "matched_multiplicity") or
                    r.get("selected_reference_slots_sha256") !=
                    sha256(canonical_slots).hexdigest() or
                    r.get("schema") !=
                    "i3-stage8c-multiplicity-matched-parent-receipt/v0"):
                raise ValueError("matched control identity not independently permuted")
        selected_counts = Counter(selected_slots)
        matched_counts = Counter(occupied_m)
        if sorted(selected_counts.values()) != sorted(matched_counts.values()):
            raise ValueError("reproduction multiplicity not exactly matched")
    for (p, arm, child_slot), r in receipts.items():
        parent_arm = "shared" if generation == 1 else arm
        r_parent = r["parent_slot"]
        if (type(r_parent) is not int or not 0 <= r_parent < 24
                or r.get("parent_generation_arm") != parent_arm):
            raise ValueError("control parent from wrong lineage")
        drawn = allocations[p, arm, child_slot]
        if (r.get("mutation_seed") != drawn["mutation_seed"] or
                r.get("prior_generation_manifest_sha256") != prior_manifest_sha):
            raise ValueError("mutations or seal not preallocated")
        genome = parents[p, parent_arm, r_parent]
        if r["parent_genome_sha256"] != G.digest(genome):
            raise ValueError("parent digest not born in previous generation")
        offspring = G.mutate(genome, r["mutation_seed"], scale=0.1)
        if (r["offspring_genome_sha256"] != G.digest(offspring)
                or children[p, arm, child_slot] != offspring or
                declared[p, arm, child_slot].get("genome") != offspring or
                declared[p, arm, child_slot].get("genome_sha256") !=
                G.digest(offspring)):
            raise ValueError("native genome-v4 mutation or birth mismatched")
    return len(receipts)


def phase_chain(folder: Path) -> str:
    rows = (folder / "PHASES.jsonl").read_bytes().splitlines()
    if len(rows) != len(PHASES):
        raise ValueError("one of 9 irreversible G/S/R phase seals missing")
    prev = None
    for idx, raw in enumerate(rows):
        row = json.loads(raw)
        phase = PHASES[idx]
        if phase.startswith("SELECT_"):
            artifact = folder / f"{phase}.json"
        elif phase == "R_FINAL":
            artifact = folder / "R_FINAL_ENGINEERING.json"
        else:
            artifact = folder / f"G{phase[-1]}" / "MANIFEST.json"
        if (row.get("phase") != phase or row.get("ordinal") != idx
                or row.get("previous_sha256") != prev
                or row.get("payload_sha256") != file_sha(artifact)
                or row.get("chain_sha256") !=
                digest({k: v for k, v in row.items()
                        if k != "chain_sha256"})):
            raise ValueError("native original phase chain or payload changed")
        prev = row["chain_sha256"]
    return prev


def primary_from_population_counts(counts: dict) -> dict:
    """Pre-exposure statistic, independent of i3 scientific reducer."""
    expected = {(p, arm) for p in range(32) for arm in ARMS}
    if type(counts) is not dict or set(counts) != expected:
        raise ValueError("exactly 32 complete S/M/U population clusters required")
    effects, rows = [], []
    for p in range(32):
        means = {}
        censored = {}
        for arm in ARMS:
            cens, steps, n = counts[p, arm]
            if (type(cens) is not int or type(steps) is not int or
                    type(n) is not int or n != 144 or not 0 <= cens <= n or
                    not n <= steps <= 400 * n):
                raise ValueError("invalid full G2 original life cell")
            means[arm] = steps / 144
            censored[arm] = cens / 144
        d = means["selected"] - means["matched_multiplicity"]
        effects.append(d)
        rows.append({
            "population": p,
            "G2_mean_lived_steps": means,
            "G2_horizon_censored_fraction": censored,
            "G2_S_minus_M_steps": d,
            "G2_S_minus_U_steps_descriptive": means["selected"]-means["random_parent"],
            "G2_M_minus_U_steps_descriptive": means["matched_multiplicity"]-means["random_parent"],
            "G2_six_world_opportunities_per_genome": True,
        })
    mean = math.fsum(effects)/32
    sample_sd = math.sqrt(math.fsum((x-mean)**2 for x in effects)/31)
    lower = mean-T_CRIT_31*sample_sd/math.sqrt(32)
    verdict = SUCCESS if sample_sd > 0 and lower > 0 else NEGATIVE
    return {
        "status": verdict, "population_units": 32,
        "mean_G2_S_minus_M_steps": mean, "sd_G2_S_minus_M_steps": sample_sd,
        "one_sided_97_5_percent_lower_bound_steps": lower,
        "positive_populations": sum(x > 0 for x in effects),
        "negative_populations": sum(x < 0 for x in effects),
        "zero_populations": sum(x == 0 for x in effects),
        "effects": effects, "rows": rows,
        "mean_G2_S_minus_U_steps": math.fsum(
            r["G2_S_minus_U_steps_descriptive"] for r in rows)/32,
        "mean_G2_M_minus_U_steps": math.fsum(
            r["G2_M_minus_U_steps_descriptive"] for r in rows)/32,
    }


def _close(left: object, right: object) -> bool:
    return (type(left) in (int, float) and type(right) in (int, float)
            and math.isfinite(left) and math.isfinite(right)
            and abs(left - right) <= 1e-9)


def _confirm_publication(computed: dict, final: dict) -> None:
    if (final.get("schema") != "i3-stage8c-new-prospective-science-original/v1"
            or final.get("scientific_admission") is not True
            or final.get("status") != computed["status"]
            or final.get("result", {}).get("status") != computed["status"]):
        raise ValueError("published scientific verdict differs from original-body reduction")
    pub = final["result"]
    primary = pub["primary"]
    for field, actual in (
        ("population_units", 32),
        ("mean_G2_S_minus_M_steps", computed["mean_G2_S_minus_M_steps"]),
        ("sd_G2_S_minus_M_steps", computed["sd_G2_S_minus_M_steps"]),
        ("one_sided_97_5_percent_lower_bound_steps",
         computed["one_sided_97_5_percent_lower_bound_steps"]),
        ("positive_populations", computed["positive_populations"]),
        ("negative_populations", computed["negative_populations"]),
        ("zero_populations", computed["zero_populations"]),
    ):
        value = primary.get(field)
        if (value != actual if field.endswith("populations") or field == "population_units"
                else not _close(value, actual)):
            raise ValueError("published primary G2 S-M statistic differs from gzip lives")
    if (type(primary.get("all_population_contrasts")) is not list
            or len(primary["all_population_contrasts"]) != 32 or
            any(not _close(a, b) for a,b in zip(
                primary["all_population_contrasts"], computed["effects"]))):
        raise ValueError("hidden adverse/null population in public primary")
    reported = pub.get("all_32_population_analyses")
    if type(reported) is not list or len(reported) != 32:
        raise ValueError("published scientific population analysis incomplete")
    for x, y in zip(reported, computed["rows"]):
        if x.get("population") != y["population"]:
            raise ValueError("population reordered or omitted")
        for arm in ARMS:
            if (not _close(x["G2_mean_lived_steps"].get(arm),
                           y["G2_mean_lived_steps"][arm])
                    or not _close(x["G2_horizon_censored_fraction"].get(arm),
                                  y["G2_horizon_censored_fraction"][arm])):
                raise ValueError("published S/M/U original-body steps/censorship differ")
        for key in ("G2_S_minus_M_steps", "G2_S_minus_U_steps_descriptive",
                    "G2_M_minus_U_steps_descriptive"):
            if not _close(x.get(key), y[key]):
                raise ValueError("published secondary or primary population contrast changed")
    if (pub.get("native_original_lives_rehashed") != LIVES or
            pub.get("native_mutations_reconstructed") != MUTATIONS or
            not _close(pub.get("secondary_descriptive",{}).get("mean_G2_S_minus_U_steps"),
                       computed["mean_G2_S_minus_U_steps"]) or
            not _close(pub.get("secondary_descriptive",{}).get("mean_G2_M_minus_U_steps"),
                       computed["mean_G2_M_minus_U_steps"])):
        raise ValueError("original scientific reduction and census totals changed")


def audit(science_plan_path: str, science_originals_path: str) -> dict:
    root = Path(science_originals_path).resolve()
    if not root.is_dir() or Path(science_originals_path).is_symlink():
        raise ValueError("unavailable or symlinked science original root")
    plan = parse(Path(science_plan_path))
    inner, panels = _plan_controls(plan, root)
    claim = parse(root / "CLAIM.json")
    if (claim.get("scientific_admission") is not True or
            claim.get("source_git_head") != ORIGINAL_HEAD or
            claim.get("plan_sha256") != plan["allocation_sha256"] or
            (root / "FAILURE.json").exists()):
        raise ValueError("scientific original source was not independently admitted")
    if parse(root / "SCIENCE_FINAL.json").get("plan_sha256") != plan["allocation_sha256"]:
        raise ValueError("scientific report not bound to preexposure plan")
    native_root = root / "NATIVE_ORIGINALS"
    inner_core = parse(root / "INNER_CORE.json")
    if (inner_core.get("status") != TECH_PASS or
            inner_core.get("original_lives") != LIVES or
            inner_core.get("plan_sha256") != inner["allocation_sha256"] or
            inner_core.get("scientific_admission") is not False or
            len(inner_core.get("panel_chain_sha256", [])) != 2 or
            parse(native_root / "CLAIM.json").get("allocation_sha256") !=
            inner["allocation_sha256"]):
        raise ValueError("inner original G/S/R custody does not match science source")
    all_g2, seals, totals = {}, [], []
    all_mutations = 0
    for i,panel in enumerate(panels):
        if parse(native_root / f"PANEL_{i}_PLAN.json") != panel:
            raise ValueError("one frozen panel allocation differs from original archive")
        folder = native_root / f"PANEL_{i}"
        if folder.is_symlink():
            raise ValueError("unsafe native original panel link")
        meta = parse(folder / "CLAIM.json")
        core = parse(native_root / f"PANEL_{i}_CORE.json")
        if (meta.get("source_git_head") != ORIGINAL_HEAD or
                meta.get("plan_sha256") != panel["allocation_sha256"]
                or core.get("plan_sha256") != panel["allocation_sha256"]
                or core.get("status") != TECH_PASS or
                (folder / "FAILURE.json").exists()):
            raise ValueError("foreign or partial original G/S/R panel")
        founders = parse(folder / "FOUNDERS.json")
        if len(founders) != 384:
            raise ValueError("wrong founder genotype count")
        root_by_gen = {}
        scores_by_gen = {}
        for g in range(3):
            scores, genotypes, generation = scan_generation(panel, folder, g)
            totals.append(generation)
            scores_by_gen[g] = scores
            root_by_gen[g] = genotypes
            if g == 0:
                found = {(r["population"], "shared", r["slot"]): r
                         for r in founders}
                srcfound = {(r["population"], "shared", r["slot"]): r
                            for r in panel["founders"]}
                if set(found) != set(genotypes) or set(srcfound) != set(genotypes):
                    raise ValueError("one source-locked founder missing")
                for key,genome in genotypes.items():
                    f, src = found[key], srcfound[key]
                    if (f["genome"] != genome or
                            f["genome_seed"] != src["genome_seed"] or
                            G.generation_zero(src["genome_seed"]) != genome or
                            f["genome_sha256"] != G.digest(genome)):
                        raise ValueError("G0 genome differs from its precommitted founder seed")
            else:
                seal = file_sha(folder / f"G{g-1}" / "MANIFEST.json")
                all_mutations += verify_parentage(
                    panel, folder, g, scores_by_gen[g-1],
                    root_by_gen[g-1], genotypes, seal)
        for p in range(16):
            for arm in ARMS:
                c, steps, n = scores_by_gen[2][p, arm, 0]
                # The population total includes all 24 genotypes and 6 F0 lives each.
                cells = [scores_by_gen[2][p, arm, s] for s in range(24)]
                globalpop = i*16+p
                all_g2[globalpop,arm] = (
                    sum(z[0] for z in cells),
                    sum(z[1] for z in cells),
                    sum(z[2] for z in cells))
        chain = phase_chain(folder)
        if (chain != core.get("phase_chain_sha256") or
                chain != inner_core["panel_chain_sha256"][i]):
            raise ValueError("original phase seal differs from source exact published core")
        seals.append(chain)
    if (len(seals) != 2 or len(set(seals)) != 2
            or sum(x["lives"] for x in totals) != LIVES
            or all_mutations != MUTATIONS):
        raise ValueError("incomplete original-life audit or mutation reconstruction")
    calculated = primary_from_population_counts(all_g2)
    final = parse(root / "SCIENCE_FINAL.json")
    _confirm_publication(calculated, final)
    if (final.get("both_engineering_receipts_sha256") !=
            digest(plan["engineering_receipts"]) or
            final.get("source_git_head") != ORIGINAL_HEAD or
            final.get("source_files_sha256") != plan["source_files_sha256"] or
            final.get("original_native_lives") != LIVES or
            final.get("preexposure_g2_worlds_sha256") !=
            plan["g2_heldout_worlds_sha256"]):
        raise ValueError("published scientific original body not tied to allocation")
    return {
        "schema": SCHEMA, "status": "READ_ONLY_32K_ORIGINALS_REPRODUCED",
        "scientific_status": calculated["status"],
        "source_git_head": ORIGINAL_HEAD, "run_id": ORIGINAL_RUN_ID,
        "science_allocation_sha256": plan["allocation_sha256"],
        "heldout_worlds_sha256": plan["g2_heldout_worlds_sha256"],
        "native_original_lives_rehashed": LIVES,
        "mutated_parentage_reconstructed": all_mutations,
        "phase_chains_verified": seals,
        "per_generation_native_lives": [GEN_COUNTS[g]*2 for g in range(3)],
        "population_units": POPULATIONS,
        "mean_G2_S_minus_M_steps": calculated["mean_G2_S_minus_M_steps"],
        "population_sd_steps": calculated["sd_G2_S_minus_M_steps"],
        "one_sided_97_5_percent_lower_bound_steps":
            calculated["one_sided_97_5_percent_lower_bound_steps"],
        "positive_populations": calculated["positive_populations"],
        "negative_populations": calculated["negative_populations"],
        "zero_populations": calculated["zero_populations"],
        "all_population_contrasts": calculated["effects"],
        "mean_G2_S_minus_U_steps_descriptive": calculated["mean_G2_S_minus_U_steps"],
        "mean_G2_M_minus_U_steps_descriptive": calculated["mean_G2_M_minus_U_steps"],
        "new_worlds": 0, "new_lives": 0,
        "limits": "INTERNAL_READONLY_NO_MOTOR_REPLAY_NO_EXTERNAL_ATTESTATION_NO_PROOF_OF_CAUSAL_GENE",
    }


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("read-only: python -m i3.lab.stage8c_independent_original_audit PLAN.json ORIGINALS_ROOT")
    report = audit(sys.argv[1], sys.argv[2])
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
