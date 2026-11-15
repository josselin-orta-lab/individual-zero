"""Prospective native I3 Stage6-light G0 engineering transport (ADR-0022).

This is a REAL native G0 transport when separately allocated and launched,
not a toy original generator. It cannot select G1/G2, rehearse the complete
nine-phase Stage6 design, admit science or activate I3. No allocation or World
is created by importing this module.

Usage after this source has been merged and pinned:
  PYTHONPATH=src python -m i3.lab.stage6_light_native_g0_transport allocate HEAD SOURCE_MAP_SHA OUTSIDE_REPO.json
  # publish the plan and its digest to an immutable, pre-exposure internal record
  PYTHONPATH=src python -m i3.lab.stage6_light_native_g0_transport run PLAN.json OUTSIDE_REPO_DIR PLAN_SHA256

The old method-v1 deny-all contract is NEVER edited or used as a live permit.
"""
from __future__ import annotations

from hashlib import sha256
import hmac
import json
import os
from pathlib import Path
import re
import secrets
import subprocess
import sys

SCHEMA = "i3-stage6-light-native-g0-engineering-plan/v1"
PROTOCOL = "i3-stage6-light-g0-engineering-native-funded-v2/v1"
SCOPE = "ENGINEERING_G0_ONLY_NOT_FULL_STAGE6_REHEARSAL"
FAMILIES = ("stable", "depletion", "pulse")
POPS = 16
FOUNDERS = 24
HORIZON = 400
WORLD_COUNT = POPS * len(FAMILIES) * 2
G0_LIVES = WORLD_COUNT * FOUNDERS
ROOT = Path(__file__).resolve().parents[3]
METHOD = ROOT / "src/i3/docs/studies/stage6-light-preparation/STAGE6_LIGHT_PROTOCOL_METHOD_V1.json"
DIRECTION = ROOT / "src/i3/docs/studies/stage6-light-preparation/STAGE6_LIGHT_OWNER_RESEARCH_DIRECTION_2026-11-15.json"
DIGEST = re.compile(r"[0-9a-f]{64}\Z")
COMMIT = re.compile(r"[0-9a-f]{40}\Z")
MASK = (1 << 60) - 1
BASE = {"world_index": 1 << 60, "world_seed": 2 << 60,
        "life_seed": 3 << 60, "genome_seed": 4 << 60}


def _canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def _sha(value: object) -> str:
    return sha256(_canonical(value)).hexdigest()


def _pins() -> tuple[str, str]:
    """Read owner authority, while asserting historic method v1 is still inert."""
    m = json.loads(METHOD.read_bytes())
    a = m.get("authorization", {})
    denied = ("worlds_allowed", "cohorts_allowed", "engineering_rehearsal_allowed",
              "science_admission_allowed", "auto_start_allowed",
              "adr0017_lineage_exception_accepted")
    unbound = ("owner_decision_sha", "owner_authorized_world_indices",
               "assigned_world_seeds", "assigned_founder_seeds",
               "execution_source_sha", "execution_transport_fingerprint",
               "independent_allocation_manifest_sha256",
               "full_scale_python311_rehearsal_sha",
               "full_scale_python312_rehearsal_sha")
    if (m.get("schema") != "i3-stage6-light-method-preauth/v1" or
            m.get("status") != "METHOD_FIXED_PREAUTH_NOT_EXECUTABLE" or
            set(a) != set(denied + unbound) or
            any(a[k] is not False for k in denied) or
            any(a[k] is not None for k in unbound)):
        raise PermissionError("historic Stage6 method must remain deny-all")
    d = json.loads(DIRECTION.read_bytes())
    allowed = d.get("applies_to", {})
    req = d.get("prospective_execution_requirements", {})
    if (d.get("schema") != "i3-owner-prospective-research-direction/v1" or
            d.get("decision") != "OWNER_AUTHORIZES_NEW_PROSPECTIVE_I3_EXPERIMENTS" or
            allowed.get("generation") != "I3" or
            allowed.get("engineering_prospective_experiments_authorized") is not True or
            allowed.get("stage6_light_gsr_lineage_exception_adr0017_accepted") is not True or
            allowed.get("previously_consumed_worlds_allowed") is not False or
            allowed.get("legacy_cohort_replay_allowed") is not False or
            req.get("frozen_method_v1_remains_immutable") is not True):
        raise PermissionError("ADR-0022 does not match this bounded engineering scope")
    return sha256(METHOD.read_bytes()).hexdigest(), sha256(DIRECTION.read_bytes()).hexdigest()


def _hex(value: object, pattern: re.Pattern, label: str) -> str:
    if type(value) is not str or pattern.fullmatch(value) is None or len(set(value)) == 1:
        raise ValueError(f"invalid {label}")
    return value


def _seed(root: bytes, domain: str, key: str) -> int:
    message = f"i3-stage6-native-g0-engineering-v1/{domain}/{key}".encode("ascii")
    bits = int.from_bytes(hmac.new(root, message, sha256).digest()[:8], "big")
    return BASE[domain] + (bits & MASK)


def make_plan(root_hex: str, source_git_head: str, source_files_sha256: str) -> dict:
    """Deterministic allocation from one new OS-generated root, before exposure.

    This function is pure and can be tested with a clearly synthetic root.
    A real root is minted ONLY by the explicit 'allocate' command.
    """
    _hex(root_hex, DIGEST, "allocation root")
    _hex(source_git_head, COMMIT, "source commit")
    _hex(source_files_sha256, DIGEST, "native source map")
    method_sha, direction_sha = _pins()
    root = bytes.fromhex(root_hex)
    worlds = []
    for p in range(POPS):
        for f, family in enumerate(FAMILIES):
            for repeat in range(2):
                key = f"{p}/{family}/{repeat}"
                worlds.append({
                    "population": p, "generation": 0, "family": family,
                    "repeat": repeat, "logical_world": ((p * 3) * 3 + f) * 2 + repeat,
                    "world_index": _seed(root, "world_index", key),
                    "world_seed": _seed(root, "world_seed", key),
                    "life_seed": _seed(root, "life_seed", key),
                })
    founders = [
        {"population": p, "slot": slot,
         "genome_seed": _seed(root, "genome_seed", f"{p}/{slot}")}
        for p in range(POPS) for slot in range(FOUNDERS)
    ]
    # Namespace separation plus collision detection; no retry or post-hoc reroll.
    numbers = [row[k] for row in worlds for k in
               ("world_index", "world_seed", "life_seed")]
    numbers.extend(row["genome_seed"] for row in founders)
    if (len(worlds) != WORLD_COUNT or len(founders) != POPS * FOUNDERS or
            len(numbers) != len(set(numbers)) or
            any(type(v) is not int or v < 1 << 60 or v >= 5 << 60
                for v in numbers)):
        raise RuntimeError("allocation collision or namespace error: abandon root")
    plan = {
        "schema": SCHEMA, "scope": SCOPE, "status": "ALLOCATED_NOT_EXPOSED",
        "reference": "P1.3 funded-v2", "decision_policy": "reference",
        "protocol": PROTOCOL, "horizon": HORIZON,
        "source_git_head": source_git_head,
        "source_files_sha256": source_files_sha256,
        "method_sha256": method_sha, "owner_direction_sha256": direction_sha,
        "allocation_root_hex": root_hex, "worlds": worlds, "founders": founders,
        "worlds_planned": WORLD_COUNT, "g0_lives_planned": G0_LIVES,
        "full_stage6_rehearsal_complete": False, "scientific_admission": False,
        "worlds_opened_at_allocation": 0, "lives_created_at_allocation": 0,
        "provenance": "INTERNAL_PROSPECTIVE_NOT_EXTERNALLY_ATTESTED",
        "no_retry": True,
    }
    plan["allocation_sha256"] = _sha(plan)
    return plan


def verify_plan(plan: object) -> dict:
    if type(plan) is not dict or plan.get("schema") != SCHEMA:
        raise ValueError("foreign or missing Stage6 engineering plan")
    expected = make_plan(plan.get("allocation_root_hex"),
                         plan.get("source_git_head"),
                         plan.get("source_files_sha256"))
    if _canonical(expected) != _canonical(plan):
        raise ValueError("plan, seeds, source, status or digest changed")
    return plan


def g0_cases(plan: dict) -> list[dict]:
    verify_plan(plan)
    worlds = {(w["population"], w["family"], w["repeat"]): w
              for w in plan["worlds"]}
    result = []
    for founder in plan["founders"]:
        p, slot = founder["population"], founder["slot"]
        for family in FAMILIES:
            for repeat in range(2):
                w = worlds[p, family, repeat]
                result.append({
                    "population": p, "generation": 0, "arm": "shared",
                    "slot": slot, "family": family, "repeat": repeat,
                    "logical_world": w["logical_world"],
                    "world_index": w["world_index"],
                    "world_seed": w["world_seed"], "life_seed": w["life_seed"],
                    "genome_seed": founder["genome_seed"],
                })
    if len(result) != G0_LIVES or len(set(
            (r["population"], r["slot"], r["family"], r["repeat"])
            for r in result)) != G0_LIVES:
        raise ValueError("G0 case coverage mismatch")
    return result


def _verify_checkout(plan: dict) -> None:
    """No World is imported until source-exact, clean checkout is verified."""
    if sys.version_info[:2] not in ((3, 11), (3, 12)):
        raise PermissionError("engineering rehearsal requires Python 3.11 or 3.12")
    for args, expected in ((["rev-parse", "HEAD"], plan["source_git_head"]),):
        done = subprocess.run(["git", *args], cwd=ROOT, text=True,
                              capture_output=True, check=True, timeout=15)
        if done.stdout.strip() != expected:
            raise PermissionError("Git HEAD differs from prospectively pinned source")
    status = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=ROOT, text=True, capture_output=True, check=True, timeout=15)
    if status.stdout.strip():
        raise PermissionError("dirty source checkout may not create lives")
    from i3.runtime.provenance import source_snapshot
    source = source_snapshot()
    if (source["git_head"] != plan["source_git_head"] or
            source["sha256"] != plan["source_files_sha256"] or
            source["working_tree_dirty"] is not False):
        raise PermissionError("native Python source bytes differ from frozen plan")


def _claim(root: Path, plan: dict) -> None:
    """Atomic no-retry claim. Even a process crash must not release this path."""
    root.mkdir()  # exist_ok=False, parent must already exist
    receipt = {
        "schema": "i3-stage6-native-g0-engineering-claim/v1",
        "plan_sha256": plan["allocation_sha256"],
        "source_git_head": plan["source_git_head"],
        "status": "CLAIMED_NO_RETRY_EVEN_IF_PARTIAL",
    }
    with (root / "CLAIM.json").open("xb") as file:
        file.write(_canonical(receipt))
        file.flush()
        os.fsync(file.fileno())


def run_g0(plan: dict, archive_dir: str | Path, published_sha256: str) -> dict:
    """Generate 2,304 native G0 engineering originals, once, with no G1/R.

    Publication of the plan hash BEFORE calling this method is an operator
    obligation. Matching a caller-supplied hash proves equality, NOT time.
    """
    verify_plan(plan)
    if (type(published_sha256) is not str or
            published_sha256 != plan["allocation_sha256"]):
        raise PermissionError("pre-exposure committed plan digest mismatch")
    root = Path(archive_dir).resolve()
    if root.is_relative_to(ROOT.resolve()):
        raise PermissionError("archive must live outside the Git checkout")
    _verify_checkout(plan)
    cases = g0_cases(plan)
    _claim(root, plan)  # before first possible native World
    from i3.lab import p2_ecologies, two_phase_panel
    from i3.modules.genome import generation_zero, digest as genome_digest
    from i3.runtime.life import run_life

    def run_case(case: dict) -> dict:
        genome = generation_zero(case["genome_seed"])
        spec = p2_ecologies._generate_ecology(
            case["family"], case["world_seed"], prospective_stage6=True)
        life = run_life(genome, spec, case["life_seed"], HORIZON,
                        keep_trace=True, protocol=PROTOCOL,
                        decision_policy="reference")
        source = life["manifest"]["source"]
        accounting = life["cognitive_accounting"]
        if (source["sha256"] != plan["source_files_sha256"] or
                source["git_head"] != plan["source_git_head"] or
                source["working_tree_dirty"] is not False or
                life["manifest"]["execution_model"] != "i3-funded-v2" or
                life["manifest"]["protocol"] != PROTOCOL or
                life["genome"] != genome_digest(genome) or
                life["manifest"]["world_sha256"] != p2_ecologies.fingerprint(spec) or
                life["life_seed"] != case["life_seed"] or
                accounting["status"] != "SETTLED_FOR_DECLARED_WORK" or
                accounting["shortfall_steps"] != 0 or
                any(accounting["totals"][c]["unpaid"] > 1e-12
                    for c in ("energy", "vigilance")) or
                not 0 < life["steps_lived"] <= HORIZON or
                (life["terminal"] == "censored") !=
                (life["steps_lived"] == HORIZON)):
            raise ValueError("native life source, body, billing or identity mismatch")
        return life

    generation = two_phase_panel.generate(cases, run_case, root / "G0")
    receipt = {
        "schema": "i3-stage6-native-g0-engineering-receipt/v1",
        "status": ("ENGINEERING_G0_SEALED_NOT_FULL_REHEARSAL"
                   if generation["status"] == "GENERATED" and
                   generation["generated"] == G0_LIVES
                   else "ENGINEERING_FAILURE_NOT_A_DEATH_NO_RETRY"),
        "plan_sha256": plan["allocation_sha256"],
        "source_git_head": plan["source_git_head"],
        "planned": G0_LIVES, "generated": generation["generated"],
        "generation_manifest_sha256": sha256(
            (root / "G0/MANIFEST.json").read_bytes()).hexdigest(),
        "full_stage6_rehearsal_complete": False,
        "scientific_admission": False, "stage2_scientific_verdict": "NOT_ISSUED",
        "no_retry": True,
    }
    with (root / "G0_ENGINEERING_RECEIPT.json").open("xb") as file:
        file.write(_canonical(receipt))
        file.flush()
        os.fsync(file.fileno())
    return receipt


def main() -> None:
    if len(sys.argv) == 5 and sys.argv[1] == "allocate":
        _, _, head, source_hash, output = sys.argv
        # No reroll on collisions, no output overwrite, no live World.
        plan = make_plan(secrets.token_hex(32), head, source_hash)
        with Path(output).open("x", encoding="utf-8") as file:
            json.dump(plan, file, sort_keys=True, indent=2)
            file.write("\n")
        print(json.dumps({"status": plan["status"],
                          "scope": SCOPE, "allocation_sha256": plan["allocation_sha256"],
                          "worlds_opened": 0, "lives_created": 0}, sort_keys=True))
    elif len(sys.argv) == 3 and sys.argv[1] == "verify":
        plan = verify_plan(json.loads(Path(sys.argv[2]).read_text(encoding="utf-8")))
        print(json.dumps({"status": plan["status"],
                          "allocation_sha256": plan["allocation_sha256"],
                          "g0_lives_planned": G0_LIVES}, sort_keys=True))
    elif len(sys.argv) == 5 and sys.argv[1] == "run":
        plan = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
        print(json.dumps(run_g0(plan, sys.argv[3], sys.argv[4]), sort_keys=True))
    else:
        raise SystemExit("usage: stage6_light_native_g0_transport allocate HEAD SOURCE_SHA PLAN.json | verify PLAN.json | run PLAN.json OUT_DIR COMMITTED_SHA256")


if __name__ == "__main__":
    main()
