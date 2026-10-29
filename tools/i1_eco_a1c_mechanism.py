"""A1-C observer-only causal-exposure gate on independently audited M11 paths.

Never certifies external Q floats or confuses later motor divergence with
better health. The caller has already verified the whole M11 chain, TD update
chronology, original birth, path continuity and all paired horizons.
"""
from collections import defaultdict
from i1_eco_a1_decision_join import _read_canonical_events


def _decisions(events):
    bycycle = defaultdict(lambda: {"stage8": {}, "competition": None,
                                     "proposals": []})
    for e in events:
        if e.get("kind") not in (
            "stage8_option_evaluation", "competition_cycle",
            "i1_local_opportunity_proposed",
            "i1_unknown_affordance_proposed"):
            continue
        key = (e.get("t_monde"), e.get("cycle"))
        if type(key[0]) is not int or type(key[1]) is not int:
            raise ValueError("missing M11 decision key")
        row = bycycle[key]
        if e["kind"] == "stage8_option_evaluation":
            opt = e["data"].get("option_ref")
            if opt in row["stage8"]:
                raise ValueError("duplicate Stage8 candidate")
            row["stage8"][opt] = e["data"]
        elif e["kind"] == "competition_cycle":
            if row["competition"] is not None:
                raise ValueError("duplicate Competition")
            row["competition"] = e["data"]
        else:
            row["proposals"].append(e["data"])
    return bycycle


def verify_mechanism(*, canonical_events, masked_events,
                     masked_reads, adapters, canonical_prefix,
                     masked_prefix, first_masked_step):
    """Report strict witness without filtering weak pairs or inventing a GO."""
    if (type(canonical_events) is not list
            or type(masked_events) is not list
            or type(masked_reads) is not list
            or type(adapters) is not list):
        raise ValueError("invalid A1-C M11 evidence")
    if first_masked_step is None:
        return {"mechanism_exposed": False, "reason": "NOT_EXPOSED",
                "first_masked_step": None, "first_motor_difference": None}
    if type(first_masked_step) is not int or first_masked_step < 1:
        raise ValueError("invalid A1-C intervention step")
    first_motor = next((
        i for i in range(1, min(len(canonical_prefix),len(masked_prefix)) + 1)
        if canonical_prefix[i-1] != masked_prefix[i-1]), None)
    if first_motor is None and len(canonical_prefix) != len(masked_prefix):
        first_motor = min(len(canonical_prefix),len(masked_prefix)) + 1
    if first_motor is not None and first_motor < first_masked_step:
        raise ValueError("A1-C motor divergence precedes masked learned Q")
    if first_motor is None:
        return {"mechanism_exposed": False, "reason": "EXPOSED_NO_MOTOR_EFFECT",
                "first_masked_step": first_masked_step,
                "first_motor_difference": None}
    if not any(r.get("masked") is True
               and r.get("original_status") == "learned"
               and r.get("step") == first_masked_step
               for r in masked_reads):
        raise ValueError("missing externally observed first learned Q intervention")
    c = _decisions(canonical_events)
    m = _decisions(masked_events)
    candidates = []
    for read in masked_reads:
        if (read.get("masked") is not True
                or read.get("original_status") != "learned"
                or read.get("step") is None
                or read["step"] < first_masked_step
                or read["step"] > first_motor):
            continue
        key = (read["step"], read["cycle"])
        event = m.get(key)
        if not event or event["competition"] is None:
            continue
        evaluated = {
            opt for opt, d in event["stage8"].items()
            if d.get("status") == "evaluated"}
        traces = {t.get("option_ref") for t in
                  event["competition"].get("traces", [])
                  if type(t) is dict}
        competitive = evaluated & traces
        if len(competitive) < 2:
            continue
        if read["source"] == "stage8_direct":
            opt = read.get("option_ref")
            if (opt in competitive and
                    event["stage8"][opt].get("learning_signature") ==
                    read["signature"]):
                candidates.append((key, opt, "direct"))
        elif read["source"] in ("planning_local", "planning_goal"):
            # A pending candidate may be evaluated in a later cycle. Require
            # an authentic Planning proposal in the original read cycle and
            # a later adapter row that agrees with a native M11 evaluation.
            from i1_eco_a1_decision_join import _signature
            for proposal in event["proposals"]:
                sig = proposal.get("learning_signature")
                if sig is None and type(proposal.get("command")) is dict:
                    sig = _signature(proposal["command"])
                if sig != read["signature"]:
                    continue
                opt = proposal.get("option_ref")
                for ad in adapters:
                    if (ad.get("signature") != sig
                            or ad.get("option_ref") != opt
                            or ad.get("delivered_status") != "unlearned"
                            or ad.get("step") is None
                            or (ad["step"], ad["cycle"]) < key
                            or ad["step"] > first_motor):
                        continue
                    later = m.get((ad["step"], ad["cycle"]))
                    if later and later["competition"] is not None:
                        later_evaluated = {
                            o for o,d in later["stage8"].items()
                            if d.get("status") == "evaluated"}
                        later_traces = {
                            t.get("option_ref") for t in
                            later["competition"].get("traces", [])
                            if type(t) is dict}
                        if (opt in later_evaluated & later_traces and
                                len(later_evaluated & later_traces) >= 2):
                            candidates.append((key, opt, "planning_pending"))
                            break
    # Native Stage8/Competition must differ on a decision cycle between
    # intervention and the first different motor command.
    changed_decisions = [
        k for k in (set(c) | set(m))
        if first_masked_step <= k[0] <= first_motor
        and ((c.get(k) or {}).get("stage8") !=
             (m.get(k) or {}).get("stage8")
             or (c.get(k) or {}).get("competition") !=
                (m.get(k) or {}).get("competition"))
    ]
    success = bool(candidates and changed_decisions)
    return {
        "mechanism_exposed": success,
        "reason": ("M11_LINKED_COMPETITIVE_Q_TO_MOTOR" if success
                   else "NO_COMPETITIVE_M11_CHAIN"),
        "first_masked_step": first_masked_step,
        "first_motor_difference": first_motor,
        "competitive_witness_count": len(candidates),
        "decision_divergence_cycles": len(changed_decisions),
        "scope": "M11_LINKED_EXTERNAL_Q_OBSERVER_NOT_PROOF_OF_BENEFIT",
    }


def audited_pair_mechanism(*, canonical, masked, first_masked_step):
    def events(row):
        return _read_canonical_events(
            path=row["database_path"], identity=row["identity"],
            audit=row["audited"])
    return verify_mechanism(
        canonical_events=events(canonical),
        masked_events=events(masked),
        masked_reads=masked["read_observations"],
        adapters=masked["pending_adapter_observations"],
        canonical_prefix=canonical["physical_prefix"],
        masked_prefix=masked["physical_prefix"],
        first_masked_step=first_masked_step,
    )
