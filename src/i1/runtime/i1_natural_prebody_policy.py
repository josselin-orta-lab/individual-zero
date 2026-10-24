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
