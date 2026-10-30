"""Cold A2-R replay of physical geographic visits and offered frontier origins.

Read ONLY previously authenticated M11 journal occurrences, its SEALED final
Exploration owner, and an independently reconstructed zero-step birth.
Unlike an intrinsic motivation report, a physical position and the visit
counter can be checked against an independent final-state commitment.

LIMITS: Stage3 publishes passability only if an agency cue was enabled, and
does not publish per-neighbor creature presence. Canonical Action Control
safety/admissibility and the complete historical Exploration owner remain
UNPROVEN even when all checks succeed. No birth, action, mutation, GO or L3.
"""
from __future__ import annotations

from i1_a2r_m11_cold import HORIZON, numeric

_DIRECTIONS = {"north":(0,-1),"east":(1,0),"south":(0,1),"west":(-1,0)}
_FIELDS = ("x", "y")
_SOURCE_SCOPE = "SOURCE_RECONSTRUCTED_ZERO_STEP_REFERENCE_NOT_NEW_LIFE"


def _position(value):
    if (type(value) is not dict or set(value) != set(_FIELDS)
            or any(type(value[k]) is not int for k in _FIELDS)):
        raise ValueError("invalid signed physical Perception position")
    return value["x"], value["y"]


def _pair(value):
    if (type(value) is not list or len(value) != 2
            or any(type(k) is not int for k in value)):
        raise ValueError("invalid geographic M11 position")
    return tuple(value)


def _birth_state(birth):
    if (type(birth) is not dict or birth.get("scope") != _SOURCE_SCOPE
            or birth.get("q_at_birth_empty") is not True
            or type(birth.get("initial_exploration")) is not dict):
        raise ValueError("missing independently reconstructed zero-step Exploration")
    initial = birth["initial_exploration"]
    geography = initial.get("geography")
    if (initial.get("state_schema") != "exploration-activity-v3-geographic"
            or type(geography) is not dict
            or geography.get("visits") != []
            or geography.get("last_capture") is not None
            or type(geography.get("version")) is not str
            or not geography["version"]):
        raise ValueError("zero-step I1 already has a geographic visit history")
    return initial


def replay_geographic_history(events, *, final_exploration, birth, generation):
    """Replay visit evidence independent of final owner, then compare both.

    All event objects must come from inspect_m11 after the M11 SQLite ledger,
    journal chain and final owner hash have been verified. The source-born
    parameter reference itself is checked outside this function against the
    externally pinned Git checkout.
    """
    initial = _birth_state(birth)
    if (type(events) is not list or type(final_exploration) is not dict
            or type(generation) is not int or not 1 <= generation <= HORIZON
            or final_exploration.get("state_schema") != initial["state_schema"]
            or final_exploration.get("config_version") != initial.get("config_version")
            or numeric(final_exploration.get("coefficient"))
               != numeric(initial.get("coefficient"))
            or numeric(final_exploration.get("coefficient"))
               != numeric(birth.get("born_temperament",{}).get("exploration_coefficient"))):
        raise ValueError("sealed final Exploration differs from pinned birth")
    geo = final_exploration.get("geography")
    prior = initial["geography"]
    if (type(geo) is not dict
            or geo.get("schema") != prior.get("schema")
            or geo.get("version") != prior.get("version")
            or type(geo.get("visits")) is not list):
        raise ValueError("sealed geographic owner was substituted")
    max_sites = birth.get("stage11_geographic_max_distinct_sites")
    if type(max_sites) is not int or max_sites < 1:
        raise ValueError("missing pinned geographic visit capacity")

    visits = {}
    captures = {}
    direct_frontiers = []
    transit_proposals = 0
    passability_checked = 0
    cues_missing = 0
    current = None
    last_full_position = None
    pending = None
    visit_events = 0
    capacity_exhaustions = 0
    stage11_direct = set()

    def finish_pending():
        nonlocal pending
        if pending is not None and pending[1] != "none":
            raise ValueError("physical visit or capacity receipt missing from M11")
        pending = None

    for event in events:
        if type(event) is not dict:
            raise ValueError("malformed M11 geographic occurrence")
        kind = event.get("kind")
        if kind == "perceptual_capture":
            finish_pending()
            t, data = event.get("t_monde"), event.get("data")
            if (type(t) is not int or not 1 <= t <= generation
                    or t in captures or type(data) is not dict
                    or data.get("capture_t_monde") != t
                    or (current is not None and t <= current)):
                raise ValueError("nonchronological or repeated physical Perception")
            position = _position(data.get("position"))
            if any(not 0 <= v <= 31 for v in position):
                raise ValueError("Perception outside registered 32x32 world")
            if len(visits) >= max_sites and position not in visits:
                expected = "capacity"
            elif last_full_position is None or position != last_full_position:
                expected = "visit"
            else:
                expected = "none"
            captures[t] = data
            current = t
            pending = (t, expected, position)
            last_full_position = position
        elif kind in ("stage11_geographic_visit_observed",
                      "stage11_geographic_physical_capture_unregistered"):
            t, data = event.get("t_monde"), event.get("data")
            if (type(data) is not dict or type(t) is not int
                    or pending is None or pending[0] != t
                    or data.get("world_step") != t):
                raise ValueError("orphan geographic ledger event")
            expected = ("visit" if kind == "stage11_geographic_visit_observed"
                        else "capacity")
            if pending[1] != expected:
                raise ValueError("duplicate, missing or impossible geographic visit")
            if kind == "stage11_geographic_visit_observed":
                location = _pair(data.get("position"))
                if (data.get("source") != "perception_capture"
                        or location != pending[2]):
                    raise ValueError("geographic visit not from actual capture")
                visits[location] = visits.get(location,0) + 1
                if (type(data.get("new_distinct_sites")) is not int
                        or data["new_distinct_sites"] != len(visits)
                        or type(data.get("visit_count")) is not int
                        or data["visit_count"] != sum(visits.values())
                        or len(visits) > max_sites):
                    raise ValueError("M11 geographic visit counters diverge")
                visit_events += 1
            else:
                if (data.get("source") != "actual_perception_capture"
                        or _pair(data.get("physical_position")) != pending[2]
                        or data.get("new_registered_visit") is not False
                        or data.get("registered_distinct_sites") != len(visits)
                        or data.get("max_distinct_sites") != max_sites):
                    raise ValueError("false geographic capacity exhaustion")
                capacity_exhaustions += 1
            pending = (t, "none", pending[2])
        elif kind == "stage11_geographic_option_proposed":
            t, cycle, data = (event.get("t_monde"), event.get("cycle"),
                              event.get("data"))
            if (type(t) is not int or type(cycle) is not int or cycle < 1
                    or t not in captures or current != t or type(data) is not dict
                    or pending is None or pending[1] != "none"):
                raise ValueError("geographic option without current settled Perception")
            source = data.get("source")
            if source == "frozen_prior_observed_frontier_route":
                transit_proposals += 1
                continue
            if source != "single_perceptual_capture":
                raise ValueError("unknown geographic option producer")
            origin = _position(captures[t]["position"])
            target = _pair(data.get("destination"))
            direction = data.get("direction")
            if direction not in _DIRECTIONS:
                raise ValueError("geographic proposal has no canonical direction")
            dx, dy = _DIRECTIONS[direction]
            expected_ref = (f"frontier:{target[0]}:{target[1]}:"
                            f"from:{origin[0]}:{origin[1]}")
            option = data.get("option_ref")
            key = (t, cycle, option)
            if (key in stage11_direct
                    or target != (origin[0]+dx,origin[1]+dy)
                    or target in visits
                    or data.get("target_ref") != expected_ref
                    or option != "option:geographic:" + expected_ref
                    or data.get("goal_ref") is not None):
                raise ValueError("frontier not novel or not grounded in current position")
            stage11_direct.add(key)
            adjacency = captures[t].get("agency_visible_adjacent")
            if adjacency is None:
                cues_missing += 1
            else:
                if (captures[t].get("agency_capture_schema")
                        != "stage12-first-person-cue-v1"
                        or type(adjacency) is not list):
                    raise ValueError("unrecognized first-person adjacency schema")
                matches = [row for row in adjacency
                           if type(row) is dict and row.get("direction") == direction]
                if (len(matches) != 1 or matches[0].get("x") != target[0]
                        or matches[0].get("y") != target[1]
                        or matches[0].get("passable") is not True):
                    raise ValueError("frontier lacks independently observed passability")
                passability_checked += 1
            direct_frontiers.append({
                "step":t, "cycle":cycle, "option":option,
                "not_previously_registered":True,
                "perceptual_passability_checked":adjacency is not None,
            })
    finish_pending()
    if not captures:
        raise ValueError("no physical Perception in original M11")
    recorded = geo["visits"]
    if any(type(row) is not list or len(row) != 3
           or any(type(v) is not int for v in row)
           or row[2] < 1 for row in recorded):
        raise ValueError("malformed final signed geographic ledger")
    expected = [[x,y,c] for (x,y),c in sorted(visits.items())]
    if recorded != expected:
        raise ValueError("sealed final Exploration visits differ from journal replay")
    last_capture = geo.get("last_capture")
    if (capacity_exhaustions == 0 and last_capture is not None
            and (type(last_capture) is not list or len(last_capture) != 3
                 or last_capture[0] != current
                 or tuple(last_capture[1:]) != last_full_position)):
        raise ValueError("final geographic last capture differs from physical journal")

    return {
        "scope":"A2R_PHYSICAL_GEOGRAPHIC_VISIT_REPLAY_NOT_L3",
        "perceptual_captures":len(captures),
        "physical_visit_receipts_recomputed":visit_events,
        "distinct_sites_verified_against_sealed_owner":len(visits),
        "capacity_events_attested":capacity_exhaustions,
        "direct_frontier_candidates_checked":len(direct_frontiers),
        "direct_frontier_passability_cues_checked":passability_checked,
        "direct_frontier_passability_cues_absent":cues_missing,
        "transit_proposals_not_replayed":transit_proposals,
        "frontier_occurrences":direct_frontiers,
        "historic_visits_match_sealed_final_owner":True,
        "per_neighbor_creature_absence_attested":False,
        "action_control_admissibility_replayed":False,
        "all_intrinsic_owner_history_replayed":False,
        "preregistered_mechanism_exposed":False,
        "study_admissible":False,
        "general_L3":"NOT_ESTABLISHED",
    }
