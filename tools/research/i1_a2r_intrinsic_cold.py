"""Cold Stage11 intrinsic diagnostic using original M11 and a source-born reference.

NO individual births, state mutations, causal GO or study admission. For a
DIRECT geographic frontier only, calculate the intrinsic *magnitude* from
the independently reconstructed temperament and geographic novelty config.
Then independently recompute the Stage8 extrinsic blend and the Stage11
evidence addition using the signed M11 Q/simulation observations.

This does NOT independently prove that the reported frontier was physically
admissible, nor reconstruct Exploration questions, route-history lengths,
place-memory confidence or lived-site context. Those remain quarantined.
"""
from __future__ import annotations

from math import tanh

from i1_a2r_m11_cold import numeric
from i1_a2r_stage8_evidence import _calibration

_SCOPE = "A2R_COLD_NATIVE_Q_FULL_VECTOR_NOT_L3"
_TOL = 2e-9
_DIRECT = frozenset(("exploration:p48_geographic",
                     "exploration:p48_instrumental"))


def _number(value):
    return numeric(value)


def _same(left, right, label):
    a, b = _number(left), _number(right)
    if abs(a - b) > _TOL * max(1.0, abs(a), abs(b)):
        raise ValueError("Stage11 " + label + " differs from source formula")


def _clip(value):
    return min(1., max(-1., value))


def _occurrence(event):
    if type(event) is not dict or type(event.get("data")) is not dict:
        raise ValueError("malformed authenticated Stage11 M11 occurrence")
    data = event["data"]
    step, cycle, option = (event.get("t_monde"), event.get("cycle"),
                           data.get("option_ref"))
    if (type(step) is not int or step < 1 or type(cycle) is not int or cycle < 1
            or type(option) is not str or not option):
        raise ValueError("invalid native Stage11 occurrence identity")
    return (step, cycle, option)


def _extrinsic(stage8, count, calibration):
    """Recalculate original Stage8 pre-intrinsic term, without reading evidence."""
    p = _calibration(calibration)
    if type(count) is not int or count < 0:
        raise ValueError("invalid native TD count")
    has_q = stage8.get("learned_value_status") == "learned"
    if not has_q and stage8.get("learned_value_status") != "unlearned":
        raise ValueError("unknown Stage8 Q status")
    if has_q != (count > 0):
        raise ValueError("learned Q status inconsistent with authenticated history")
    q = _number(stage8.get("learned_value")) if has_q else None
    if not has_q and stage8.get("learned_value") is not None:
        raise ValueError("native unlearned Q unexpectedly has a value")
    sim_status = stage8.get("simulated_value_status")
    if sim_status not in ("computed", "unavailable"):
        raise ValueError("unknown Stage8 simulation status")
    sim = (_number(stage8.get("simulated_value"))
           if sim_status == "computed" else None)
    if sim is None and stage8.get("simulated_value") is not None:
        raise ValueError("native unavailable simulation has a value")
    if q is None and sim is None:
        return 0., False
    if q is not None and sim is not None:
        w = count / (count + p["n0"])
        x = w * q + (1 - w) * sim
    else:
        x = q if q is not None else sim
    return _clip(p["extrinsic_gain"] * tanh(x / p["evidence_scale"])), sim is not None


def audit_stage11_intrinsic_magnitude(events, *, q_replay, stage8_audit, birth):
    """Recompute direct-frontier intrinsic magnitudes, retain other gaps.

    Inputs MUST already have gone through M11 cold verification and 12-feature
    TD/Q replay. Stage11's own published intrinsic value is NEVER considered
    independent evidence of how Exploration derived it.
    """
    if (type(events) is not list or type(q_replay) is not dict
            or type(stage8_audit) is not dict or type(birth) is not dict
            or q_replay.get("scope") != _SCOPE
            or q_replay.get("full_q_replay_verified") is not True
            or stage8_audit.get("scope") !=
               "A2R_STAGE8_NATIVE_EVIDENCE_RECONSTRUCTED_NOT_L3"
            or stage8_audit.get("same_full_m11_q_replay") is not True
            or stage8_audit.get("preregistered_mechanism_exposed") is not False
            or birth.get("scope") !=
               "SOURCE_RECONSTRUCTED_ZERO_STEP_REFERENCE_NOT_NEW_LIFE"
            or birth.get("q_at_birth_empty") is not True
            or birth.get("identity") != q_replay.get("m11_identity")
            or birth.get("mode") != q_replay.get("mode")):
        raise ValueError("Stage11 diagnostic needs authentic Q replay and pinned birth")
    p = _calibration(birth.get("stage8_evaluation"))
    weight = _number(birth.get("stage11_intrinsic_weight"))
    if weight < 0:
        raise ValueError("invalid source-born intrinsic weight")
    temperament = birth.get("born_temperament")
    if type(temperament) is not dict:
        raise ValueError("missing source-born temperament")
    coefficient = _number(temperament.get("exploration_coefficient"))
    novelty = birth.get("stage11_geographic_novelty_weight")
    if novelty is not None:
        novelty = _number(novelty)
    if not -1 <= coefficient <= 1 or (novelty is not None
                                    and not 0 <= novelty <= 1):
        raise ValueError("invalid source-born intrinsic geographical config")

    recurrences = q_replay.get("td_recurrences")
    if type(recurrences) is not list or type(q_replay.get("q_update_counts")) is not dict:
        raise ValueError("missing cold TD recurrence chronology")
    published_td = {}
    for item in recurrences:
        if (type(item) is not dict or type(item.get("step")) is not int
                or type(item.get("signatures_updated")) not in (list, tuple)
                or item["step"] in published_td):
            raise ValueError("invalid cold TD recurrence")
        published_td[item["step"]] = list(item["signatures_updated"])

    stage8, stage11, td_counts = {}, {}, {}
    events_seen, watched_td = [], set()
    for position, event in enumerate(events):
        if type(event) is not dict:
            raise ValueError("malformed native journal event")
        kind = event.get("kind")
        if kind == "td_update_published":
            step = event.get("t_monde")
            if step not in published_td or step in watched_td:
                raise ValueError("unmatched or repeated native TD update")
            watched_td.add(step)
            signatures = event.get("data", {}).get("updated_signatures")
            if signatures != published_td[step] or len(signatures) != len(set(signatures)):
                raise ValueError("TD signature chronology differs from cold replay")
            for signature in signatures:
                td_counts[signature] = td_counts.get(signature, 0) + 1
        elif kind in ("stage8_option_evaluation", "stage11_intrinsic_evaluation"):
            key = _occurrence(event)
            target = stage8 if kind == "stage8_option_evaluation" else stage11
            if key in target:
                raise ValueError("duplicate native evaluation")
            target[key] = (event["data"], position, dict(td_counts))
            events_seen.append(key)

    if watched_td != set(published_td) or td_counts != q_replay["q_update_counts"]:
        raise ValueError("incomplete cold TD history in Stage11 audit")
    if set(stage11) - set(stage8):
        raise ValueError("orphan native Stage11 intrinsic occurrence")

    verified, unavailable = [], []
    for key, (provenance, position, _) in stage11.items():
        raw, earlier, before_counts = stage8[key]
        if earlier >= position:
            raise ValueError("Stage11 publication precedes original Stage8")
        if (provenance.get("status") != raw.get("status")
                or raw.get("intrinsic_status") != "applicable"
                or type(provenance.get("intrinsic_producers")) is not list
                or type(provenance.get("signal_ids")) is not list
                or len(provenance["signal_ids"]) !=
                   len(set(provenance["signal_ids"]))):
            raise ValueError("inconsistent native Stage11 provenance")
        if provenance.get("intrinsic_value") is None:
            if raw.get("intrinsic_value") is not None:
                raise ValueError("native Stage11 missing value differs from Stage8")
            unavailable.append({"step":key[0], "cycle":key[1], "option":key[2],
                                "reason":"no_intrinsic_value_or_unscored"})
            continue
        reported = _number(provenance["intrinsic_value"])
        _same(raw.get("intrinsic_value"), reported, "duplicate published intrinsic")
        _same(provenance.get("P15_intrinsic_weight"), weight, "born P15 weight")
        if not 0 <= reported <= 1:
            raise ValueError("Stage11 intrinsic value outside physical motivation bounds")

        producers = provenance["intrinsic_producers"]
        signals = provenance["signal_ids"]
        direct = [producer for producer in producers if producer in _DIRECT]
        frontier_signal = [signal for signal in signals
                           if type(signal) is str
                           and signal.startswith("exploration:frontier:")
                           and signal.endswith(":t" + str(key[0]))]
        if (novelty is not None and len(direct) == 1
                and len(frontier_signal) == 1
                and not any(type(s) is str and
                            s.startswith("exploration:remote-frontier:")
                            for s in signals)
                and not any("lived_site_context" in str(z) for z in producers)):
            expected_intrinsic = min(1., max(0., (1 + coefficient) * novelty))
            if expected_intrinsic <= 0:
                raise ValueError("nonpositive source-born geographic motivation")
            _same(reported, expected_intrinsic, "direct frontier motivation")
            sig = raw.get("learning_signature")
            if type(sig) is not str or not sig:
                raise ValueError("missing native Stage8 Q learning signature")
            count = before_counts.get(sig, 0)
            ext, has_sim = _extrinsic(raw, count, birth["stage8_evaluation"])
            if direct[0] == "exploration:p48_instrumental":
                if (not has_sim or _number(raw.get("simulated_value")) <= 0):
                    raise ValueError("instrumental geographic augmentation without positive simulation")
            expected = _clip(ext + weight * expected_intrinsic)
            _same(raw.get("evidence"), expected, "direct frontier score")
            verified.append({"step":key[0], "cycle":key[1], "option":key[2],
                             "recomputed_intrinsic":expected_intrinsic,
                             "recomputed_evidence":expected,
                             "producer":direct[0]})
        else:
            if "exploration:entity_place_recall" in producers:
                if reported > min(.12, weight * .12) + _TOL:
                    raise ValueError("place confidence motivation exceeds source bound")
                reason = "place_memory_confidence_and_lived_site_history"
            elif "exploration:p48" in producers:
                reason = "causal_question_visits_progress_and_proof_history"
            elif any(isinstance(s, str) and
                     s.startswith("exploration:remote-frontier:") for s in signals):
                reason = "frontier_route_path_and_prior_visit_history"
            else:
                reason = "unreplayed_intrinsic_owner_state_or_site_context"
            unavailable.append({"step":key[0], "cycle":key[1], "option":key[2],
                                "reason":reason})
    return {
        "scope":"A2R_STAGE11_PARTIAL_SOURCE_INTRINSIC_ARITHMETIC_NOT_L3",
        "stage11_intrinsic_occurrences":len(stage11),
        "direct_frontier_intrinsic_recomputed":len(verified),
        "unreconstructed_owner_intrinsic_occurrences":len(unavailable),
        "intrinsic_magnitude_verified":verified,
        "missing_owner_state_examples":unavailable[:12],
        "unreconstructed_owner_intrinsic":unavailable,
        "all_stage11_intrinsic_state_independently_replayed":False,
        "frontier_admissibility_independently_replayed":False,
        "study_admissible":False,
        "preregistered_mechanism_exposed":False,
        "general_L3":"NOT_ESTABLISHED",
    }
