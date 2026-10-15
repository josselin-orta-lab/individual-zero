"""Read-only independent audit for versioned first-person dual-scope receipts.

Cannot certify WorldBody physical truth, only committed sensory provenance.
"""
from dataclasses import dataclass
import json
from math import isfinite

from .determinism import deterministic_id
from .independent_journal_audit import audit_export_bytes
from .stage12_goal_progress_audit import _number

VERSION = "stage12-dual-scope-agency-v1"
SENSOR = "stage12-dual-scope-body-cue-v1"


@dataclass(frozen=True)
class DualScopeAudit:
    head_hash: str
    precommits: int
    judgements: int
    unavailable: int
    unresolved: int


def audit_stage12_dual_scope(content: bytes, *, expected_head=None, expected_count=None):
    base = audit_export_bytes(content, expected_head=expected_head,
                              expected_count=expected_count)
    rows = [json.loads(raw) for raw in content.splitlines()]
    commitments = {}
    proximal_pre = {}
    proximal_judgements = {}
    captures = {}
    charges = {}
    dual = {}
    observed_refs = set()
    for i, row in enumerate(rows):
        e = row["causal_event"]
        k = e.get("kind")
        if k == "perceptual_capture":
            key = (e.get("t_monde"), e.get("attempt_ref"))
            if e.get("data", {}).get("dual_scope_capture_schema") == SENSOR:
                if key in captures:
                    raise ValueError("duplicate dual-scope sensory receipt")
                captures[key] = (i, e["data"])
        elif k == "stage12_goal_agency_precommitted":
            proximal_pre[e["data"]["assessment_ref"]] = (i, e)
        elif k == "stage12_goal_agency_judgement":
            proximal_judgements[e["data"]["assessment_ref"]] = (i, row["event_id"], e)
        elif k == "compute_charge" and e.get("data", {}).get("operation") == "goal_outcome_responsibility_assessment":
            charges.setdefault((e.get("t_monde"), e.get("attempt_ref")), []).append((i,e))
        elif k == "stage12_outcome_responsibility_precommitted":
            d = e.get("data")
            if (e.get("emitter") != "stage4-runtime" or type(d) is not dict
                    or d.get("policy_version") != VERSION):
                raise ValueError("uncontracted dual-scope precommit")
            ref = d.get("proximal_assessment_ref")
            if ref in commitments or ref not in proximal_pre:
                raise ValueError("duplicate or missing dual-scope proximal precommit")
            j,p = proximal_pre[ref]
            if (j>=i or e["attempt_ref"] != p["attempt_ref"]
                    or e["t_monde"] != p["t_monde"]
                    or d.get("intent_ref") != p["data"].get("intent_ref")
                    or d.get("life_id") != p["data"].get("life_id")
                    or d.get("sent_world_step") != e["t_monde"]
                    or d.get("observe_world_step") != e["t_monde"]+1
                    or d.get("goal_measure") != p["data"].get("goal_measure")):
                raise ValueError("dual scope precommit lineage mismatch")
            cue = captures.get((e["t_monde"],e["attempt_ref"]))
            if cue is None or cue[0]>=i:
                raise ValueError("dual-scope baseline lacks sensory capture")
            body=cue[1].get("dual_scope_visible_body")
            if type(body) is not dict:
                raise ValueError("invalid dual-scope body cue")
            baseline=_number(body.get(d["goal_measure"]))
            if baseline != _number(d.get("baseline")):
                raise ValueError("dual-scope baseline contradicts perception")
            commitments[ref] = (i, e, d)
        elif k == "stage12_outcome_responsibility_judgement":
            d=e.get("data")
            if (e.get("emitter")!="stage4-runtime" or type(d) is not dict
                or d.get("policy_version")!=VERSION):
                raise ValueError("uncontracted dual-scope judgement")
            ref=d.get("proximal_assessment_ref")
            if ref in observed_refs or ref not in commitments or ref not in proximal_judgements:
                raise ValueError("duplicate or orphaned dual-scope judgement")
            pi,pre,pd=commitments[ref]
            ji, proximal_id,prox=proximal_judgements[ref]
            if (pi>=ji or ji>=i or e["t_monde"] != prox["t_monde"]
                or e["attempt_ref"] != prox["attempt_ref"]
                or d.get("proximal_judgement_ref")!=proximal_id
                or d.get("proximal_agency")!=prox["data"].get("subjective_agency")
                or d.get("intent_ref")!=pd["intent_ref"]
                or d.get("life_id")!=pd["life_id"]
                or d.get("assessment_ref")!="scope:"+ref
                or d.get("sent_world_step")!=pd["sent_world_step"]
                or d.get("observed_world_step")!=e["t_monde"]):
                raise ValueError("dual-scope judgement lineage mismatch")
            charge=charges.get((e["t_monde"],e["attempt_ref"]),[])
            if (len(charge)!=1 or not ji<charge[0][0]<i
                or charge[0][1]["data"].get("module")!="action_control"
                or type(charge[0][1]["data"].get("accepted")) is not bool
                or type(charge[0][1]["data"].get("requested_uc")) is not int
                or charge[0][1]["data"]["requested_uc"] < 1):
                raise ValueError("dual-scope uncharged assessment")
            paid=charge[0][1]["data"]["accepted"]
            available=paid and e["t_monde"]==pd["observe_world_step"]
            post=captures.get((e["t_monde"],e["attempt_ref"]))
            if available:
                if post is None or post[0]>=ji:
                    raise ValueError("dual-scope judgement missing lived perception")
                current=post[1]
                inv=current.get("agency_visible_inventory")
                pos=current.get("position")
                body=current.get("dual_scope_visible_body")
                if not isinstance(inv,dict) or not isinstance(pos,dict) or not isinstance(body,dict):
                    raise ValueError("dual-scope sensory fields missing")
                expected=deterministic_id(
                    "stage12-dual-scope-perception-v1", d["life_id"],
                    e["t_monde"],pos["x"],pos["y"],
                    tuple(sorted(inv.items())),
                    tuple(sorted((k,_number(v)) for k,v in body.items())))
                # Canonical JSON $f64 decoding must retain the exact runtime
                # float meaning when reconstructing the cue id.
                if d.get("cue_ref") != expected:
                    raise ValueError("dual-scope sensory cue reference mismatch")
                baseline=_number(pd["baseline"])
                after=_number(body.get(pd["goal_measure"]))
                observed=("improved" if after>baseline else "not_improved") if (
                    baseline is not None and after is not None and pd["goal_measure"]!="spatial_distance"
                ) else "unknown"
            else:
                observed="unavailable"
            if (d.get("observed_outcome")!=observed
                or d.get("subjective_responsibility")!=("unknown" if available else "unavailable")
                or (not available and d.get("cue_ref") is not None)):
                raise ValueError("dual-scope causal claims unsupported")
            observed_refs.add(ref)
    if sum(len(x) for x in charges.values())!=len(observed_refs):
        raise ValueError("orphaned dual-scope UC debit")
    pending=set(commitments)-observed_refs
    for ref in pending:
        if base.world_steps_closed>commitments[ref][2]["sent_world_step"]:
            raise ValueError("missing due dual-scope judgement")
    return DualScopeAudit(base.head_hash,len(commitments),len(observed_refs),
                          sum(1 for ref in observed_refs if False),len(pending))
