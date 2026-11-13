"""Stage-6-light toy transport: NO World imports, no birth, no live runner.

This module is a deliberately NON-EXECUTABLE rehearsal of data plumbing.  It
cannot mint scientific indices, allocate real seeds, open a World or authorize
an engineering/scientific cohort.  Toy receipt contents are invented by tests,
not observations from Individual Zero.  Any actual lineage needs a separate,
explicitly authorised and source-locked implementation under ADR-0017.
"""
from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from hashlib import sha256
from itertools import product
import json
from math import isfinite
from pathlib import Path
import random

METHOD = Path(__file__).resolve().parents[1] / "docs/studies/stage6-light-preparation/STAGE6_LIGHT_PROTOCOL_METHOD_V1.json"
KIND = "TOY_ONLY_NO_WORLD"
FAMILIES = ("stable", "depletion", "pulse")
ARMS = ("selected", "random_parent")
GENE_FIELDS = ("beta_u_eff", "omega", "temperament.affiliation", "temperament.reward_sensitivity")
RECEIPT_FIELDS = frozenset({
    "kind", "population", "generation", "arm", "slot", "family", "repeat",
    "logical_world", "censored", "steps_lived",
})
GENE_ROW_FIELDS = frozenset({"kind", "population", "arm", "slot", *GENE_FIELDS})
# Metadata-only conservative exclusions; NOT a complete future-source disjointness audit.
HISTORIC_RESERVED = (
    range(100, 130), range(2_000, 2_100), range(10_000, 10_400),
    range(30_000, 30_200), range(60_000, 60_100),
    range(90_000, 91_000), range(100_000, 100_100),
    range(300_000, 331_000), range(1_000_200, 1_000_300),
    range(1_200_000, 1_200_200),
)


def _digest(value: object) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=True, allow_nan=False).encode("ascii")).hexdigest()


def _inert(method: dict) -> dict:
    """This exact schema can NEVER be promoted into a live launch ticket."""
    if method.get("schema") != "i3-stage6-light-method-preauth/v1" or method.get("status") != "METHOD_FIXED_PREAUTH_NOT_EXECUTABLE" or method.get("phase") != "design_only":
        raise PermissionError("not the fixed non-executable method")
    authorization = method.get("authorization")
    if not isinstance(authorization, dict):
        raise PermissionError("missing denial record")
    false_keys = (
        "worlds_allowed", "cohorts_allowed", "engineering_rehearsal_allowed",
        "science_admission_allowed", "auto_start_allowed", "adr0017_lineage_exception_accepted",
    )
    null_keys = (
        "owner_decision_sha", "owner_authorized_world_indices", "assigned_world_seeds",
        "assigned_founder_seeds", "execution_source_sha", "execution_transport_fingerprint",
        "independent_allocation_manifest_sha256", "full_scale_python311_rehearsal_sha",
        "full_scale_python312_rehearsal_sha",
    )
    if set(authorization) != set(false_keys + null_keys) or any(authorization[k] is not False for k in false_keys) or any(authorization[k] is not None for k in null_keys):
        raise PermissionError("a proposed World, owner lift or rehearsal is not authorised")
    custody = method.get("custody", {})
    if custody.get("rehearsal_worlds_and_lives_now_allowed") is not False or custody.get("scientific_worlds_and_lives_now_allowed") is not False or custody.get("per_generation_selection_requires_separate_adr0017_acceptance") is not True:
        raise PermissionError("lineage-specific release is absent")
    design = method.get("design", {})
    plan = method.get("plan", {})
    if (design.get("populations"), design.get("founders_per_population"), design.get("generations"),
        design.get("arms"), design.get("families"), design.get("repeats_per_family"),
        design.get("horizon_steps"), design.get("g0_shared_one_original")) != (
        16, 24, [0, 1, 2], list(ARMS), list(FAMILIES), 2, 400, True):
        raise ValueError("toy adapter only supports exact immutable Stage-6-light v1 design")
    if (plan.get("logical_world_coordinates"), plan.get("genotype_founders"),
        plan.get("total_lives_if_later_authorized"), plan.get("actual_world_indices_assigned")) != (288, 384, 11520, False):
        raise ValueError("the synthetic schedule does not match the v1 method")
    return method


def load_method() -> dict:
    return _inert(json.loads(METHOD.read_text(encoding="utf-8")))


def logical_world(population: int, generation: int, family: str, repeat: int) -> int:
    if (type(population) is not int or not 0 <= population < 16 or
        type(generation) is not int or not 0 <= generation < 3 or
        family not in FAMILIES or type(repeat) is not int or not 0 <= repeat < 2):
        raise ValueError("invalid logical coordinate (this is not a world index)")
    return ((population * 3 + generation) * 3 + FAMILIES.index(family)) * 2 + repeat


def expected_keys(generation: int) -> tuple[tuple[int, int, str, int, str, int], ...]:
    if type(generation) is not int or generation not in (0, 1, 2):
        raise ValueError("unknown toy generation")
    arms = ("shared",) if generation == 0 else ARMS
    return tuple((p, generation, arm, slot, family, repeat)
                 for p, arm, slot, family, repeat in product(
                     range(16), arms, range(24), FAMILIES, range(2)))


def preview_unassigned_allocation() -> dict:
    """288 logical locations; no real World, WorldSpec, life seed or genome seed."""
    load_method()
    coordinates = [
        {"population": p, "generation": g, "family": f, "repeat": r,
         "logical_coordinate": logical_world(p, g, f, r),
         "physical_world_seed": None, "physical_life_seed": None}
        for p, g, f, r in product(range(16), range(3), FAMILIES, range(2))
    ]
    if [row["logical_coordinate"] for row in coordinates] != list(range(288)):
        raise RuntimeError("logical coordinate coverage or ordering failed")
    return {
        "status": "SYMBOLIC_ONLY_NOT_ALLOCATED",
        "science_verdict": "NOT_ISSUED",
        "new_worlds_opened": 0, "actual_lives_executed": 0,
        "world_indices_assigned": False,
        "independent_world_sampling_verified": False,
        "historical_seed_disjointness_verified": False,
        "founder_seeds_assigned": None,
        "parent_or_mutation_seeds_assigned": None,
        "founder_seed_slots": 384,
        "parent_draw_slots": 16 * 2 * 2 * 24,
        "mutation_slots": 16 * 2 * 2 * 24,
        "life_seed_slots": 288,
        "coordinates": coordinates,
        "coordinate_sha256": _digest([(r["population"], r["generation"], r["family"],
                                         r["repeat"], r["logical_coordinate"]) for r in coordinates]),
    }


def inspect_mock_world_seed_mapping(entries: list[dict], *, toy_only: bool) -> dict:
    """Reject obvious collisions in a MOCK table; never certify real independence.

    Testing invented seed values does not allocate them.  Freshness and iid
    assumptions need an independent prospective review and owner authorisation.
    """
    load_method()
    if toy_only is not True or not isinstance(entries, list) or len(entries) != 288:
        raise PermissionError("mock-only input and exactly 288 rows required")
    keys, seeds = set(), set()
    for item in entries:
        if set(item) != {"logical_coordinate", "mock_seed", "kind"} or item["kind"] != KIND:
            raise ValueError("foreign candidate metadata is not admitted")
        coord, seed = item["logical_coordinate"], item["mock_seed"]
        if type(coord) is not int or not 0 <= coord < 288 or type(seed) is not int or seed < 0:
            raise ValueError("invalid mock coordinate or seed")
        if coord in keys or seed in seeds:
            raise ValueError("duplicate mock coordinate or seed")
        if any(seed in forbidden for forbidden in HISTORIC_RESERVED):
            raise ValueError("mock seed intersects a known historical exclusion")
        keys.add(coord)
        seeds.add(seed)
    if keys != set(range(288)):
        raise ValueError("incomplete mock coordinate coverage")
    return {"status": "TOY_SHAPE_CHECK_ONLY_NOT_ALLOCATED", "count": 288,
            "historical_collision_check": "PARTIAL_KNOWN_RANGES_ONLY",
            "independence_certified": False, "scientific_permission": False,
            "worlds_opened": 0, "lives_executed": 0}


class SyntheticLineageTransport:
    """A state machine for fake receipts only, not an engine or World runner."""

    def __init__(self) -> None:
        self._method = load_method()
        self.phase = "G0"
        self._rows: dict[int, tuple[dict, ...]] = {}
        self._seals: dict[int, str] = {}
        self._choices: dict[int, tuple[dict, ...]] = {}
        self._choice_hashes: dict[int, str] = {}

    def _expect(self, phase: str) -> None:
        if self.phase != phase:
            self.phase = "FAILED_NO_RETRY"
            raise RuntimeError("out-of-order synthetic phase: no restart")

    def seal_generation(self, generation: int, receipts: list[dict]) -> dict:
        self._expect(f"G{generation}")
        try:
            if not isinstance(receipts, list) or len(receipts) != len(expected_keys(generation)):
                raise ValueError("missing or additional fake lives")
            seen = set()
            checked = []
            for src in receipts:
                if not isinstance(src, dict) or set(src) != RECEIPT_FIELDS or src["kind"] != KIND:
                    raise ValueError("unexpected, real or leaky receipt type")
                p, g, arm, slot, family, rep = (src[k] for k in
                    ("population", "generation", "arm", "slot", "family", "repeat"))
                if (type(p) is not int or not 0 <= p < 16 or
                    type(g) is not int or g != generation or
                    arm not in (("shared",) if g == 0 else ARMS) or
                    type(slot) is not int or not 0 <= slot < 24 or
                    family not in FAMILIES or type(rep) is not int or not 0 <= rep < 2):
                    raise ValueError("foreign synthetic coordinate")
                key = (p, g, arm, slot, family, rep)
                if key in seen:
                    raise ValueError("duplicate synthetic life coordinate")
                seen.add(key)
                if src["logical_world"] != logical_world(p, g, family, rep):
                    raise ValueError("World opportunity mismatch even in toy record")
                censored, steps = src["censored"], src["steps_lived"]
                if (type(censored) is not bool or type(steps) is not int or
                    not 1 <= steps <= 400 or (censored and steps != 400)):
                    raise ValueError("invalid toy persistence metric")
                checked.append(deepcopy(src))
            if seen != set(expected_keys(generation)):
                raise ValueError("incomplete synthetic coverage")
            if generation > 0:
                self._verify_choices(generation)
                self._verify_seal(generation-1)
            checked.sort(key=lambda x: (x["population"], x["arm"], x["slot"],
                                       FAMILIES.index(x["family"]), x["repeat"]))
            sealed = tuple(checked)
            h = _digest(sealed)
            self._rows[generation] = sealed
            self._seals[generation] = h
            self.phase = "S1" if generation == 0 else "S2" if generation == 1 else "R_FINAL"
            return {"status": "TOY_GENERATION_SEALED_NO_WORLD", "generation": generation,
                    "receipt_count": len(sealed), "sha256": h,
                    "actual_worlds": 0, "actual_lives": 0, "science_verdict": "NOT_ISSUED"}
        except Exception:
            self.phase = "FAILED_NO_RETRY"
            raise

    def _verify_seal(self, generation: int) -> None:
        if generation not in self._seals or self._seals[generation] != _digest(self._rows[generation]):
            self.phase = "FAILED_NO_RETRY"
            raise ValueError("synthetic receipt seal has changed")

    def _verify_choices(self, generation: int) -> None:
        if (generation not in self._choice_hashes or
            self._choice_hashes[generation] != _digest({
                "prior_seal": self._seals[generation-1],
                "parent_slots": self._choices[generation],
            })):
            self.phase = "FAILED_NO_RETRY"
            raise ValueError("synthetic parent-choice receipt changed")

    def select_next(self, generation: int) -> dict:
        """Only toy persistence for selected, zero fitness reads for random arm."""
        if generation not in (0, 1):
            self.phase = "FAILED_NO_RETRY"
            raise ValueError("selection allowed only G0->G1 and G1->G2")
        self._expect(f"S{generation+1}")
        try:
            self._verify_seal(generation)
            if generation > 0:
                self._verify_choices(generation)
                self._verify_seal(generation-1)
            prev = self._rows[generation]
            by_pop: dict[int, list[dict]] = defaultdict(list)
            for row in prev:
                if row["arm"] in ("shared", "selected"):
                    by_pop[row["population"]].append(row)
            picks = []
            for pop in range(16):
                selected = by_pop[pop]
                if len(selected) != 24 * 6:
                    raise ValueError("selection lacks complete sealed parents")
                # Read the *minimal* persistence amounts for selected only.
                grouped = defaultdict(list)
                for row in selected:
                    grouped[row["slot"]].append(row)
                ranked = sorted(range(24), key=lambda slot: (
                    -sum(row["censored"] for row in grouped[slot]),
                    -sum(row["steps_lived"] for row in grouped[slot]), slot))
                for arm in ARMS:
                    for child_slot in range(24):
                        # This is a toy-only RNG, not a scientific seed or allocation.
                        rng = random.Random("TOY_NO_WORLD:" +
                            _digest((pop, generation+1, arm, child_slot)))
                        if arm == "selected":
                            parent = rng.choices(ranked, weights=range(24, 0, -1), k=1)[0]
                        else:
                            # No fitness read or rank consulted by random_parent.
                            parent = rng.randrange(24)
                        picks.append({"population": pop, "arm": arm,
                                      "offspring_slot": child_slot,
                                      "parent_slot": parent})
            self._choices[generation+1] = tuple(picks)
            h = _digest({"prior_seal": self._seals[generation], "parent_slots": picks})
            self._choice_hashes[generation+1] = h
            self.phase = f"G{generation+1}"
            return {"status": "TOY_PARENT_CHOICES_ONLY", "generation": generation+1,
                    "parent_count": len(picks), "parent_choices_sha256": h,
                    "parent_slots": deepcopy(picks),
                    "real_parent_seeds_assigned": False, "worlds_opened": 0,
                    "lives_executed": 0, "science_verdict": "NOT_ISSUED"}
        except Exception:
            self.phase = "FAILED_NO_RETRY"
            raise

    def final_synthetic_signs(self, rows: list[dict]) -> dict:
        """Pure toy expression table; cannot pronounce a scientific verdict."""
        self._expect("R_FINAL")
        try:
            for gen in (0, 1, 2):
                self._verify_seal(gen)
                if gen > 0:
                    self._verify_choices(gen)
            if not isinstance(rows, list) or len(rows) != 16 * 2 * 24:
                raise ValueError("incomplete toy G2 expression table")
            observations: dict[tuple[int, str], list[dict]] = defaultdict(list)
            seen = set()
            for src in rows:
                if not isinstance(src, dict) or set(src) != GENE_ROW_FIELDS or src["kind"] != KIND:
                    raise ValueError("foreign or post-hoc toy gene field")
                p, arm, slot = src["population"], src["arm"], src["slot"]
                if (type(p) is not int or not 0 <= p < 16 or arm not in ARMS or
                    type(slot) is not int or not 0 <= slot < 24 or (p, arm, slot) in seen):
                    raise ValueError("invalid, duplicate or missing G2 toy identity")
                seen.add((p, arm, slot))
                if any(type(src[gene]) not in (int, float) or not isfinite(src[gene])
                       for gene in GENE_FIELDS):
                    raise ValueError("non-finite toy gene value")
                if not 0 <= src["beta_u_eff"] <= 3:
                    raise ValueError("toy expressed gene outside reference bounds")
                observations[p, arm].append(src)
            if len(seen) != 16 * 2 * 24:
                raise ValueError("incomplete expression table")
            contrasts = {field: [] for field in GENE_FIELDS}
            for p in range(16):
                for field in GENE_FIELDS:
                    a = sum(x[field] for x in observations[p, "selected"]) / 24
                    b = sum(x[field] for x in observations[p, "random_parent"]) / 24
                    # Exact zeros only, no float epsilon chosen after looking.
                    contrasts[field].append(a-b)
            def signs(values: list[float]) -> dict:
                positive = sum(x > 0 for x in values)
                negative = sum(x < 0 for x in values)
                return {"positive": positive, "negative": negative,
                        "zero": 16 - positive - negative,
                        "concordant": max(positive, negative)}
            counter = {name: signs(values) for name, values in contrasts.items()}
            neutral_hits = sum(counter[marker]["concordant"] >= 13 for marker in GENE_FIELDS[1:])
            status = ("TOY_INVALID_SENTINEL" if neutral_hits >= 2 else
                      "TOY_SIGN_CONCORDANCE" if counter["beta_u_eff"]["concordant"] >= 13
                      else "TOY_NO_SIGN_CONCORDANCE")
            result = {"status": status, "science_verdict": "NOT_ISSUED",
                      "population_count": 16, "neutral_marker_warnings": neutral_hits,
                      "statistics": counter,
                      "contrasts": contrasts,
                      "worlds_opened": 0, "lives_executed": 0,
                      "input_scope": KIND}
            self.phase = "DONE_TOY_ONLY"
            return result
        except Exception:
            self.phase = "FAILED_NO_RETRY"
            raise

    def open_world(self, *args, **kwargs) -> None:
        raise PermissionError("Stage-6-light does not permit any World or cohort")

    def authorize_science(self, *args, **kwargs) -> None:
        raise PermissionError("method document and toy transport cannot mint owner authority")

    def run_life(self, *args, **kwargs) -> None:
        raise PermissionError("no individual can live inside a toy receipt transport")
