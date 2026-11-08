"""Observer-only R-depletion-v1 endpoint; no runner or hidden depletion clock.

Local absence must follow this individual's positive uptake at that location.
Available capture and paid processing are distinct. The resource sidecar is not
covered by the original evidence chain: joins check consistency, not authenticity.
"""
from __future__ import annotations

from math import isclose, isfinite

SCHEMA = "i3-stage0-revision/v1"
DEFINITION = "R-depletion-v1"
UPTAKE_TOL = 1e-9  # Same physical-uptake convention as ResourceObserver.
FUNDING = {
    "NO_PROCESSING_BUDGET": "no_processing_budget",
    "NO_FUNDED_SCORE": "no_funded_score",
    "NO_FUNDED_MOTOR": "control_rejected",
    "FUNDED": "action_admitted",
}
UPPER_COST_POLICY = "candidate_f_shadow_upper_cost_reference_controller_v1"
UPPER_COST_SCHEMA = "i3-candidate-f-shadow-cost-reference-choice/v1"
CANDIDATE_H_POLICY = "personal_relevance_candidate_h_v1"
CANDIDATE_I_POLICIES = frozenset((
    "personal_shared_prior_candidate_i_v1",
    "personal_shared_prior_candidate_i_omega0_ablation_v1",
))
_H_COMPLETE_ROUTES = frozenset(("P1.3_FINAL", "CANDIDATE_F_FINAL"))
_I_COMPLETE_ROUTES = frozenset((
    "P1.3_BASE_FINAL", "INFORMATION_FINAL", "POST_CONTACT_CANDIDATE_H"))
_COMPLETE_H_PROBE_FUNDING = frozenset(("FUNDED", "NO_FUNDED_MOTOR"))
_WORK_KEYS = ("cycles", "simulated_steps", "memory_items", "replays")


COMPOSITE_RELEVANCE_PROBE_FUNDING = "NO_FUNDED_RELEVANCE_PROBE"
_COMPOSITE_INCOMPLETE_PROBE_FUNDING = frozenset(
    ("NO_PROCESSING_BUDGET", "NO_FUNDED_SCORE"))


def _normalize_processing_status(row, event):
    """Validate public funding/outcome and return the base processing class.

    Historical rows normalize to themselves. Candidate-H's one declared
    composite probe-failure status normalizes only through its nested
    incomplete Stage-A funding receipt. Unknown composite statuses fail closed.
    """
    if type(row) is not dict or type(event) is not dict:
        raise ValueError("invalid resource processing receipt")
    info = row.get("info")
    if type(info) is not dict:
        raise ValueError("missing decision info")
    public = event.get("decision_funding")
    if info.get("funding") != public:
        raise ValueError("resource processing status disagreement")

    if public in FUNDING:
        normalized = public
    elif public == COMPOSITE_RELEVANCE_PROBE_FUNDING:
        normalized = info.get("candidate_h_probe_funding")
        if normalized not in _COMPOSITE_INCOMPLETE_PROBE_FUNDING:
            raise ValueError("invalid composite relevance-probe funding")
    else:
        raise ValueError("resource processing status disagreement")

    expected = FUNDING[normalized]
    observer = info.get("observer")
    if (type(observer) is not dict or
            event.get("decision_outcome") != expected or
            observer.get("decision_outcome") != expected):
        raise ValueError("resource processing status disagreement")
    return {
        "public": public,
        "normalized": normalized,
        "processing_paid": normalized != "NO_PROCESSING_BUDGET",
        "expected_outcome": expected,
    }


def _position(value):
    if (type(value) not in (tuple, list) or len(value) != 2 or
            any(type(x) is not int for x in value)):
        raise ValueError("invalid personal position")
    return tuple(value)


def _timeline(events, *, steps_lived, horizon, terminal):
    """Pure endpoint arithmetic on joined events, NOT a life receipt verifier."""
    if (type(steps_lived) is not int or type(horizon) is not int or
            horizon < 1 or not 0 <= steps_lived <= horizon or
            terminal not in ("dead", "censored") or
            (terminal == "censored" and steps_lived != horizon)):
        raise ValueError("invalid endpoint context")
    if len(events) != steps_lived:
        raise ValueError("incomplete endpoint events")
    used = {}
    origin = available = processed = reacquired = prior_use = None
    for i, event in enumerate(events, 1):
        if set(event) != {"step", "position", "water_here", "processing_paid", "positive_drink"}:
            raise ValueError("invalid endpoint event fields")
        if type(event["step"]) is not int or event["step"] != i:
            raise ValueError("nonsequential endpoint events")
        pos = _position(event["position"])
        for flag in ("water_here", "processing_paid", "positive_drink"):
            if type(event[flag]) is not bool:
                raise ValueError("endpoint flags must be boolean")
        if event["positive_drink"] and not (event["water_here"] and event["processing_paid"]):
            raise ValueError("positive drink needs local water and paid processing")
        # Availability is observed BEFORE this step's action; no stock read.
        if available is None and not event["water_here"] and pos in used:
            origin, available, prior_use = pos, i, used[pos]
        if (available is not None and processed is None and pos == origin and
                not event["water_here"] and event["processing_paid"]):
            processed = i
        if event["positive_drink"]:
            if available is not None and reacquired is None and pos != origin:
                reacquired = i
            used[pos] = i
    status = ("NO_EXPOSURE" if available is None else
              "REACQUIRED" if reacquired is not None else "EXPOSED_NO_REACQUISITION")
    return {
        "schema": SCHEMA, "endpoint_definition": DEFINITION, "status": status,
        "no_exposure_reason": ("NO_PRIOR_POSITIVE_UPTAKE" if not used else
                               "NO_LOCAL_ABSENCE") if available is None else None,
        "origin_personal_position": list(origin) if origin is not None else None,
        "origin_previous_uptake_step": prior_use,
        "first_available_absence_decision": available,
        "first_paid_absence_decision": processed,
        "alternative_positive_uptake_step": reacquired,
        # Decision e starts at boundary e-1; uptake s finishes at boundary s.
        "latency_from_available_steps": (reacquired - available + 1
                                         if reacquired is not None else None),
        "latency_from_paid_steps": (reacquired - processed + 1
                                    if reacquired is not None and processed is not None
                                    and processed <= reacquired else None),
        "observed_followup_steps": steps_lived - available + 1 if available is not None else None,
        "terminal": terminal, "steps_lived": steps_lived, "horizon": horizon,
        "interpretation": "BEHAVIORAL_REACQUISITION_NOT_PROOF_OF_INTERNAL_BELIEF_REVISION",
    }


def _work_vector(value, label):
    if (type(value) is not dict or set(value) != set(_WORK_KEYS) or
            any(type(value[k]) is not int or value[k] < 0 for k in _WORK_KEYS)):
        raise ValueError("invalid " + label + " work vector")
    return value


def _work_sum(left, right):
    return {
        key: left[key] + right[key]
        for key in _WORK_KEYS
    }


def _body_receipt_matches(row, info, key, label):
    claimed = info.get(key)
    actual = row.get("funding_phases", {}).get(
        "decision", {}).get("body_after_debit")
    if (type(claimed) not in (tuple, list)
            or type(actual) not in (tuple, list)
            or len(claimed) != 5 or len(actual) != 5
            or any(type(x) not in (int, float) or not isfinite(x)
                   for x in (*claimed, *actual))
            or max(abs(a - b) for a, b in zip(claimed, actual)) > 1e-12):
        raise ValueError(label + " body settlement mismatch")


def _multiphase_work(row, total_work, prefix, *, owner):
    """Authenticate one Stage-A + Stage-B receipt and return processing work."""
    info = row.get("info", {})
    if type(info) is not dict:
        raise ValueError("missing multi-phase processing receipt")
    stage_a = _work_vector(
        info.get(prefix + "_stage_a_work"), prefix + " Stage A")
    stage_b = _work_vector(
        info.get(prefix + "_stage_b_work"), prefix + " Stage B")
    claimed = _work_vector(
        info.get(prefix + "_total_work"), prefix + " total")
    if _work_sum(stage_a, stage_b) != claimed or claimed != total_work:
        raise ValueError("multi-phase processing work mismatch")
    _body_receipt_matches(
        row, info, prefix + "_body_after_cognition", prefix)
    if owner == "stage_a":
        return stage_a
    if owner == "stage_b":
        return stage_b
    raise ValueError("unknown multi-phase processing owner")


def _processing_work(life, row, total_work):
    """Return the work block governed by the public processing status.

    Total decision work always remains the physical bill. Some declared
    multi-phase policies have earlier paid cognition that does not own the
    public P1.3 processing status, so the reducer authenticates the phase
    receipt and applies the historical base-block predicate to its actual
    processing owner only.
    """
    total_work = _work_vector(total_work, "decision")
    manifest_policy = (
        life.get("manifest", {}).get("experimental_policy", {}) or {}
    ).get("name")
    info = row.get("info", {})

    if manifest_policy == UPPER_COST_POLICY:
        if info.get("experimental_policy") != UPPER_COST_POLICY:
            raise ValueError("upper-cost trace policy mismatch")
        cc = info.get("cost_control")
        if type(cc) is not dict or cc.get("schema") != UPPER_COST_SCHEMA:
            raise ValueError("missing upper-cost processing receipt")
        if (cc.get("motor_authority") != "P1.3_REFERENCE_ONLY" or
                cc.get("candidate_motor_authority") is not False or
                cc.get("settlement_authority") !=
                "CUMULATIVE_V2_PHASE_START_BODY"):
            raise ValueError("upper-cost processing authority mismatch")
        gap = cc.get("sequential_settlement_max_abs_gap")
        if type(gap) not in (int, float) or gap < 0 or gap > 1e-12:
            raise ValueError("upper-cost processing settlement mismatch")

        shadow = _work_vector(
            cc.get("candidate_shadow_work"), "candidate shadow")
        reference = _work_vector(
            cc.get("reference_choice_work"), "reference choice")
        claimed = _work_vector(cc.get("total_work"), "upper-cost total")
        summed = {k: shadow[k] + reference[k] for k in _WORK_KEYS}
        if summed != claimed or claimed != total_work:
            raise ValueError("upper-cost processing work mismatch")
        return reference

    if manifest_policy == CANDIDATE_H_POLICY:
        route = info.get("candidate_h_route")
        if route == "PROBE_UNFUNDED":
            return total_work
        if route not in _H_COMPLETE_ROUTES:
            raise ValueError("unknown Candidate-H processing route")
        if info.get("candidate_h_probe_funding") not in _COMPLETE_H_PROBE_FUNDING:
            raise ValueError("incomplete Candidate-H final processing receipt")
        return _multiphase_work(
            row, total_work, "candidate_h", owner="stage_b")

    if manifest_policy in CANDIDATE_I_POLICIES:
        route = info.get("candidate_i_route")
        if route == "PROBE_UNFUNDED":
            return total_work
        if route not in _I_COMPLETE_ROUTES:
            raise ValueError("unknown Candidate-I processing route")
        if route == "POST_CONTACT_CANDIDATE_H":
            if (info.get("candidate_i_first_contact_omega_used") is not False
                    or info.get("candidate_i_post_contact_source")
                    != "CANDIDATE_H_1163_UNCHANGED"
                    or info.get("candidate_h_route") not in _H_COMPLETE_ROUTES
                    or info.get("candidate_h_probe_funding")
                    not in _COMPLETE_H_PROBE_FUNDING):
                raise ValueError("invalid Candidate-I post-contact processing receipt")
            return _multiphase_work(
                row, total_work, "candidate_h", owner="stage_b")

        if info.get("candidate_i_probe_funding") != "FUNDED":
            raise ValueError("incomplete Candidate-I final processing receipt")
        owner = (
            "stage_a" if route == "INFORMATION_FINAL"
            else "stage_b")
        return _multiphase_work(
            row, total_work, "candidate_i", owner=owner)

    return total_work


def _resource_events(life):
    """Join consumed sidecar fields to the full trace; never inspect source stocks."""
    sidecar = life["observer_resource_acquisition"]
    if sidecar["schema"] != "i3-p5d-resource-acquisition-observer/v1":
        raise ValueError("unknown resource witness")
    rows, events = life["trace"], sidecar["steps"]
    if len(events) != len(rows):
        raise ValueError("incomplete resource sidecar")
    spawn = _position(life["manifest"]["world"]["spawn"])
    previous = spawn
    decay = life["manifest"]["world"]["laws"]["water_decay"]
    joined = []
    for row, event in zip(rows, events):
        if type(event["step"]) is not int or event["step"] != row["t"]:
            raise ValueError("nonsequential resource sidecar")
        phases = row["funding_phases"]
        for side, original in (("action", "action"), ("param", "param"),
                               ("chosen_option", "option"), ("death_causes", "dead"),
                               ("world_position_observer_only", "pos"),
                               ("body_after_paid_learning", "body")):
            if event[side] != row[original]:
                raise ValueError("resource/trace disagreement: " + side)
        pos = _position(event["personal_position"])
        if pos != tuple(p - s for p, s in zip(previous, spawn)):
            raise ValueError("resource position is not the pre-action personal position")
        previous = _position(row["pos"])
        before = phases["decision"]["body_before"]
        physical = phases["learning"]["body_before"]
        if (event["body_before_decision"] != before or
                event["body_after_physics"] != physical):
            raise ValueError("resource body/phase disagreement")
        for phase in ("decision", "learning"):
            if (event["paid_" + phase + "_work"] != phases[phase]["work"] or
                    event["phase_payment"][phase] != {
                        "work": phases[phase]["work"], "accounting": phases[phase]["accounting"]}):
                raise ValueError("resource funding/trace disagreement")
        processing = _normalize_processing_status(row, event)
        funding = processing["normalized"]
        paid = processing["processing_paid"]
        work = _processing_work(
            life, row, phases["decision"]["work"])
        if (paid and work["cycles"] < 3) or (not paid and any(work.values())):
            raise ValueError("processing status contradicts paid base block")
        if (funding == "FUNDED") != (row["action"] is not None):
            raise ValueError("processing status contradicts admitted action")
        for flag in ("capture_here_water", "positive_water_uptake"):
            if type(event[flag]) is not bool:
                raise ValueError("resource flags must be boolean")
        uptake = event["water_uptake_above_decay"]
        expected = physical[2] - max(0.0, before[2] - decay) if row["action"] == "boire" else None
        if expected is None:
            if uptake is not None or event["positive_water_uptake"]:
                raise ValueError("water uptake without a drink")
        elif (type(uptake) not in (int, float) or not isfinite(uptake) or
              not isclose(uptake, expected, rel_tol=0.0, abs_tol=UPTAKE_TOL) or
              event["positive_water_uptake"] != (expected > UPTAKE_TOL) or
              not event["capture_here_water"]):
            raise ValueError("water command is not verified positive uptake")
        joined.append({"step": row["t"], "position": pos,
                       "water_here": event["capture_here_water"],
                       "processing_paid": paid,
                       "positive_drink": expected is not None and expected > UPTAKE_TOL})
    return joined


def revision_receipt(life: dict, *, expected_protocol: str,
                     expected_source_sha256: str) -> dict:
    """Analyze an existing complete paid life, without running or changing it.

The caller still binds family/seed/genome/intervention to a prospective design.
Current pinned Mind processes local `here` after its prepaid three-cycle base;
neighbor sensor misses and hidden world schedules cannot start this endpoint.
"""
    from i3.lab.stage0_energy import energy_receipt

    paid = energy_receipt(life, expected_protocol=expected_protocol,
                          expected_source_sha256=expected_source_sha256)
    try:
        result = _timeline(_resource_events(life), steps_lived=paid["steps_lived"],
                           horizon=paid["horizon"], terminal=paid["terminal"])
    except (KeyError, TypeError, OverflowError) as exc:
        raise ValueError("missing or invalid revision witness") from exc
    result.update({"manifest_id": paid["manifest_id"], "evidence_head": paid["evidence_head"],
                   "source_sha256": paid["source_sha256"], "death_causes": paid["death_causes"],
                   "sidecar_custody": "JOINED_NOT_AUTHENTICATED_BY_ORIGINAL_CHAIN",
                   "scientific_verdict": "NOT_EVALUATED"})
    return result
