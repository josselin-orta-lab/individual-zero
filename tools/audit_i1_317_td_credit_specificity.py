#!/usr/bin/env python3
"""#317 read-only TD intervention specificity audit, on TWO sealed physical WALs.

This tests learned *action-signature* credit, NOT an entity's affordance.
Compare all Q reads before the first divergent physical movement; permit
different normalized Competition evidence because options compete. Neither
the living actor nor any original archived journal is ever changed.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from audit_i1_spatial_navigation_314 import audit as audit_wal


def _number(raw):
    from math import isfinite
    if type(raw) in (int, float):
        val = float(raw)
    elif (isinstance(raw, dict) and set(raw) == {"$f64"}
          and isinstance(raw["$f64"], str)):
        val = float.fromhex(raw["$f64"])
    else:
        raise ValueError("missing or malformed finite number")
    if not isfinite(val):
        raise ValueError("non-finite TD/evidence value")
    return val


def _data(event):
    value = event.get("data")
    return value if isinstance(value, dict) else {}


def _seal(path, public):
    if not path.is_file() or path.is_symlink():
        raise ValueError("missing/unsafe original WAL")
    raw = path.read_bytes()
    digest = sha256(raw).hexdigest()
    if digest != public["wal_sha256"]:
        raise ValueError("WAL SHA-256 changed since experiment")
    with TemporaryDirectory(prefix="i1-317-td-independent-") as root:
        copy = Path(root) / "sealed.wal"
        copy.write_bytes(raw)
        proof = audit_wal(copy)
    if (proof["independent_hash_chain_verified"] is not True
        or proof["journal_head"] != public["journal_head"]
        or proof["journal_entries"] != public["journal_entries"]):
        raise ValueError("independent WAL chain or custody failure")
    events = [json.loads(line)["causal_event"] for line in raw.splitlines()]
    if len(events) != proof["journal_entries"]:
        raise ValueError("classified bytes differ from verified journal")
    return events, {
        "wal_sha256": digest, "journal_head": proof["journal_head"],
        "journal_entries": proof["journal_entries"],
        "independent_hash_chain_verified": True,
    }


def physical_steps(events):
    grouped = defaultdict(lambda: defaultdict(list))
    for i, event in enumerate(events):
        step = event.get("t_monde")
        if (type(step) is int and step > 0
            and event.get("kind") in {
                "command_admitted", "command_experienced",
                "world_transition_experienced", "step_closed"
            }):
            grouped[step][event["kind"]].append((i, event))
    results = {}
    for t, g in sorted(grouped.items()):
        if any(len(g[name]) != 1 for name in (
            "command_admitted", "command_experienced",
            "world_transition_experienced", "step_closed"
        )):
            raise ValueError(f"unverifiable physical world step {t}")
        (ia, a), (ic, c), (iw, w), (iz, z) = (
            g[name][0] for name in (
                "command_admitted", "command_experienced",
                "world_transition_experienced", "step_closed"))
        adm, close = _data(a), _data(z)
        if (not ia < ic < iw < iz
            or a.get("attempt_ref") != c.get("attempt_ref")
            or a.get("attempt_ref") != w.get("attempt_ref")
            or a.get("attempt_ref") != z.get("attempt_ref")
            or adm.get("command_hash") != c.get("command_hash")
            or adm.get("primitive") != c.get("primitive")
            or close.get("outcome") != "normal"
            or close.get("applied_command_count") != 1
            or close.get("world_advance_count") != 1):
            raise ValueError(f"invalid physical command custody at {t}")
        results[t] = {
            "primitive": c.get("primitive"),
            "position": w.get("position_after"),
            "body": w.get("body_after"),
            "effects": w.get("effects"),
        }
    if sorted(results) != list(range(1, len(results) + 1)):
        raise ValueError("gapped world-step physical execution")
    return results


def _evaluations(events, cutoff):
    result = defaultdict(list)
    for event in events:
        t = event.get("t_monde")
        if (event.get("kind") != "stage8_option_evaluation"
            or type(t) is not int or not 1 <= t <= cutoff):
            continue
        d = _data(event)
        sig = d.get("learning_signature")
        if not isinstance(sig, str) or not sig:
            raise ValueError("unidentified Stage8 learning signature")
        status = d.get("learned_value_status")
        if status not in ("learned", "unlearned"):
            raise ValueError("uncertain Stage8 learned status")
        q = (None if status == "unlearned"
             else _number(d.get("learned_value")))
        evidence = (None if d.get("evidence") is None
                    else _number(d["evidence"]))
        result[(t, sig)].append((status, q, evidence))
    return result


def contrast_learned_q(control_events, ablated_events, target, cutoff):
    """Pure synthetic-testable temporal control; no WAL authentication here."""
    if (not isinstance(target, str) or
        not target.startswith("memory_place_return:")
        or type(cutoff) is not int or cutoff < 2):
        raise ValueError("unbounded/invalid specificity target")
    a = _evaluations(control_events, cutoff)
    b = _evaluations(ablated_events, cutoff)
    if not a or set(a) != set(b):
        raise ValueError("unmatched first-person Stage8 evaluation set")
    target_difference_steps = set()
    control_comparisons = 0
    non_target_q_differences = []
    non_target_evidence_differences = []
    duplicate_counts_at_decision = 0
    for t, sig in sorted(a):
        left, right = a[(t, sig)], b[(t, sig)]
        # Once the divergent decision starts, one arm may reconsider the
        # same candidate several more cycles. Compare the first shared
        # evaluation only, and record the unequal census separately.
        if t < cutoff and len(left) != len(right):
            raise ValueError("pre-divergence deliberation counts differ")
        if t == cutoff and len(left) != len(right):
            duplicate_counts_at_decision += 1
        for j in range(min(len(left), len(right))):
            lstatus, lq, lev = left[j]
            rstatus, rq, rev = right[j]
            if sig == target:
                if (lstatus, lq) != (rstatus, rq):
                    target_difference_steps.add(t)
            else:
                control_comparisons += 1
                if (lstatus, lq) != (rstatus, rq):
                    non_target_q_differences.append({
                        "t_monde": t, "signature": sig,
                        "control_q": lq, "ablated_q": rq,
                    })
                if t == cutoff and lev != rev:
                    non_target_evidence_differences.append({
                        "t_monde": t, "signature": sig,
                        "control_evidence": lev,
                        "ablated_evidence": rev,
                    })
    return {
        "first_target_q_difference_step": (
            min(target_difference_steps) if target_difference_steps else None),
        "target_q_difference_steps": sorted(target_difference_steps),
        "non_target_learned_q_compared": control_comparisons,
        "non_target_q_differences": non_target_q_differences,
        "non_target_evidence_differences_at_divergent_step":
            non_target_evidence_differences,
        "different_evaluation_counts_at_divergent_step":
            duplicate_counts_at_decision,
        "interpretation": (
            "same learned Q in other signatures tests direct TD isolation; "
            "option competition may indirectly alter other evidence. "
            "Neither result establishes causal utility of an entity."
        ),
    }


def _td_at(events, t, previous):
    candidates = [_data(e) for e in events
                  if e.get("t_monde") == t
                  and e.get("kind") == "td_update_published"
                  and _data(e).get("previous_signature") == previous]
    if len(candidates) != 1:
        raise ValueError("ambiguous/missing originally experienced TD update")
    return candidates[0]


def audit_pair(folder):
    report_path = folder / "report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    if (report.get("schema") != "i1-317-operator-td-counterfactual-v1"
        or report.get("status") != "COMPLETED_DIAGNOSTIC_NO_GLOBAL_GO"
        or report.get("population_go") is not False
        or report.get("entity_causality_proven") is not False):
        raise ValueError("not a complete, non-GO diagnostic")
    arms = report["arms"]
    records = {}
    physical = {}
    custody = {}
    for label in ("control", "memory-credit-ablated"):
        public = arms[label]
        rel = Path(public["wal_file"])
        if rel.is_absolute() or ".." in rel.parts:
            raise ValueError("unsafe WAL relative path")
        events, sealed = _seal(folder / rel, public)
        records[label] = events
        physical[label] = physical_steps(events)
        custody[label] = sealed
        if len(physical[label]) != public["steps_lived"]:
            raise ValueError("life horizon disagrees with physical WAL")
    control, ablated = physical["control"], physical["memory-credit-ablated"]
    divergence = next(
        (t for t in sorted(set(control) & set(ablated))
         if control[t] != ablated[t]), None)
    if (divergence is None
        or divergence != report["comparison"]["first_physical_divergence_step"]
        or divergence != report["later_decision_step"]):
        raise ValueError("physical divergence not reproduced")
    if control[divergence]["primitive"] != "se_deplacer":
        raise ValueError("missing control movement")
    if ablated[divergence]["primitive"] != "dormir":
        raise ValueError("ablation did not lead to experienced sleep")
    sig = report["memory_signature"]
    step = report["targeted_td_step"]
    if (not 1 < step < divergence
        or report.get("identical_world_steps_before_credit") != step - 1):
        raise ValueError("incorrect intervention temporal horizon")
    prev = arms["control"]["td_at_credit_step"]["previous_signature"]
    first = _td_at(records["control"], step, prev)
    second = _td_at(records["memory-credit-ablated"], step, prev)
    if (first["previous_signature"] != second["previous_signature"]
        or first["next_signature"] != second["next_signature"]
        or _number(first["return_g"]) != _number(second["return_g"])
        or _number(first["delta"]) != _number(second["delta"])
        or sorted(x for x in first["updated_signatures"] if x != sig)
        != sorted(second["updated_signatures"])
        or sig not in first["updated_signatures"]
        or sig in second["updated_signatures"]):
        raise ValueError("TD intervention leaked to unrelated action credit")
    specificity = contrast_learned_q(
        records["control"], records["memory-credit-ablated"], sig,
        divergence)
    if (not specificity["target_q_difference_steps"]
        or specificity["non_target_q_differences"]
        or specificity["non_target_learned_q_compared"] < 1):
        raise ValueError("failed TD specificity proof")
    return {
        "schema": "i1-317-td-credit-specificity/v1",
        "source_report_sha256": sha256(report_path.read_bytes()).hexdigest(),
        "code_sha_of_physical_lives": report["code_sha"],
        "world": report["preset"], "seed": report["seed"],
        "custody": custody,
        "intervention_td_step": step,
        "first_physical_divergence_step": divergence,
        "decision_actions": {
            "control": control[divergence]["primitive"],
            "memory-credit-ablated": ablated[divergence]["primitive"],
        },
        "specificity": specificity,
        "direct_other_td_updates_unchanged": True,
        "causal_status": "operator-intervention-on-learned-action-credit",
        "entity_causality_proven": False,
        "heldout_population_go": False,
        "scientific_verdict": "NO-GO_GLOBAL",
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input-dir", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    if args.output.exists():
        raise FileExistsError("never replace original scientific evidence")
    report = audit_pair(args.input_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n",
                           encoding="utf-8")
    print("I1_317_TD_CREDIT_SPECIFICITY_CERTIFIED")
    print(json.dumps({
        "physical_divergence": report["first_physical_divergence_step"],
        "first_target_q_divergence":
            report["specificity"]["first_target_q_difference_step"],
        "non_target_q_comparisons":
            report["specificity"]["non_target_learned_q_compared"],
        "non_target_q_changes":
            report["specificity"]["non_target_q_differences"],
        "other_competition_evidence_changes":
            report["specificity"][
                "non_target_evidence_differences_at_divergent_step"],
        "scientific_verdict": report["scientific_verdict"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
