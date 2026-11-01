#!/usr/bin/env python3
"""Read-only, fail-closed dossiers linking research claims to exact source blobs.

This is a review preparation tool, NEVER a scientific evaluator or engine runner.
A PASS asserts only that a curated manifest and its cited document bytes agree.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "config/research-dossiers.json"
REGISTRY = "config/engine-registry.json"
PROGRAM = "config/research-program.json"
SCHEMA = "individual-zero-curated-research-dossiers/v1"
SHA40 = re.compile(r"^[0-9a-f]{40}$")
ALLOWED_KINDS = {
    "historical_confirmatory": "NO_GO",
    "preregistered_unexecuted": "NOT_EXECUTED",
    "historical_inconclusive": "INCONCLUSIVE",
    "architecture_review_pending": "REVIEW_REQUIRED",
    "archive_custody_pending": "PARTIAL",
}
ALLOWED_ROLES = {
    "preregistration", "reported_result", "posthoc_diagnostic",
    "current_status", "architecture_proposal", "review_proposal",
    "g0_transition", "artifact_inventory", "custody_review",
    "offline_reproduction",
}
ALLOWED_GAP_STATES = {
    "EXTERNAL_NOT_VERIFIED", "INDEPENDENT_REVIEW_REQUIRED",
    "NOT_EXECUTED", "UNVERIFIED", "NOT_OBSERVED", "NOT_ESTABLISHED",
    "PROVIDER_RETENTION_RISK", "SOURCE_REF_UNPROTECTED",
}
ALLOWED_AUTHORITIES = {
    "original_preregistration", "dated_posthoc_diagnostic",
    "dated_reported_result", "current_status_snapshot",
    "architecture_proposal", "pending_review_proposal",
    "dated_transition_decision", "dated_offline_reproduction",
    "dated_provider_metadata_snapshot", "dated_custody_review",
}
FIELDS_OF_SCOPE = ("study_key", "cohort_key", "endpoint_key", "contrast_key")
G0_INVENTORY = "config/research-g0-artifacts.json"
DIGEST_SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")
G0_SOURCE_ARCHIVE_SHA = "1e19f02db14b64a35f8bb014d69cc061f311002c"
G0_I1_TREE_SHA = "cf7968d3ee94a5792d37d76241a55d4c8406a3fb"



def load_json(root: Path, relative: str) -> dict:
    return json.loads((root / relative).read_text(encoding="utf-8"))


def safe_relative(value: object) -> bool:
    if not isinstance(value, str) or not value or value.startswith("/") or "\\" in value:
        return False
    parts = PurePosixPath(value).parts
    return bool(parts) and all(p not in (".", "..") for p in parts)


def source_integrity(root: Path, src: dict) -> dict:
    path = src["path"]
    result = {"id": src["id"], "path": path, "pinned_blob_sha": src["blob_sha"],
              "observed_blob_sha": None, "marker_present": False,
              "status": "UNVERIFIED", "scientific_verdict": "NOT_EVALUATED"}
    if not safe_relative(path):
        result["status"] = "UNSAFE_PATH"
        return result
    target = root / path
    if target.is_symlink() or not target.is_file() or not target.resolve().is_relative_to(root.resolve()):
        result["status"] = "MISSING_OR_UNSAFE_SOURCE"
        return result
    try:
        raw = target.read_bytes()
        text = raw.decode("utf-8")
    except (OSError, UnicodeError):
        result["status"] = "UNREADABLE_SOURCE"
        return result
    result["observed_blob_sha"] = hashlib.sha1(
        b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()
    result["marker_present"] = src["anchor"] in text
    if result["observed_blob_sha"] != src["blob_sha"]:
        result["status"] = "SOURCE_BLOB_DRIFT"
    elif not result["marker_present"]:
        result["status"] = "SOURCE_MARKER_MISSING"
    else:
        result["status"] = "PIN_MATCH"
    return result



def audit_g0_inventory(root: Path = ROOT) -> dict:
    """Validate dated GitHub metadata, never the M11 ZIP bytes or independent custody."""
    errors: list[str] = []
    try:
        data = load_json(root, G0_INVENTORY)
    except (OSError, ValueError, TypeError) as exc:
        return {"status": "FAIL", "errors": [str(exc)],
                "scientific_verdict": "NOT_EVALUATED",
                "custody_status": "NOT_ATTESTED"}
    if (data.get("schema") != "individual-zero-g0-provider-artifact-inventory/v1"
            or data.get("repository") != "josselin-orta-lab/individual-zero"
            or data.get("observed_on") != "2026-11-01"
            or data.get("provider_metadata_only") is not True):
        errors.append("G0 inventory schema/date/provider scope mismatch")
    for field in ("provider_download_verified", "original_m11_zip_sha256_verified_in_this_audit",
                  "original_m11_archives_retrieved_in_this_audit",
                  "independent_durable_custody_attested",
                  "independent_reviewer_access_attested"):
        if data.get(field) is not False:
            errors.append("G0 metadata cannot claim independent original-data custody: " + field)
    for field in ("no_auto_scientific_go", "no_archive_mutation",
                  "no_cohort_execution", "provider_digest_not_original_m11_digest"):
        if data.get("policy", {}).get(field) is not True:
            errors.append("missing G0 metadata-only safety declaration: " + field)
    if data.get("scientific_verdict") != "NOT_EVALUATED":
        errors.append("G0 metadata may not approve science")
    archive = data.get("source_archive", {})
    if not isinstance(archive, dict) or any((
            archive.get("branch") != "archive/i1-reference-2026-10-31",
            archive.get("commit_sha") != G0_SOURCE_ARCHIVE_SHA,
            archive.get("src_i1_tree_sha") != G0_I1_TREE_SHA,
            archive.get("protected") is not False)):
        errors.append("G0 historical archive pin/protection mismatch")

    campaigns = data.get("campaigns", {})
    expected = {
        "A1P": (40938021102, "012ece9eb0b4531f714bd69af439eeb38d7bf701", 1, 2, 8, "failure", "a1"),
        "A1C": (40944104333, "26f7929b6db43f68e78b0cc0d9c67e7444f924c6", 101, 112, 48, "success", "a1c"),
    }
    if not isinstance(campaigns, dict) or set(campaigns) != set(expected):
        errors.append("G0 must retain exactly the two historical A1 campaigns")
        campaigns = {}
    seen_ids: set[int] = set()
    artifact_count = 0
    earliest_expiry = None
    for label, (run_id, head_sha, seed_lo, seed_hi, n, outcome, prefix) in expected.items():
        run = campaigns.get(label)
        if not isinstance(run, dict):
            errors.append("missing G0 historical campaign: " + label)
            continue
        if any((run.get("run_id") != run_id, run.get("run_head_sha") != head_sha,
                run.get("run_status") != "completed", run.get("run_attempt") != 1,
                run.get("run_conclusion") != outcome,
                run.get("aggregate_job_conclusion") != outcome,
                run.get("individual_artifact_count") != n,
                run.get("reported_individual_lives") != n,
                run.get("provider_artifact_count") != n + 1,
                run.get("individual_job_total") != n,
                run.get("individual_job_pass_count") != n)):
            errors.append(label + ": original source/job outcome/count mismatch")
        expected_names = {
            f"{prefix}-{role}-s{s}-{arm}"
            for role in ("native", "reversed")
            for s in range(seed_lo, seed_hi + 1)
            for arm in ("canonical", "td_read_masked")
        }
        expected_names.add(f"{prefix}-aggregate-{run_id}")
        records = run.get("artifact_provider_snapshot", [])
        if not isinstance(records, list) or len(records) != len(expected_names):
            errors.append(label + ": incomplete provider artifact inventory")
            continue
        names: list[str] = []
        for item in records:
            if not isinstance(item, dict):
                errors.append(label + ": malformed artifact entry")
                continue
            names.append(item.get("name"))
            ident = item.get("id")
            if type(ident) is not int or ident <= 0 or ident in seen_ids:
                errors.append(label + ": duplicate/invalid provider artifact id")
            else:
                seen_ids.add(ident)
            if not isinstance(item.get("provider_artifact_digest"), str) or not DIGEST_SHA256.fullmatch(item["provider_artifact_digest"]):
                errors.append(label + ": missing provider SHA-256 digest")
            if type(item.get("size_bytes")) is not int or item["size_bytes"] <= 0:
                errors.append(label + ": invalid artifact byte count")
            if item.get("expired") is not False:
                errors.append(label + ": provider snapshot did not report the artifact available")
            expires = item.get("expires_at", "")
            if not isinstance(expires, str) or not re.fullmatch(
                    r"2026-11-28T\d{2}:\d{2}:\d{2}Z", expires):
                errors.append(label + ": unexpected retention/expiry metadata")
            else:
                earliest_expiry = min(earliest_expiry, expires) if earliest_expiry else expires
        if set(names) != expected_names or len(set(names)) != len(names):
            errors.append(label + ": missing/duplicate original slots or aggregate")
        artifact_count += len(records)
    return {"status": "FAIL" if errors else "PASS", "errors": sorted(set(errors)),
            "provider_records": artifact_count,
            "original_lives_metadata_count": 56 if not errors else None,
            "scheduled_earliest_expiry": earliest_expiry,
            "metadata_observed_on": data.get("observed_on"),
            "custody_status": "NOT_ATTESTED",
            "scientific_verdict": "NOT_EVALUATED",
            "warning": "Provider upload digests are not original M11 ZIP proofs. Historical availability is not current availability, and neither external custody nor scientific G0 is approved."}


def validate(root: Path = ROOT, *, strict_sources: bool = True) -> dict:
    """Validate structure; optionally report source drift without failing structural CI.

    Strict mode fails closed on changed evidence. Structure-only mode still
    exposes every mismatched exact blob and never approves a dossier.
    """
    errors: list[str] = []
    source_drift: list[str] = []
    inventory_result = audit_g0_inventory(root)
    if inventory_result["status"] != "PASS":
        errors.extend("G0 artifact inventory: " + error
                      for error in inventory_result["errors"])
    try:
        manifest = load_json(root, MANIFEST)
        registry = load_json(root, REGISTRY)
        i2 = load_json(root, "src/i2/engine.json")
        program = load_json(root, PROGRAM)
    except (OSError, ValueError, TypeError) as exc:
        return {"status": "FAIL", "errors": ["cannot read navigation metadata: " + str(exc)],
                "scientific_verdict": "NOT_EVALUATED"}

    if manifest.get("schema") != SCHEMA or manifest.get("repository") != "josselin-orta-lab/individual-zero":
        errors.append("schema/repository mismatch")
    for name in ("no_auto_scientific_approval", "no_auto_execution",
                 "none_claims_independent_attestation", "scopes_required_for_comparisons"):
        if manifest.get("policy", {}).get(name) is not True:
            errors.append("missing fail-closed policy " + name)
    if registry.get("active_generation") != "I1":
        errors.append("active generation requires a review of dossier safety assumptions")
    if i2.get("status") != "proposal" or i2.get("entrypoints"):
        errors.append("I2 must remain an unregistered inert proposal")
    if "I2" in registry.get("generations", {}):
        errors.append("I2 unexpectedly registered")
    known_questions = {q["id"] for q in program.get("questions", [])}
    sources = manifest.get("sources", [])
    dossiers = manifest.get("dossiers", [])
    if not isinstance(sources, list) or not sources:
        errors.append("sources must be a nonempty list")
        sources = []
    if not isinstance(dossiers, list) or not dossiers:
        errors.append("dossiers must be a nonempty list")
        dossiers = []
    if len({s.get("id") for s in sources if isinstance(s, dict)}) != len(sources):
        errors.append("duplicate/invalid source IDs")
    if len({d.get("id") for d in dossiers if isinstance(d, dict)}) != len(dossiers):
        errors.append("duplicate/invalid dossier IDs")
    source_by_id: dict[str, dict] = {}
    source_results: dict[str, dict] = {}
    for s in sources:
        if not isinstance(s, dict):
            errors.append("invalid source record")
            continue
        ident = s.get("id")
        if not isinstance(ident, str) or not ident:
            errors.append("invalid source id")
            continue
        if not safe_relative(s.get("path")):
            errors.append(ident + ": unsafe path")
            continue
        if not isinstance(s.get("blob_sha"), str) or not SHA40.fullmatch(s["blob_sha"]):
            errors.append(ident + ": missing/invalid exact source blob")
            continue
        if (not isinstance(s.get("anchor"), str) or len(s["anchor"]) < 12
                or "\n" in s["anchor"] or s.get("authority") not in ALLOWED_AUTHORITIES):
            errors.append(ident + ": missing exact marker/authority")
            continue
        source_by_id[ident] = s
        source_results[ident] = source_integrity(root, s)
        if source_results[ident]["status"] != "PIN_MATCH":
            source_drift.append(ident)
            if strict_sources:
                errors.append(ident + ": " + source_results[ident]["status"])

    for dossier in dossiers:
        if not isinstance(dossier, dict):
            errors.append("invalid dossier")
            continue
        name = dossier.get("id")
        if not isinstance(name, str) or not name:
            errors.append("invalid dossier id")
            continue
        kind = dossier.get("kind")
        if (kind not in ALLOWED_KINDS
                or dossier.get("reported_assessment") != ALLOWED_KINDS.get(kind)):
            errors.append(name + ": invalid kind/assessment pairing")
        if dossier.get("generation") not in ("I1", "I2"):
            errors.append(name + ": invalid generation")
        if dossier.get("question_id") not in known_questions:
            errors.append(name + ": unknown research question")
        if (dossier.get("authority") != "CURATED_SOURCE_NAVIGATION_ONLY"
                or dossier.get("scientific_gate") != "NOT_EVALUATED"):
            errors.append(name + ": dossier may not claim scientific authority")
        if not all(isinstance(dossier.get(key), str) and len(dossier[key]) >= 12
                   for key in ("title", "scope_limit", "next_review")):
            errors.append(name + ": missing context or limitations")
        issues = dossier.get("related_issues", [])
        if not isinstance(issues, list) or not issues or any(
                type(num) is not int or num < 1 for num in issues):
            errors.append(name + ": missing/invalid issues")
        scope = dossier.get("scope", {})
        if not isinstance(scope, dict) or any(
                not isinstance(scope.get(k), str) or not scope.get(k) for k in FIELDS_OF_SCOPE):
            errors.append(name + ": incomplete comparison scope")
        if name == "I2-G1-INDEPENDENT-REVIEW" and dossier.get("generation") != "I2":
            errors.append(name + ": wrong generation")

        links = dossier.get("source_roles", [])
        if not isinstance(links, list) or not links:
            errors.append(name + ": missing source references")
            links = []
        roles = []
        seen_links = set()
        for link in links:
            if not isinstance(link, dict):
                errors.append(name + ": malformed source link")
                continue
            sid, role = link.get("source_id"), link.get("role")
            if sid not in source_by_id or role not in ALLOWED_ROLES:
                errors.append(name + ": unknown source or role")
            if (sid, role) in seen_links:
                errors.append(name + ": duplicate source role")
            seen_links.add((sid, role))
            roles.append(role)
            if sid in source_by_id:
                source = source_by_id[sid]
                if role == "preregistration" and source["authority"] != "original_preregistration":
                    errors.append(name + ": preregistration role does not cite a preregistration")
                if role == "reported_result" and source["authority"] != "dated_reported_result":
                    errors.append(name + ": result role does not cite original dated result")
                special_roles = {
                    "g0_transition": "dated_transition_decision",
                    "artifact_inventory": "dated_provider_metadata_snapshot",
                    "custody_review": "dated_custody_review",
                    "offline_reproduction": "dated_offline_reproduction",
                    "posthoc_diagnostic": "dated_posthoc_diagnostic",
                }
                if role in special_roles and source["authority"] != special_roles[role]:
                    errors.append(name + ": mismatched source authority for " + role)
        if kind in ("historical_confirmatory", "historical_inconclusive",
                    "preregistered_unexecuted") and "preregistration" not in roles:
            errors.append(name + ": preregistration not linked")
        if kind == "historical_inconclusive" and "reported_result" not in roles:
            errors.append(name + ": original dated result not linked")
        if kind == "preregistered_unexecuted" and "reported_result" in roles:
            errors.append(name + ": unexecuted protocol cannot have claimed results")
        if kind == "architecture_review_pending" and not {"architecture_proposal", "review_proposal"} <= set(roles):
            errors.append(name + ": missing independent review inputs")
        if kind == "archive_custody_pending":
            required_roles = {"g0_transition", "artifact_inventory", "custody_review",
                              "offline_reproduction", "posthoc_diagnostic", "preregistration"}
            if not required_roles <= set(roles):
                errors.append(name + ": missing G0 archive provenance roles")
            if dossier.get("id") != "I1-G0-CUSTODY" or dossier.get("generation") != "I1":
                errors.append(name + ": G0 dossier owner mismatch")
        gaps = dossier.get("review_gaps", [])
        if not isinstance(gaps, list) or not gaps:
            errors.append(name + ": must disclose at least one open review gap")
        else:
            ids = []
            for gap in gaps:
                if (not isinstance(gap, dict) or not gap.get("id")
                        or gap.get("state") not in ALLOWED_GAP_STATES
                        or not isinstance(gap.get("question"), str)
                        or len(gap["question"]) < 12):
                    errors.append(name + ": invalid or missing review gap")
                else:
                    ids.append(gap["id"])
            if len(set(ids)) != len(ids):
                errors.append(name + ": duplicate review gap IDs")
    return {"status": "FAIL" if errors else "PASS", "errors": sorted(set(errors)),
            "sources": len(source_by_id), "dossiers": len(dossiers),
            "g0_provider_metadata": inventory_result,
            "source_integrity": source_results,
            "source_review_required": sorted(source_drift),
            "source_status": "SOURCE_REVIEW_REQUIRED" if source_drift else "PIN_MATCH",
            "audit_mode": "STRICT_SOURCES" if strict_sources else "STRUCTURE_ONLY",
            "scientific_verdict": "NOT_EVALUATED",
            "warning": "Structure-only PASS does NOT validate source freshness. Every changed source requires review. Neither mode certifies scientific outcomes, independent reviews, M11 archives or active gates."}


def dossier_view(dossier: dict, source_by_id: dict, audit: dict) -> dict:
    source_items = []
    for item in dossier["source_roles"]:
        src = source_by_id[item["source_id"]]
        status = audit["source_integrity"].get(src["id"], {})
        source_items.append({
            "source_id": src["id"], "role": item["role"],
            "path": src["path"], "authority": src["authority"],
            "pinned_blob_sha": src["blob_sha"],
            "marker": src["anchor"],
            "integrity": status.get("status", "UNVERIFIED")
        })
    source_valid = all(s["integrity"] == "PIN_MATCH" for s in source_items)
    roles = {item["role"] for item in source_items}
    open_gaps = dossier["review_gaps"]
    if dossier["kind"] == "historical_confirmatory" and "reported_result" not in roles:
        primary_status = "PRIMARY_ORIGINAL_RESULT_NOT_LINKED"
    elif dossier["kind"] == "preregistered_unexecuted":
        primary_status = "NO_RESULTS_EXPECTED_NOT_EXECUTED"
    elif dossier["kind"] == "architecture_review_pending":
        primary_status = "REVIEW_PROPOSALS_ONLY"
    elif dossier["kind"] == "archive_custody_pending":
        primary_status = "PROVIDER_METADATA_ONLY_INDEPENDENT_CUSTODY_NOT_ATTESTED"
    else:
        primary_status = "RESULT_REPORT_LINKED_NOT_INDEPENDENTLY_ATTESTED"
    return {
        "id": dossier["id"], "generation": dossier["generation"],
        "kind": dossier["kind"], "title": dossier["title"],
        "question_id": dossier["question_id"],
        "related_issues": dossier["related_issues"],
        "scope": dossier["scope"], "reported_assessment": dossier["reported_assessment"],
        "sources": source_items,
        "source_integrity": "PIN_MATCH" if source_valid else "SOURCE_RECONCILIATION_REQUIRED",
        "primary_record": primary_status,
        "review_gaps": open_gaps,
        "scope_limit": dossier["scope_limit"],
        "next_review": dossier["next_review"],
        "scientific_verdict": "NOT_EVALUATED",
        "approval": "NOT_GRANTED",
        "decision": "REVIEW_SOURCE_CHANGES_FIRST" if not source_valid else "REVIEW_ONLY_NO_AUTOMATIC_DECISION"
    }


def load_views(root: Path = ROOT, *, strict_sources: bool = True) -> tuple[dict, dict, list[dict]]:
    manifest = load_json(root, MANIFEST)
    result = validate(root, strict_sources=strict_sources)
    by_id = {x["id"]: x for x in manifest["sources"]}
    views = [dossier_view(d, by_id, result) for d in manifest["dossiers"]]
    return manifest, result, views


def compare_views(left: dict, right: dict) -> dict:
    if left["id"] == right["id"]:
        raise ValueError("compare two distinct dossier IDs")
    scope_fields = {f: (left["scope"][f], right["scope"][f]) for f in FIELDS_OF_SCOPE}
    exactly_same_scope = (left["generation"] == right["generation"]
                          and all(a == b for a, b in scope_fields.values()))
    if not all(value == "PIN_MATCH" for value in (left["source_integrity"], right["source_integrity"])):
        status = "SOURCE_RECONCILIATION_REQUIRED"
    elif not exactly_same_scope:
        status = "DIFFERENT_EXPERIMENT_OR_ENDPOINT_NO_CONTRADICTION_INFERRED"
    elif left["reported_assessment"] != right["reported_assessment"]:
        status = "POSSIBLE_SAME_SCOPE_REPORTED_ASSESSMENT_DISAGREEMENT_REVIEW"
    else:
        status = "SAME_REPORTED_ASSESSMENT_NOT_REPLICATION"
    return {
        "status": status, "left": left["id"], "right": right["id"],
        "same_explicit_scope": exactly_same_scope, "scope_dimensions": scope_fields,
        "reported_assessments": [left["reported_assessment"], right["reported_assessment"]],
        "scientific_verdict": "NOT_EVALUATED",
        "warning": "Even equal exact-scope keys cannot authenticate datasets, comparability, replication or causal inference. A difference is a review lead, never a proven contradiction."
    }


def gaps_report(views: list[dict]) -> dict:
    gaps = []
    for d in views:
        for item in d["review_gaps"]:
            gaps.append({"dossier": d["id"], "generation": d["generation"],
                         "question_id": d["question_id"], "reported_assessment": d["reported_assessment"],
                         "issue_links": [f"https://github.com/josselin-orta-lab/individual-zero/issues/{n}"
                                         for n in d["related_issues"]],
                         **item,
                         "source_integrity": d["source_integrity"],
                         "scientific_gate": "NOT_EVALUATED"})
    priority = {"PROVIDER_RETENTION_RISK": 0, "INDEPENDENT_REVIEW_REQUIRED": 1,
                "SOURCE_REF_UNPROTECTED": 2, "EXTERNAL_NOT_VERIFIED": 3,
                "UNVERIFIED": 4, "NOT_ESTABLISHED": 5,
                "NOT_OBSERVED": 6, "NOT_EXECUTED": 7}
    gaps.sort(key=lambda g: (g["source_integrity"] != "PIN_MATCH",
                             priority[g["state"]], g["dossier"], g["id"]))
    return {"status": "REVIEW_QUEUE_ONLY", "open_gaps": gaps,
            "scientific_verdict": "NOT_EVALUATED", "execution": "NOT_PERFORMED",
            "warning": "Sorted review gaps are not authorizations, scientific conclusions or a complete research backlog."}


def main(argv: list[str] | None = None, root: Path = ROOT) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    cmd = parser.add_subparsers(dest="command", required=True)
    audit_parser = cmd.add_parser("audit")
    audit_parser.add_argument("--structure-only", action="store_true",
                              help="Keep source drift visible without blocking structure-only checks")
    cmd.add_parser("g0-provider-inventory")
    cmd.add_parser("list")
    cmd.add_parser("gaps")
    pshow = cmd.add_parser("show")
    pshow.add_argument("--id", required=True)
    pcompare = cmd.add_parser("compare")
    pcompare.add_argument("--left", required=True)
    pcompare.add_argument("--right", required=True)
    args = parser.parse_args(argv)
    try:
        manifest, audit, views = load_views(
            root, strict_sources=not (args.command == "audit"
                                     and getattr(args, "structure_only", False)))
        if args.command == "audit":
            result = audit
        elif args.command == "g0-provider-inventory":
            result = audit["g0_provider_metadata"]
        elif args.command == "list":
            result = {"status": "NAVIGATION_ONLY", "dossiers": [
                {"id": v["id"], "kind": v["kind"], "reported_assessment": v["reported_assessment"],
                 "primary_record": v["primary_record"], "source_integrity": v["source_integrity"],
                 "open_review_gaps": len(v["review_gaps"])} for v in views],
                "scientific_verdict": "NOT_EVALUATED"}
        elif args.command == "gaps":
            result = gaps_report(views)
        elif args.command == "show":
            matches = [v for v in views if v["id"] == args.id]
            if len(matches) != 1:
                raise ValueError("unknown dossier ID: " + args.id)
            result = matches[0]
        else:
            by_id = {v["id"]: v for v in views}
            if args.left not in by_id or args.right not in by_id:
                raise ValueError("unknown comparison dossier ID")
            result = compare_views(by_id[args.left], by_id[args.right])
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if audit["status"] == "PASS" else 2
    except (OSError, KeyError, TypeError, ValueError, UnicodeError) as exc:
        print("research-dossiers: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
