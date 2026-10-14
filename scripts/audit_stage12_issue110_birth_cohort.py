"""External issue #110 cohort scope and cross-life reference validation.

Distinct physical lives are independent *only* if their birth identities and
cognitive receipts are distinct. Never merge multiple journals into one
metacognitive history. This verifier does not feed I0 or claim causal truth.
"""
from __future__ import annotations

import json
from pathlib import Path
from hashlib import sha256

from lab.independent_journal_audit import audit_export_bytes
from lab.stage12_goal_progress_audit import audit_stage12_goal_progress
from lab.stage12_first_person_agency_audit import audit_stage12_first_person_agency
from lab.stage12_attribution_pair_audit import audit_stage12_attribution_pairs

KINDS = frozenset({
    "stage12_goal_progress_preregistered",
    "stage12_goal_progress_followup",
    "stage12_goal_agency_precommitted",
    "stage12_goal_agency_judgement",
    "stage12_attribution_pair_admitted",
})


def scoped_cognitive_evidence(journal: bytes, *, declared_birth: str):
    if type(declared_birth) is not str or not declared_birth:
        raise ValueError("missing nonempty declared birth identity")
    audit_export_bytes(journal)
    audit_stage12_goal_progress(journal)
    audit_stage12_first_person_agency(journal)
    audit_stage12_attribution_pairs(journal)
    ids = set()
    for line in journal.splitlines():
        row = json.loads(line)
        event = row["causal_event"]
        if event["kind"] not in KINDS:
            continue
        evidence = event.get("data")
        if type(evidence) is not dict:
            raise ValueError("invalid lived cognition event")
        life = evidence.get("life_id")
        if life is not None and life != declared_birth:
            raise ValueError("cognitive receipt claims a different birth")
        if event["kind"] in (
            "stage12_goal_agency_precommitted",
            "stage12_goal_agency_judgement",
            "stage12_attribution_pair_admitted",
        ) and life != declared_birth:
            raise ValueError("attribution lacks its own birth identity")
        if row["event_id"] in ids:
            raise ValueError("same cognitive event reference duplicated")
        ids.add(row["event_id"])
    return ids


def audit_cohort(folder: Path) -> dict:
    index = json.loads((folder / "index.json").read_text())
    cases = index.get("lives")
    if (type(cases) is not list
            or len(cases) != index.get("n_planned")
            or len(cases) != index.get("n_completed")):
        raise ValueError("incomplete preregistered life cohort")
    births = set()
    scoped = set()
    reports = []
    for row in cases:
        if (type(row) is not dict or row.get("error")
                or row.get("audit_error")
                or type(row.get("world")) is not str
                or type(row.get("life_id")) is not str):
            raise ValueError("failed or unverified life cannot support cohort")
        life = row["life_id"]
        if life in births:
            raise ValueError("duplicate life identity in independently born cohort")
        births.add(life)
        label = f'{row["world"]}-water{int(row["initial_water"])}-{row["sleep_profile"]}'
        path = folder / label / "canonical.jsonl"
        raw = path.read_bytes()
        if sha256(raw).hexdigest() != row["journal_sha256"]:
            raise ValueError("life's source journal differs from its declared digest")
        local = scoped_cognitive_evidence(raw, declared_birth=life)
        if local & scoped:
            raise ValueError("cross-life cognitive reference collision")
        scoped.update(local)
        reports.append({
            "life_id": life,
            "journal_sha256": sha256(raw).hexdigest(),
            "cognitive_references": len(local),
            "physical_steps": row["executed_steps"],
        })
    return {
        "schema": "stage12-issue110-independent-birth-cohort-audit-v1",
        "preregistered_lives": len(cases),
        "distinct_births": len(births),
        "distinct_cognitive_refs": len(scoped),
        "physical_steps": sum(x["physical_steps"] for x in reports),
        "births": reports,
        "no_causal_truth_claim": True,
        "detector_calibration_validated": False,
    }


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--cohort-dir", type=Path, required=True)
    a = p.parse_args()
    print(json.dumps(audit_cohort(a.cohort_dir), sort_keys=True))
