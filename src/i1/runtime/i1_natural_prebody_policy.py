"""Explicit, currently DORMANT I1-only DC-09 pre-action body policy.

Do not register for a natural birth without tested M11 replay compatibility
and a paid owner-side read. Historical Stage2/Stage7 policy versions remain
unchanged. Physical pre-action values enter Memory only through committed,
version-matched JournalViews projections, never through technical journals.
"""
from __future__ import annotations

from .journal_views import AutobiographicalPolicy
from .stage7_runtime import STAGE7_AUTOBIOGRAPHICAL_POLICY

LIVED_PREBODY_POLICY = AutobiographicalPolicy(
    version="i1-lived-body-before-v1",
    allowed_fields_by_kind={
        kind: (
            tuple(fields[:fields.index("body_after")])
            + ("body_before",)
            + tuple(fields[fields.index("body_after"):])
            if kind == "world_transition_experienced" else tuple(fields)
        )
        for kind, fields in
        STAGE7_AUTOBIOGRAPHICAL_POLICY.allowed_fields_by_kind.items()
    },
)
LIVED_PREBODY_POLICY.validate()

def captured_prebody_matches_transition(
    *, captured_body: object, physical_body_before: object,
) -> bool:
    """Fail closed when a physical pre-action state was not itself perceived.

    This pure gate authorizes no journal read and never changes a motor
    command. A scenario applied after admission may make the physical state
    differ from the pre-decision capture: that state must NOT be described
    as the body's earlier first-person perception.
    """
    from collections.abc import Mapping
    from math import isfinite

    keys = frozenset(("energy", "food", "water", "integrity"))
    if (not isinstance(captured_body, Mapping)
            or not isinstance(physical_body_before, Mapping)
            or set(captured_body) != keys
            or set(physical_body_before) != keys):
        return False
    for name in keys:
        a = captured_body[name]
        b = physical_body_before[name]
        if (type(a) not in (int, float) or type(b) not in (int, float)
                or not isfinite(a) or not isfinite(b)
                or not 0 <= a <= 100 or not 0 <= b <= 100
                or float(a) != float(b)):
            return False
    return True
