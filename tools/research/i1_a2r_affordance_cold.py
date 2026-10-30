"""A2-R cold, independent arithmetic for I1 local affordance evidence.

This is NOT an I1 implementation, a birth, a cohort or a causal GO. It checks
the two FIRST-PERSON I1 affordance adapters against native proposal events,
a separately cold-verified TD/Q replay, and parameters from an independently
reconstructed source-born reference. It does NOT claim that Q changed a
motor action, that a local option was available to other agents, or that
other intrinsic/experimental evidence producers have been replayed.
"""
from __future__ import annotations

from math import isfinite, tanh
from i1_a2r_m11_cold import numeric

SCOPE = "A2R_COLD_NATIVE_Q_FULL_VECTOR_NOT_L3"
BASE_INSTRUMENTAL_SCORE = 0.35  # frozen source I1_SCORE, NOT predicted utility
TOL = 2e-9
KINDS = ("i1_local_opportunity_proposed", "i1_unknown_affordance_proposed")


def _num(value, label):
    v = numeric(value)
    if not isfinite(v):
        raise ValueError("nonfinite native " + label)
    return v


def _same(actual, expected, label):
    a, b = _num(actual, label), _num(expected, label)
    if abs(a - b) > TOL * max(1., abs(a), abs(b)):
        raise ValueError(label + ": M11 value differs from independent formula")


def _clamp(value):
    return max(-1., min(1., value))


def _unit(value):
    return max(0., min(1., value))


def audit_native_affordance_evidence(events, *, q_replay, birth):
    """Read-only audit of *both* goal-linked and goal-independent local I1.

    M11 events must first be authenticated by inspect_m11 and q_replay must
    match the final M11 Q owner. The birth reference must come from a pinned
    source, never a report.json or the original living runtime.
    """
    if (type(events) is not list or type(q_replay) is not dict
            or q_replay.get("scope") != SCOPE
            or q_replay.get("full_q_replay_verified") is not True
            or type(q_replay.get("stage8_observations")) is not list
            or type(birth) is not dict
            or birth.get("q_at_birth_empty") is not True
            or birth.get("identity") != q_replay.get("m11_identity")
            or birth.get("mode") != q_replay.get("mode")):
        raise ValueError("affordance auditor requires cold M11 and independent birth")

    temperament = birth.get("born_temperament")
    if type(temperament) is not dict:
        raise ValueError("no source-born temperament")
    exploration = _num(temperament.get("exploration_coefficient"), "exploration")
    uncertainty = _num(temperament.get("uncertainty_penalty_scale"), "uncertainty")
    scale = _num(birth.get("born_td_evidence_scale"), "TD evidence scale")
    if not scale > 0 or uncertainty < 0 or exploration < 0:
        raise ValueError("invalid frozen local instrumental parameters")

    # First index authentic source events. Exact M11 (step, cycle, option)
    # matching disallows a proposal from another occurrence or stale cycle.
    proposals = {}
    evaluations = {}
    intrinsics = {}
    for order, event in enumerate(events):
        if type(event) is not dict:
            raise ValueError("malformed M11 event")
        kind = event.get("kind")
        if kind not in (*KINDS, "stage8_option_evaluation",
                        "stage11_intrinsic_evaluation"):
            continue
        data = event.get("data")
        key = (event.get("t_monde"), event.get("cycle"),
               data.get("option_ref") if type(data) is dict else None)
        if (type(key[0]) is not int or type(key[1]) is not int
                or type(key[2]) is not str or not key[2]):
            raise ValueError("malformed M11 per-cycle option provenance")
        registry = (proposals if kind in KINDS else
                    evaluations if kind == "stage8_option_evaluation" else
                    intrinsics)
        if key in registry:
            raise ValueError("duplicate M11 option evidence/proposal")
        registry[key] = (kind, data, order)

    q_observations = {}
    for row in q_replay["stage8_observations"]:
        if type(row) is not dict:
            raise ValueError("bad cold Q evidence row")
        key = (row.get("step"), row.get("cycle"), row.get("option"))
        if key in q_observations:
            raise ValueError("duplicate cold Q option")
        q_observations[key] = row
    if set(evaluations) != set(q_observations):
        raise ValueError("Stage8 original events differ from cold Q replay")

    covered = set()
    verification = []
    for key, (kind, proposal, index) in proposals.items():
        # Not every registered proposal must reach evaluation (UC limits).
        if key not in evaluations:
            continue
        stage_kind, data, position = evaluations[key]
        q = q_observations[key]
        signature = data.get("learning_signature")
        if kind == KINDS[0]:
            origin_signature = proposal.get("learning_signature")
        else:
            # Goal-linked proposals publish option_ref but not the signature.
            # Reconstruct the signature from the explicit command suffix
            # of that option's occurrence, never assume a missing key.
            token = ":t" + str(key[0]) + ":"
            if not key[2].startswith("option:i1:affordance:") or token not in key[2]:
                raise ValueError("goal-linked option has no grounded occurrence")
            origin_signature = "i1:affordance:" + key[2].rsplit(token, 1)[1]
        if (position <= index
                or type(signature) is not str
                or signature != origin_signature
                or q.get("signature") != origin_signature
                or q.get("status") != data.get("learned_value_status")
                or proposal.get("learned_value_status") != data.get("learned_value_status")):
            raise ValueError("affordance proposal is not source of native Stage8 Q")
        if (data.get("intrinsic_status") != "not_applicable"
                or data.get("intrinsic_value") is not None
                or data.get("simulated_value_status") != "unavailable"
                or data.get("simulated_value") is not None
                or data.get("status") != "evaluated"):
            raise ValueError("affordance stage8 was overwritten by another evaluator")
        if kind == KINDS[0]:
            if not key[2].startswith(f"option:i1:local:t{key[0]}:"):
                raise ValueError("local affordance carries wrong first-person option")
            prior = _unit(BASE_INSTRUMENTAL_SCORE * (1 + .25 * exploration)
                          / (1 + .25 * uncertainty))
        else:
            if not key[2].startswith("option:i1:affordance:"):
                raise ValueError("goal-linked affordance has another option source")
            _same(proposal.get("temperament_exploration"), exploration,
                  "source-born exploration")
            _same(proposal.get("uncertainty_penalty_scale"), uncertainty,
                  "source-born uncertainty")
            pressure = _num(proposal.get("goal_pressure"), "goal pressure")
            if not 0 <= pressure <= 1.:
                raise ValueError("invalid first-person goal pressure")
            prior = _unit(BASE_INSTRUMENTAL_SCORE * (.5 + .5 * pressure)
                          * (1 + .25 * exploration) / (1 + .25 * uncertainty))
        _same(proposal.get("prior_evidence"), prior, "affordance prior")

        if data["learned_value_status"] == "learned":
            if q.get("q") is None or proposal.get("learned_value_status") != "learned":
                raise ValueError("missing Q for native learned affordance")
            learned_value = _num(q["q"], "cold Q")
            _same(data.get("learned_value"), learned_value, "affordance Q")
            if kind == KINDS[1]:
                _same(proposal.get("learned_value"), learned_value,
                      "goal-linked proposal Q")
            evidence = _clamp(.25 * prior + .75 * tanh(learned_value / scale))
            has_q = True
        elif data["learned_value_status"] == "unlearned":
            if (q.get("q") is not None or data.get("learned_value") is not None
                    or proposal.get("learned_value_status") != "unlearned"
                    or (kind == KINDS[1] and proposal.get("learned_value") is not None)):
                raise ValueError("unlearned local affordance contains spurious Q")
            evidence = prior
            has_q = False
        else:
            raise ValueError("unknown local Q status")
        _same(data.get("evidence"), evidence, "native affordance evidence")
        if key in intrinsics:
            raise ValueError("nonintrinsic local option also has Stage11 record")
        covered.add(key)
        verification.append({
            "step":key[0], "cycle":key[1], "option":key[2],
            "path":"local" if kind == KINDS[0] else "goal_linked",
            "q_active_used":has_q,
            "expected_evidence":evidence,
        })

    # Non-Q input families remain distinct, never silently swallowed by a
    # successful local audit. Match every Stage11 intrinsic record to exactly
    # one native Stage8 evaluation and its published intrinsic value.
    matched_intrinsic = 0
    for key, (_, payload, index) in intrinsics.items():
        if key not in evaluations or index <= evaluations[key][2]:
            raise ValueError("Stage11 intrinsic event has no preceding Stage8")
        data = evaluations[key][1]
        if (data.get("intrinsic_status") != "applicable"
                or payload.get("status") != data.get("status")):
            raise ValueError("Stage11 intrinsic status differs from Stage8")
        a, b = payload.get("intrinsic_value"), data.get("intrinsic_value")
        if (a is None) != (b is None):
            raise ValueError("Stage11 intrinsic value presence differs")
        if a is not None:
            _same(a, b, "Stage11 intrinsic value")
        if (type(payload.get("intrinsic_producers")) is not list
                or type(payload.get("signal_ids")) is not list):
            raise ValueError("Stage11 intrinsic provenance not recorded")
        expected_weight = birth.get("stage11_intrinsic_weight")
        _same(payload.get("P15_intrinsic_weight"), expected_weight,
              "source-born P15 intrinsic weight")
        matched_intrinsic += 1
    if any(data.get("intrinsic_status") == "applicable" and key not in intrinsics
           for key, (_, data, _) in evaluations.items()):
        raise ValueError("missing Stage11 intrinsic evidence provenance")

    # A remaining non-Q Stage8 option must NOT be promoted to a proof.
    remaining = [
        {"step":k[0], "cycle":k[1], "option":k[2]}
        for k, (_, data, _) in evaluations.items()
        if k not in covered and (
            data.get("intrinsic_status") == "applicable"
            or (data.get("status") == "evaluated"
                and data.get("simulated_value_status") != "computed"
                and data.get("learned_value_status") == "unlearned"))
    ]
    return {
        "scope":"A2R_NATIVE_LOCAL_AFFORDANCE_ARITHMETIC_NOT_L3",
        "native_local_affordance_recomputed":len(verification),
        "local_with_learned_q":sum(row["q_active_used"] for row in verification),
        "stage11_intrinsic_provenance_matched_not_replayed":matched_intrinsic,
        "other_non_q_evaluations_not_replayed":len(remaining),
        "example_covered":verification[:6],
        "example_remaining":remaining[:6],
        "all_non_q_evaluations_recomputed":len(remaining) == 0,
        "independent_source_checkout_required":True,
        "preregistered_mechanism_exposed":False,
        "general_L3":"NOT_ESTABLISHED",
    }
