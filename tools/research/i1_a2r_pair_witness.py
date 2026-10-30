"""A2-R independent paired TD -> Q -> Competition -> motor witness.

No I1 imports at module load, no simulation, no births and no intervention.
Evidence is taken only from the two native, cold-verified per-life replays
and their M11 occurrences. A visible linked sequence is a *mechanistic
candidate*, NOT a controlled demonstration that Q alone caused the action.
Missing independent birth/source provenance means mechanism_exposed=False.
"""
from __future__ import annotations

from i1_a2r_m11_cold import numeric, physical_steps, reward

TOL = 2e-9
MODES = ("CANONICAL_ABS", "RESEARCH_DEFICIT")
SCOPE = "A2R_COLD_NATIVE_Q_FULL_VECTOR_NOT_L3"
BASELINE = (
    "simulated_value_status", "simulated_value", "intrinsic_status",
    "intrinsic_value", "risk_status", "risk", "safety_uncertainty",
    "protection",
)


def _different(a, b):
    a, b = numeric(a), numeric(b)
    return abs(a - b) > TOL * max(1.0, abs(a), abs(b))


def _check_replay(row, mode):
    if (type(row) is not dict or row.get("scope") != SCOPE
            or row.get("mode") != mode
            or row.get("full_q_replay_verified") is not True
            or row.get("birth_source_provenance_verified") is not False
            or row.get("adaptive_learning_go") != "NOT_ESTABLISHED"
            or type(row.get("m11_identity")) is not str
            or type(row.get("m11_journal_head")) is not str
            or len(row["m11_journal_head"]) != 64
            or type(row.get("generation")) is not int
            or row.get("status") not in ("active", "dead")
            or type(row.get("td_recurrences")) is not list
            or type(row.get("stage8_observations")) is not list
            or type(row.get("decisions")) is not list):
        raise ValueError("A2-R pair requires two fully cold-verified native Q replays")


def _step_proofs(events):
    """Unique native Stage8, Competition and admitted decision per key."""
    stage8, competition, admitted = {}, {}, {}
    for event in events:
        kind = event.get("kind")
        t, c, data = event.get("t_monde"), event.get("cycle"), event.get("data")
        if kind not in ("stage8_option_evaluation", "competition_cycle",
                        "command_admitted"):
            continue
        if (type(t) is not int or type(data) is not dict
                or (kind != "command_admitted" and type(c) is not int)):
            raise ValueError("invalid paired M11 evidence chronology")
        if kind == "stage8_option_evaluation":
            option = data.get("option_ref")
            key = (t, c, option)
            if type(option) is not str or key in stage8:
                raise ValueError("duplicate paired Stage8 evidence")
            stage8[key] = data
        elif kind == "competition_cycle":
            key = (t, c)
            if key in competition or type(data.get("traces")) is not list:
                raise ValueError("duplicate paired Competition")
            by_option = {}
            for trace in data["traces"]:
                if type(trace) is not dict or type(trace.get("option_ref")) is not str:
                    raise ValueError("malformed paired Competition trace")
                option = trace["option_ref"]
                if option in by_option or (t, c, option) not in stage8:
                    raise ValueError("paired Competition cannot be joined to Stage8")
                observed = stage8[(t, c, option)].get("evidence")
                observed_trace = trace.get("evidence")
                if (observed is None) != (observed_trace is None):
                    raise ValueError("Stage8 evidence disappeared at Competition")
                if observed is not None and _different(observed, observed_trace):
                    raise ValueError("Stage8 evidence changed before Competition")
                by_option[option] = trace
            expected = {o for tt, cc, o in stage8 if (tt, cc) == key}
            if set(by_option) != expected:
                raise ValueError("paired Competition omitted Stage8 options")
            competition[key] = by_option
        elif data.get("source") == "decision":
            key = t
            if key in admitted or type(data.get("option_ref")) is not str:
                raise ValueError("duplicate paired decision admission")
            matches = sorted((cy, option) for (tt, cy, option) in stage8
                             if tt == t and option == data["option_ref"]
                             and (t, cy) in competition)
            if not matches:
                raise ValueError("motor admission has no M11 Stage8/Competition cycle")
            admitted[key] = matches[-1]
    return stage8, competition, admitted


def _same_baseline(a, b):
    """Conservative guard against a non-Q Stage8 input changing."""
    for key in BASELINE:
        va, vb = a.get(key), b.get(key)
        if (type(va) is dict and set(va) == {"$f64"}) or (
                type(vb) is dict and set(vb) == {"$f64"}):
            try:
                if _different(va, vb):
                    return False
            except ValueError:
                return False
        elif type(va) in (int, float) and type(vb) in (int, float):
            if _different(va, vb):
                return False
        elif va != vb:
            return False
    return True


def compare_pair(*, canonical, candidate, canonical_events, candidate_events,
                 setpoints, weights):
    """Produce one fail-closed, DESCRIPTIVE pair witness, never a GO flag.

    Inputs must originate from cold_replay_m11 + inspect_m11 on the same
    signed SQLite head. This function refuses to count a reward difference
    unless it is followed by a published TD difference, a changed Q *read*
    in the same first-person state, a changed Competition evidence and a
    different applied motor command. Proof of independent birth/source
    parameters and exclusion of other policy mediators remain separate.
    """
    _check_replay(canonical, MODES[0])
    _check_replay(candidate, MODES[1])
    if (canonical["m11_identity"] == candidate["m11_identity"]
            or type(canonical_events) is not list or type(candidate_events) is not list):
        raise ValueError("A2-R paired lives must be independent and journalled")

    arms = ((canonical, canonical_events), (candidate, candidate_events))
    phys = [physical_steps(events, generation=row["generation"],
                           status=row["status"]) for row, events in arms]
    a, b = phys
    if a[0]["before"] != b[0]["before"]:
        raise ValueError("A2-R birth physical body differs")
    # Each replay already authenticates its own born reward policy and TD.
    first_reward, first_motor, first_physical = None, None, None
    for i in range(min(len(a), len(b))):
        x, y = a[i], b[i]
        same_command = (x["action"], x["parameters"]) == (
            y["action"], y["parameters"])
        same_physics = (x["before"], x["after"], x["status"]) == (
            y["before"], y["after"], y["status"])
        if not (same_command and same_physics):
            if first_reward is None:
                raise ValueError("pre-reward physical divergence: no valid causal pairing")
            first_physical = i + 1
            if not same_command:
                first_motor = i + 1
            break
        canonical_r = reward(x["before"], x["after"],
                             setpoints=setpoints, weights=weights, mode=MODES[0])
        research_r = reward(y["before"], y["after"],
                            setpoints=setpoints, weights=weights, mode=MODES[1])
        if first_reward is None and _different(canonical_r, research_r):
            first_reward = i + 1
    if first_physical is None and len(a) != len(b):
        if first_reward is None:
            raise ValueError("inter-arm mortality diverged before reward intervention")
        first_physical = min(len(a), len(b)) + 1

    c_td = {x["step"]: x for x in canonical["td_recurrences"]}
    d_td = {x["step"]: x for x in candidate["td_recurrences"]}
    def matched_td(t):
        x, y = c_td[t], d_td[t]
        return all(x.get(k) == y.get(k) for k in (
            "step", "segment_start", "length",
            "previous_signature", "next_signature"))

    first_td = None
    if first_reward is not None:
        cap = first_physical if first_physical is not None else min(len(a),len(b)) + 1
        for t in sorted(set(c_td) & set(d_td)):
            if first_reward < t < cap and matched_td(t) and (
                    _different(c_td[t]["return_g"], d_td[t]["return_g"])):
                first_td = t
                break

    stage8 = [_step_proofs(events) for _, events in arms]
    qa = {(x["step"],x["cycle"],x["option"]):x
          for x in canonical["stage8_observations"]}
    qb = {(x["step"],x["cycle"],x["option"]):x
          for x in candidate["stage8_observations"]}
    ca, cb = stage8[0][1], stage8[1][1]
    paired_q = paired_competition = None
    first_non_q_confound = None
    if first_td is not None:
        max_step = (first_physical if first_physical is not None
                    else min(len(a),len(b)))
        for t,c,option in sorted(set(qa) & set(qb)):
            if t <= first_td or t > max_step:
                continue
            x, y = qa[t,c,option], qb[t,c,option]
            if (x["status"] != "learned" or y["status"] != "learned"
                    or x["signature"] != y["signature"]
                    or x["q"] is None or y["q"] is None
                    or not _different(x["q"], y["q"])):
                continue
            if paired_q is None:
                paired_q = {"step":t,"cycle":c,"option":option,
                            "signature":x["signature"],
                            "canonical_q":numeric(x["q"]),
                            "candidate_q":numeric(y["q"])}
            key = (t,c,option)
            pa,pb = stage8[0][0].get(key),stage8[1][0].get(key)
            ta,tb = ca.get((t,c),{}).get(option),cb.get((t,c),{}).get(option)
            if not (pa and pb and ta and tb):
                continue
            options_a = set(ca[(t,c)])
            options_b = set(cb[(t,c)])
            if options_a != options_b or not all(
                _same_baseline(stage8[0][0][(t,c,o)],
                               stage8[1][0][(t,c,o)])
                for o in options_a
            ):
                if first_non_q_confound is None:
                    first_non_q_confound = t
                continue
            ea,eb=pa.get("evidence"),pb.get("evidence")
            if ea is None or eb is None or not _different(ea,eb):
                continue
            if paired_competition is None:
                paired_competition = {
                    "step":t,"cycle":c,"option":option,
                    "canonical_evidence":numeric(ea),
                    "candidate_evidence":numeric(eb),
                    "crossed_canonical":ta.get("crossed"),
                    "crossed_candidate":tb.get("crossed"),
                    "same_non_q_stage8_inputs":True,
                }

    motor_witness = None
    if first_motor is not None and paired_competition is not None and (
            paired_competition["step"] == first_motor):
        t = first_motor
        da, db = stage8[0][2].get(t), stage8[1][2].get(t)
        if (da and db and da != db
                and da[0] == db[0] == paired_competition["cycle"]
                and da[1] in ca.get((t,da[0]),{})
                and db[1] in cb.get((t,db[0]),{})):
            motor_witness = {
                "step":t,
                "canonical_option":da[1],
                "candidate_option":db[1],
                "canonical_command":a[t-1]["action"],
                "candidate_command":b[t-1]["action"],
                "motor_physics_diverged":True,
            }
    if first_reward is None:
        grade="NO_REWARD_DIFFERENCE"
    elif first_td is None:
        grade="REWARD_DIFFERENCE_WITHOUT_PUBLISHED_TD"
    elif paired_q is None:
        grade="PUBLISHED_TD_DIFFERENCE_WITHOUT_CHANGED_Q_READ"
    elif paired_competition is None:
        grade="CHANGED_Q_READ_WITHOUT_COMPARABLE_COMPETITION"
    elif motor_witness is None:
        grade="COMPETITION_DIFFERENCE_WITHOUT_LINKED_MOTOR_SWITCH"
    else:
        grade="CANDIDATE_MEDIATION_PATH_OBSERVED_PENDING_SOURCE_ATTESTATION"
    if first_physical is not None and first_motor is None:
        grade="PHYSICAL_DIVERGENCE_WITHOUT_MOTOR_SWITCH"
    return {
        "schema":"i1-a2r-pair-mechanism-witness/1",
        "scope":"COLD_PAIRED_L1_DIAGNOSTIC_NOT_L3",
        "canonical_m11_head":canonical["m11_journal_head"],
        "candidate_m11_head":candidate["m11_journal_head"],
        "first_physical_reward_difference_step":first_reward,
        "first_published_td_return_difference_step":first_td,
        "first_changed_q_read":paired_q,
        "first_changed_competition_evidence":paired_competition,
        "first_motor_divergence_step":first_motor,
        "first_physical_divergence_step":first_physical,
        "first_non_q_competition_confound_step":first_non_q_confound,
        "motor_witness":motor_witness,
        "evidence_grade":grade,
        "descriptive_candidate_path_observed":motor_witness is not None,
        "independent_birth_provenance_verified":False,
        "preregistered_mechanism_exposed":False,
        "general_L3":"NOT_ESTABLISHED",
        "historical_A1C":"NO_GO",
    }


def cold_compare_pair(*, canonical_path, candidate_path, canonical_id,
                      candidate_id, setpoints, weights, born_td, world_clock,
                      allow_incomplete=False):
    """Audit original read-only SQLite in BOTH arms; never launch a life."""
    from i1_a2r_m11_cold import inspect_m11
    from i1_a2r_q_replay import cold_replay_m11
    c = cold_replay_m11(path=canonical_path,identity=canonical_id,
                        mode=MODES[0],setpoints=setpoints,weights=weights,
                        born_td=born_td,world_clock=world_clock,
                        allow_incomplete=allow_incomplete)
    d = cold_replay_m11(path=candidate_path,identity=candidate_id,
                        mode=MODES[1],setpoints=setpoints,weights=weights,
                        born_td=born_td,world_clock=world_clock,
                        allow_incomplete=allow_incomplete)
    a = inspect_m11(path=canonical_path,identity=canonical_id,
                    mode=MODES[0],allow_incomplete=allow_incomplete)
    b = inspect_m11(path=candidate_path,identity=candidate_id,
                    mode=MODES[1],allow_incomplete=allow_incomplete)
    if (a["receipt"]["journal_head"] != c["m11_journal_head"]
            or b["receipt"]["journal_head"] != d["m11_journal_head"]
            or a["receipt"]["state_hash"] != c["m11_state_hash"]
            or b["receipt"]["state_hash"] != d["m11_state_hash"]):
        raise ValueError("M11 changed while validating reward paired lives")
    result = compare_pair(canonical=c,candidate=d,
                          canonical_events=a["events"],candidate_events=b["events"],
                          setpoints=setpoints,weights=weights)
    return {**result,
            "study_admissible":bool(c["study_admissible"] and d["study_admissible"]),
            "technical_incomplete":allow_incomplete}
