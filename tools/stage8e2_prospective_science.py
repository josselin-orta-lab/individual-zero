"""Stage8-E2 outer SCIENTIFIC envelope around the frozen native data generator.

This is NOT an I3 engine file. The unmodified source-exact native engine at
03faff4b... has already passed two independently original-audited technical
repetitions (run 44536464441). The protocol code itself is precommitted in a
new HEAD, and the one-shot GitHub workflow checks that NO src/i3 engine file
changed between the two HEADs. An independent third OS root and method are
published BEFORE G0. The technical inner runner never issues science claims.

The single confirmatory statistic is only computed AFTER independently
rehashing every science original gzip, reconstructing the lineage, and
validating the G2 factorial intervention. No exploratory re-selection.
"""
from __future__ import annotations

from hashlib import sha256
import gzip
import json
import math
import os
from pathlib import Path
import re
import secrets
import subprocess
import sys

from i3.lab import stage8e2_preexposure_schedule as P
from i3.lab import stage8e2_technical_transport as T
from i3.lab import stage8e2_two_technical_receipts as R
from i3.lab import stage8e2_cold_original_archive_audit as C
from i3.lab import stage8e_causal_gamma_population_test as ANALYSIS
from i3.lab import stage6_light_native_g0_transport as OWNER
from i3.runtime.provenance import source_snapshot

SCHEMA = "i3-stage8e2-new-prospective-science-over-frozen-technical-source/v0"
ENGINE_HEAD = "03faff4b9c194a5288b92e394f6a75cbe62cd095"
ENGINE_SHA = "e816ff5f5ee679253fc57f6e9ee79d21dff73dd72d6adf3c7f55ba7aa0f3e7f6"
TECHNICAL_RUN_ID = 44536464441
TECHNICAL_PLAN_SHAS = {
    "3.11": "a5b32b52b80d0ce80050dfca3c30f6cc30884e1aada99a10061c86c4d229a1bc",
    "3.12": "88e5c0fdfc3a1fcc25e9cd22d6cdeedc08de30ee2977888b971809d2fa0accd1",
}
TECHNICAL_PLAN_ALLOCATIONS = {
    "3.11": "ed37fdb55a355a49ebaa71bf19c1dabdb634a09b85dec642a543d96b283bc741",
    "3.12": "b8c6a9895ed1ae7ef9a61fac8ffafc1cb772b1ea01f8f4a23f3031c8839858e2",
}
TECHNICAL_PLAN_ARTIFACT_IDS = {"3.11": 14535268998, "3.12": 14535124704}
TECHNICAL_COLD_ARTIFACT_IDS = {"3.11": 14566382506, "3.12": 14564879336}
TECHNICAL_GATE_ARTIFACT_ID = 14566511727
TECHNICAL_GATE_FILE_SHA256 = "5d66fbe5aee219e3b2e3b1a32a575280c6bfb52320f5cb1908421f4352c01011"
TECHNICAL_COLD_FILE_SHA256 = {
    "3.11": "11a194e7e69af209b4daa535c99fffc7299fce437d240aaead1e3431175e6642",
    "3.12": "f15589712f02eef97690449dd978aa69ab7aafeb6b34ddc4447c7879877c78f6",
}
TECH_PASS = "TWO_TECHNICAL_RECEIPTS_STRUCTURALLY_ACCEPTED_NO_SCIENCE"
COLD_PASS = "ALL_64512_NATIVE_ORIGINAL_GZIP_REAUDITED_NO_SCIENCE"
SCIENCE_PASS = "STAGE8E2_CAUSAL_GAMMA_BLOCK_MODULATION_F0"
SCIENCE_NO = "STAGE8E2_CAUSAL_GAMMA_BLOCK_NOT_DEMONSTRATED_F0"
SCIENCE_FAIL = "STAGE8E2_SCIENTIFIC_NO_VERDICT_NO_RETRY"
SCIENCE_HELD = "STAGE8E2_NEW_SCIENCE_NATIVE_COMPLETE_AWAIT_INDEPENDENT_GZIP_AUDIT"
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
ARMS = ("S_sham", "M_sham", "S_swap", "M_swap")
PRIMARY = {
    "schema": "i3-stage8e2-prospective-primary-gamma123-block-did/v0",
    "research_question": "causal_modulation_by_joint_gamma123_block_in_F0",
    "population_units": 64,
    "G2_lives_per_arm_population": 144,
    "four_arms": list(ARMS),
    "primary_estimand": "(S_sham-M_sham)-(S_swap-M_swap)",
    "observed_outcome": "native_steps_lived_1_to_400",
    "analysis": "unweighted_population_means_then_two_sided_Student_t",
    "two_sided_alpha": 0.025,
    "t_critical_df63": 2.2962367715148795,
    "interval": "two_sided_97.5_percent_Student_df63",
    "success": "strictly_excludes_zero_with_positive_variance",
    "zero_variance": "NO_VERDICT",
    "missing_native_original": "NO_VERDICT",
    "worlds": "G2_physically_matched_separate_individual_seeds",
    "no_adaptive_looks_or_subgroup_promotions": True,
    "negative_or_null_results_must_be_published": True,
    "gamma3_single_gene_causality_not_tested": True,
    "scope": "F0_only",
    "old_technical_lives_never_used_as_science": True,
    "no_retry": True,
}
EVIDENCE_SCHEMA = "i3-stage8e2-two-technical-originals-publication-evidence/v0"


def dump(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def digest(value: object) -> str:
    return sha256(dump(value)).hexdigest()


def write_new(path: str | Path, value: object) -> str:
    raw = dump(value)
    with Path(path).open("xb") as fh:
        fh.write(raw)
        fh.flush()
        os.fsync(fh.fileno())
    return sha256(raw).hexdigest()


def read_json(path: str | Path) -> dict:
    p = Path(path)
    if p.is_symlink() or not p.is_file():
        raise ValueError("missing or redirected published evidence")
    return json.loads(p.read_bytes())


def verify_wrapper_head(head: str, expected_sha: str) -> None:
    if (type(head) is not str or not HEX40.fullmatch(head)
            or type(expected_sha) is not str or not HEX64.fullmatch(expected_sha)):
        raise PermissionError("prospectively frozen wrapper HEAD/script SHA required")
    checkout = Path(__file__).resolve().parents[1]
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=checkout,
                                      text=True, timeout=15).strip()
    dirty = subprocess.check_output(["git", "status", "--porcelain",
                                      "--untracked-files=all"], cwd=checkout,
                                     text=True, timeout=15).strip()
    actual_sha = sha256(Path(__file__).read_bytes()).hexdigest()
    if commit != head or dirty or actual_sha != expected_sha:
        raise PermissionError("scientific wrapper code is not clean precommitted source")


def verify_native_source() -> None:
    snap = source_snapshot()
    if (snap.get("git_head") != ENGINE_HEAD or snap.get("sha256") != ENGINE_SHA
            or snap.get("working_tree_dirty") is not False):
        raise PermissionError("science cannot change or substitute the two-rehearsal engine")



def verify_owner_science_scope() -> None:
    """ADR-0022 permits NEW science, never a replay of consumed cohorts."""
    OWNER._pins()
    direction = json.loads(OWNER.DIRECTION.read_bytes())
    applies = direction.get("applies_to", {})
    requirements = direction.get("prospective_execution_requirements", {})
    if (applies.get("scientific_prospective_experiments_authorized") is not True
            or applies.get("previously_consumed_worlds_allowed") is not False
            or applies.get("legacy_cohort_replay_allowed") is not False
            or requirements.get("run_specific_admission_manifest_required") is not True
            or requirements.get("all_originals_favorable_adverse_null_required") is not True
            or requirements.get(
                "complete_source_exact_engineering_rehearsal_for_stage6_science_required"
            ) is not True):
        raise PermissionError("missing owner scope for prospective science on NEW root")


def _read_technical_evidence(root: str) -> dict:
    path = Path(root)
    expected = ("gate", "cold311", "cold312", "plan311", "plan312")
    if not all((path / k).is_dir() for k in expected):
        raise ValueError("two technical preexposures and cold audits not downloaded")
    gate_raw = (path / "gate/TECHNICAL_GATE.json").read_bytes()
    if sha256(gate_raw).hexdigest() != TECHNICAL_GATE_FILE_SHA256:
        raise ValueError("technical final gate does not match previously published bytes")
    gate = json.loads(gate_raw)
    for version, directory in (("3.11", "cold311"), ("3.12", "cold312")):
        cold_raw = (path / directory / "COLD_AUDIT.json").read_bytes()
        if sha256(cold_raw).hexdigest() != TECHNICAL_COLD_FILE_SHA256[version]:
            raise ValueError("independent technical cold-audit artifact was replaced")
    audits = {
        "3.11": read_json(path / "cold311/COLD_AUDIT.json"),
        "3.12": read_json(path / "cold312/COLD_AUDIT.json"),
    }
    plans, raw_sha = {}, {}
    for version, directory in (("3.11", "plan311"), ("3.12", "plan312")):
        p = path / directory / "PLAN.json"
        raw = p.read_bytes()
        actual = sha256(raw).hexdigest()
        written = (path / directory / "PLAN.sha256").read_text().strip()
        if actual != written or actual != TECHNICAL_PLAN_SHAS[version]:
            raise ValueError("technical original preexposure byte SHA mismatch")
        plans[version] = json.loads(raw)
        if raw != dump(plans[version]):
            raise ValueError("technical preexposure is not canonical")
        raw_sha[version] = actual
    evidence = {
        "schema": EVIDENCE_SCHEMA,
        "technical_run_id": TECHNICAL_RUN_ID,
        "technical_gate_artifact_id": TECHNICAL_GATE_ARTIFACT_ID,
        "technical_gate_file_sha256": TECHNICAL_GATE_FILE_SHA256,
        "technical_cold_file_sha256": TECHNICAL_COLD_FILE_SHA256,
        "technical_plan_artifact_ids": TECHNICAL_PLAN_ARTIFACT_IDS,
        "technical_cold_artifact_ids": TECHNICAL_COLD_ARTIFACT_IDS,
        "technical_gate": gate, "cold_audits": audits,
        "technical_plans": plans, "technical_plan_file_sha256": raw_sha,
    }
    verify_technical_evidence(evidence)
    return evidence


def verify_technical_evidence(evidence: object) -> dict:
    if (type(evidence) is not dict or set(evidence) != {
            "schema", "technical_run_id", "technical_gate_artifact_id",
            "technical_gate_file_sha256", "technical_cold_file_sha256",
            "technical_plan_artifact_ids", "technical_cold_artifact_ids",
            "technical_gate", "cold_audits", "technical_plans",
            "technical_plan_file_sha256"}
            or evidence["schema"] != EVIDENCE_SCHEMA
            or evidence["technical_run_id"] != TECHNICAL_RUN_ID
            or evidence["technical_gate_artifact_id"] != TECHNICAL_GATE_ARTIFACT_ID
            or evidence["technical_gate_file_sha256"] != TECHNICAL_GATE_FILE_SHA256
            or evidence["technical_cold_file_sha256"] != TECHNICAL_COLD_FILE_SHA256
            or evidence["technical_plan_artifact_ids"] != TECHNICAL_PLAN_ARTIFACT_IDS
            or evidence["technical_cold_artifact_ids"] != TECHNICAL_COLD_ARTIFACT_IDS):
        raise PermissionError("foreign Stage8-E2 original-gzip technical evidence")
    gate = evidence["technical_gate"]
    if (type(gate) is not dict or gate.get("schema") != R.SCHEMA
            or gate.get("status") != TECH_PASS
            or gate.get("source_git_head") != ENGINE_HEAD
            or gate.get("source_files_sha256") != ENGINE_SHA
            or gate.get("total_original_lives_claimed") != 129024
            or gate.get("total_mutations_claimed") != 12288
            or gate.get("scientific_admission") is not False
            or gate.get("science_verdict") != "NOT_ISSUED"
            or gate.get("science_lives_generated") != 0
            or gate.get("python_versions") != ["3.11", "3.12"]):
        raise PermissionError("both source-exact technical rehearsals not admitted")
    plans, audits = evidence["technical_plans"], evidence["cold_audits"]
    if (type(plans) is not dict or set(plans) != {"3.11", "3.12"}
            or type(audits) is not dict or set(audits) != {"3.11", "3.12"}
            or evidence["technical_plan_file_sha256"] != TECHNICAL_PLAN_SHAS):
        raise PermissionError("technical plan inputs missing or altered")
    for version in ("3.11", "3.12"):
        plan, audit = plans[version], audits[version]
        # T.verify_plan reconstructs the original physically frozen F0 Worlds,
        # all founder/selection/mutation and 64512 identity commitments.
        T.verify_plan(plan)
        if (sha256(dump(plan)).hexdigest() != TECHNICAL_PLAN_SHAS[version]
                or plan["allocation_sha256"] != TECHNICAL_PLAN_ALLOCATIONS[version]
                or plan["source_git_head"] != ENGINE_HEAD
                or plan["source_files_sha256"] != ENGINE_SHA
                or plan["scientific_admission"] is not False):
            raise PermissionError("technical original plan is not source-exact")
        if (type(audit) is not dict or audit.get("schema") != C.SCHEMA
                or audit.get("status") != COLD_PASS
                or audit.get("original_lives_rehashed") != 64512
                or audit.get("scientific_admission") is not False
                or audit.get("source_git_head") != ENGINE_HEAD
                or audit.get("source_files_sha256") != ENGINE_SHA
                or audit.get("allocation_sha256") != plan["allocation_sha256"]
                or type(audit.get("g0_g1_g2_manifest_sha256")) is not list
                or len(audit["g0_g1_g2_manifest_sha256"]) != 3
                or type(audit.get("parentage_audit_sha256")) is not list
                or len(audit["parentage_audit_sha256"]) != 2
                or any(type(v) is not str or not HEX64.fullmatch(v)
                       for v in (audit["g0_g1_g2_manifest_sha256"]
                                 + audit["parentage_audit_sha256"]))):
            raise PermissionError("technical originals were not cold-rehashed")
    if (plans["3.11"]["root_hex"] == plans["3.12"]["root_hex"]
            or audits["3.11"]["phase_chain_sha256"] ==
               audits["3.12"]["phase_chain_sha256"]
            or audits["3.11"]["g0_g1_g2_manifest_sha256"] ==
               audits["3.12"]["g0_g1_g2_manifest_sha256"]):
        raise PermissionError("reused engineering root or original phase chain")
    return evidence


def make_science_plan(root_hex: str, wrapper_head: str, wrapper_sha: str,
                      outer_archive_root: str, evidence: dict) -> dict:
    """Bind an OS-generated *third* root to sealed science before birth."""
    P._root(root_hex)
    verify_owner_science_scope()
    verify_technical_evidence(evidence)
    if type(wrapper_head) is not str or not HEX40.fullmatch(wrapper_head):
        raise ValueError("source-locked scientific wrapper HEAD required")
    if type(wrapper_sha) is not str or not HEX64.fullmatch(wrapper_sha):
        raise ValueError("source-locked wrapper bytes required")
    T._outside_repo(outer_archive_root)
    for tech in evidence["technical_plans"].values():
        if (root_hex == tech["root_hex"] or
                Path(outer_archive_root) == Path(tech["archive_root"]) or
                Path(outer_archive_root).is_relative_to(Path(tech["archive_root"]))):
            raise PermissionError("third science root/custody reuses technical data")
    native = T.make_plan(root_hex, ENGINE_HEAD, ENGINE_SHA,
                         str(Path(outer_archive_root) / "native-originals"))
    if (native["planned_lives"] != 64512
            or native["planned_mutations"] != 6144
            or native["scientific_admission"] is not False
            or native["frozen_method"] != T.METHOD
            or native["g2_heldout_worlds_sha256"] in {
                row["g2_heldout_worlds_sha256"]
                for row in evidence["technical_plans"].values()}):
        raise PermissionError("science native allocation is not independent/new")
    payload = {
        "schema": SCHEMA, "status": "SCIENCE_PREEXPOSED_NOT_RUN",
        "scientific_admission": True, "no_retry": True,
        "source_engine_head": ENGINE_HEAD, "source_engine_sha256": ENGINE_SHA,
        "source_protocol_head": wrapper_head, "source_protocol_file_sha256": wrapper_sha,
        "owner_scope": "ADR_0022_NEW_PROSPECTIVE_LAB_STUDY",
        "original_technical_run_id": TECHNICAL_RUN_ID,
        "technical_evidence": evidence,
        "technical_evidence_sha256": digest(evidence),
        "scientific_entropy_root_hex": root_hex,
        "outer_archive_root": outer_archive_root,
        "native_generator_plan": native,
        "native_generator_plan_sha256": sha256(dump(native)).hexdigest(),
        "allocation_g2_worlds_sha256": native["g2_heldout_worlds_sha256"],
        "primary": PRIMARY,
        "primary_sha256": digest(PRIMARY),
        "population_units": 64, "planned_original_lives": 64512,
        "planned_g2_original_lives": 36864,
        "planned_original_gzip": 64512,
        "preexposure_scientific_verdict": "NOT_ISSUED",
        "science_lives_created_at_preexposure": 0,
        "previous_technical_lives_excluded": True,
        "independent_cold_audit_required": True,
        "gamma3_alone_not_identified": True,
        "stage2_verdict_unchanged": "NOT_ISSUED",
    }
    payload["allocation_sha256"] = digest(payload)
    return payload


def verify_science_plan(plan: object) -> dict:
    if (type(plan) is not dict or plan.get("schema") != SCHEMA
            or plan.get("status") != "SCIENCE_PREEXPOSED_NOT_RUN"
            or plan.get("scientific_admission") is not True
            or plan.get("no_retry") is not True
            or plan.get("preexposure_scientific_verdict") != "NOT_ISSUED"
            or plan.get("science_lives_created_at_preexposure") != 0):
        raise PermissionError("science plan missing prior prospective admission")
    expected = make_science_plan(
        plan.get("scientific_entropy_root_hex"),
        plan.get("source_protocol_head"),
        plan.get("source_protocol_file_sha256"),
        plan.get("outer_archive_root"), plan.get("technical_evidence"))
    if dump(expected) != dump(plan):
        raise PermissionError("changed method, technical proof, source or science root")
    return plan


def _assert_environment(plan: dict) -> None:
    if sys.version_info[:2] != (3, 11):
        raise PermissionError("one source-exact Python 3.11 scientific cohort required")
    verify_wrapper_head(plan["source_protocol_head"],
                        plan["source_protocol_file_sha256"])
    verify_native_source()
    T._assert_technical_environment(plan["native_generator_plan"])


def allocate(technical_evidence_dir: str, wrapper_head: str,
             outer_archive_root: str, science_plan_path: str,
             native_plan_path: str) -> dict:
    verify_native_source()
    wrapper_sha = sha256(Path(__file__).read_bytes()).hexdigest()
    verify_wrapper_head(wrapper_head, wrapper_sha)
    evidence = _read_technical_evidence(technical_evidence_dir)
    plan = make_science_plan(secrets.token_hex(32), wrapper_head, wrapper_sha,
                             outer_archive_root, evidence)
    outer_sha = write_new(science_plan_path, plan)
    inner_sha = write_new(native_plan_path, plan["native_generator_plan"])
    if inner_sha != plan["native_generator_plan_sha256"]:
        raise AssertionError("unpublished different inner native allocation")
    return {"schema": SCHEMA + "/preexposure-receipt",
            "status": "SCIENCE_PREEXPOSED_ZERO_LIVES",
            "source_protocol_head": wrapper_head,
            "source_engine_head": ENGINE_HEAD,
            "outer_plan_file_sha256": outer_sha,
            "native_plan_file_sha256": inner_sha,
            "technical_originals": 129024,
            "scientific_lives_created": 0}


def _verified_files(plan_path: str, published_plan_sha256: str,
                    native_plan_path: str) -> dict:
    if (type(published_plan_sha256) is not str
            or not HEX64.fullmatch(published_plan_sha256)):
        raise PermissionError("missing externally published science file SHA")
    raw = Path(plan_path).read_bytes()
    if sha256(raw).hexdigest() != published_plan_sha256:
        raise PermissionError("science plan bytes not equal prepublished artifact")
    plan = verify_science_plan(json.loads(raw))
    if raw != dump(plan):
        raise PermissionError("noncanonical scientific preexposure bytes")
    native = Path(native_plan_path).read_bytes()
    if (sha256(native).hexdigest() != plan["native_generator_plan_sha256"]
            or native != dump(plan["native_generator_plan"])):
        raise PermissionError("native generator does not consume published science root")
    return plan


def run_native_science(plan_path: str, published_plan_sha256: str,
                       native_plan_path: str) -> dict:
    """Single-use SCIENCE cohort as an outer admitted envelope; no statistics."""
    plan = _verified_files(plan_path, published_plan_sha256, native_plan_path)
    _assert_environment(plan)
    root = Path(plan["outer_archive_root"])
    if (Path(plan_path).resolve().is_relative_to(root.resolve())
            or Path(native_plan_path).resolve().is_relative_to(root.resolve())
            or not root.parent.is_dir()):
        raise PermissionError("preexposure plan must predate science archive")
    root.mkdir()  # atomic no-retry science-claim: fail if anything exists
    write_new(root / "SCIENCE_CLAIM.json", {
        "schema": SCHEMA + "/science-claim",
        "status": "SCIENCE_IRREVERSIBLY_CLAIMED_NO_RETRY",
        "scientific_admission": True, "no_retry": True,
        "published_science_file_sha256": published_plan_sha256,
        "science_allocation_sha256": plan["allocation_sha256"],
        "source_engine_head": ENGINE_HEAD,
        "source_protocol_head": plan["source_protocol_head"],
        "technical_evidence_sha256": plan["technical_evidence_sha256"],
    })
    try:
        # This is the proven exact-source native generator. Its inner receipt
        # remains TECHNICAL, and has no authority to declare a scientific result.
        inner = T.run_technical(native_plan_path,
                                plan["native_generator_plan_sha256"])
        if (inner.get("status") != T.TECH_PASS
                or inner.get("original_lives_audited") != P.EXPECTED_TOTAL
                or inner.get("mutations_reconstructed") != 6144
                or inner.get("scientific_admission") is not False):
            raise ValueError("native original data generator not fully sealed")
        result = {
            "schema": SCHEMA + "/science-native-transport",
            "status": SCIENCE_HELD,
            "scientific_admission": True,
            "native_generator_admission": False,
            "published_science_file_sha256": published_plan_sha256,
            "science_allocation_sha256": plan["allocation_sha256"],
            "native_phase_chain_sha256": inner["phase_chain_sha256"],
            "native_originals_claimed": P.EXPECTED_TOTAL,
            "scientific_verdict": "NOT_ISSUED_AWAIT_COLD_GZIP",
            "no_retry": True,
        }
        write_new(root / "SCIENCE_NATIVE_RECEIPT.json", result)
        return result
    except BaseException as error:
        write_new(root / "SCIENCE_FAILURE.json", {
            "schema": SCHEMA + "/failure", "status": SCIENCE_FAIL,
            "error_type": type(error).__name__, "no_retry": True,
            "scientific_admission": False,
        })
        raise


def reduce_after_independent_cold_audit(
        plan_path: str, published_plan_sha256: str, native_plan_path: str,
        outer_archive_root: str) -> dict:
    """No original is scored before the full independent 64512-life rehash."""
    plan = _verified_files(plan_path, published_plan_sha256, native_plan_path)
    root = Path(outer_archive_root)
    if (str(root.resolve()) != plan["outer_archive_root"]
            or (root / "SCIENCE_FAILURE.json").exists()):
        raise ValueError("invalid or failed science original archive")
    claim = read_json(root / "SCIENCE_CLAIM.json")
    if (claim.get("status") != "SCIENCE_IRREVERSIBLY_CLAIMED_NO_RETRY"
            or claim.get("published_science_file_sha256") != published_plan_sha256
            or claim.get("science_allocation_sha256") != plan["allocation_sha256"]
            or claim.get("technical_evidence_sha256") !=
               plan["technical_evidence_sha256"]):
        raise PermissionError("scientific birth not linked to preexposure")
    native_root = root / "native-originals"
    # SOURCE HEAD is verified from every life manifest by the cold auditor.
    audited = C.cold_audit(native_plan_path,
                           plan["native_generator_plan_sha256"], str(native_root))
    inner = read_json(native_root / "TECHNICAL_RECEIPT.json")
    born = read_json(root / "SCIENCE_NATIVE_RECEIPT.json")
    if (audited["original_lives_rehashed"] != 64512
            or audited["source_git_head"] != ENGINE_HEAD
            or audited["source_files_sha256"] != ENGINE_SHA
            or audited["allocation_sha256"] !=
               plan["native_generator_plan"]["allocation_sha256"]
            or audited["phase_chain_sha256"] != inner["phase_chain_sha256"]
            or born["native_phase_chain_sha256"] != audited["phase_chain_sha256"]
            or born["status"] != SCIENCE_HELD):
        raise ValueError("independent original-level source or filial custody failed")
    # This is the FIRST time the prospective outcome is read for inference.
    # The cold auditor already inspected and hashed every original, including
    # all 36864 G2 gzip, their identity, World, terminal and paid trace chains.
    totals = {(p, arm): [] for p in range(64) for arm in ARMS}
    g2_root = native_root / "PHYSICAL_G2/G2"
    manifest = read_json(g2_root / "MANIFEST.json")
    if len(manifest["files"]) != 36864:
        raise ValueError("incomplete G2 prospective original archive")
    for row in manifest["files"]:
        gz = g2_root / row["file"]
        if gz.is_symlink():
            raise ValueError("redirected native original")
        record = json.loads(gzip.decompress(gz.read_bytes()))
        life, key = record["life"], record["identity"]
        p, arm = key["population"], key["arm"]
        if (p not in range(64) or arm not in ARMS
                or life["genome"] != key["genome_sha256"]
                or life["terminal"] not in ("dead", "censored")
                or type(life["steps_lived"]) is not int
                or not 1 <= life["steps_lived"] <= 400):
            raise ValueError("unexpected post-audit G2 bodily score")
        totals[p, arm].append(life["steps_lived"])
    rows = []
    for p in range(64):
        for arm in ARMS:
            if len(totals[p, arm]) != 144:
                raise ValueError("missing six G2 physical opportunities per child")
        rows.append({
            "population": p,
            "mean_G2_steps": {
                arm: math.fsum(totals[p, arm]) / 144 for arm in ARMS
            },
            "original_lives_by_arm": {arm: 144 for arm in ARMS},
        })
    design = ANALYSIS.analyze_design_only(rows)
    mean, sd, ci = (
        design["primary_gamma_block_did_mean_steps"],
        design["primary_gamma_block_did_population_sd_steps"],
        design["two_sided_97_5_percent_interval_steps"])
    if (not math.isfinite(mean) or not math.isfinite(sd)
            or any(not math.isfinite(x) for x in ci)
            or design["population_units"] != 64):
        raise ValueError("foreign/nonfinite primary causal statistic")
    if sd == 0:
        status = SCIENCE_FAIL
        interpretation = "UNDEFINED_VARIANCE_NO_CONFIRMATORY_TEST"
    elif ci[0] > 0 or ci[1] < 0:
        status = SCIENCE_PASS
        interpretation = "CAUSAL_GAMMA123_BLOCK_MODULATION_COMPATIBLE_WITH_F0_DESIGN"
    else:
        status = SCIENCE_NO
        interpretation = "NO_GAMMA123_BLOCK_MODULATION_DEMONSTRATED_IN_F0"
    return {
        "schema": SCHEMA + "/from-cold-originals",
        "status": status,
        "scientific_admission": status != SCIENCE_FAIL,
        "science_plan_file_sha256": published_plan_sha256,
        "science_allocation_sha256": plan["allocation_sha256"],
        "source_engine_head": ENGINE_HEAD,
        "source_protocol_head": plan["source_protocol_head"],
        "frozen_primary_sha256": digest(PRIMARY),
        "technical_evidence_sha256": plan["technical_evidence_sha256"],
        "cold_originals_sha256": digest(audited),
        "cold_audit": audited,
        "original_native_lives_rehashed": 64512,
        "G2_original_lives_scored": 36864,
        "native_mutations_reconstructed": 6144,
        "population_units": 64,
        "original_population_means": rows,
        "primary": design,
        "positive_population_DID": sum(x > 0 for x in design["all_64_population_did"]),
        "negative_population_DID": sum(x < 0 for x in design["all_64_population_did"]),
        "zero_population_DID": sum(x == 0 for x in design["all_64_population_did"]),
        "interpretation": interpretation,
        "joint_block_not_gamma3_alone": True,
        "external_attestation": False,
        "F0_only": True,
        "previous_technical_lives_excluded": True,
        "no_retry": True,
        "stage2_verdict": "NOT_ISSUED",
    }


def main() -> None:
    args = sys.argv
    if len(args) == 7 and args[1] == "allocate":
        _, _, evidence_dir, wrapper_head, original_root, out_plan, out_native = args
        print(json.dumps(allocate(evidence_dir, wrapper_head,
                                  original_root, out_plan, out_native),
                         sort_keys=True))
    elif len(args) == 5 and args[1] == "run":
        _, _, plan_path, sha, native_path = args
        print(json.dumps(run_native_science(plan_path, sha, native_path),
                         sort_keys=True))
    elif len(args) == 6 and args[1] == "audit":
        _, _, plan_path, sha, native_path, original_root = args
        print(json.dumps(reduce_after_independent_cold_audit(
            plan_path, sha, native_path, original_root), sort_keys=True))
    else:
        raise SystemExit(
            "usage: allocate EVIDENCE_DIR WRAPPER_HEAD SCIENCE_ARCHIVE_ROOT"
            " SCIENCE_PLAN NATIVE_PLAN | run SCIENCE_PLAN PUB_SHA NATIVE_PLAN"
            " | audit SCIENCE_PLAN PUB_SHA NATIVE_PLAN SCIENCE_ARCHIVE_ROOT")


if __name__ == "__main__":
    main()
