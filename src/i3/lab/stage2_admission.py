"""Stage-2.1 exact-transport admission guard (ADR-0019, fail closed).

Before an explicit owner ADR-0017 lift, only the `engineering` cohort is
admitted. Development, selection, validation and reserve raise before any
World is constructed. A lift is recognised only as one exact line in the
STATUS ledger naming this transport's fingerprint:

    ADR-0017 OWNER LIFT: Stage-2.1 transport <64 hex fingerprint>

The fingerprint covers every file of the exact transport: cognition and
runtime (`src/i3/modules`, `src/i3/runtime`), the G/R pipeline, the panel
runner, this guard, the cohort and ecology generators and the frozen plan.
Any change to any of them yields a new fingerprint, which invalidates an
earlier rehearsal PASS and any lift line naming the old fingerprint.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path

from . import engineering_cohort as ENG
from . import p2_ecologies as P2
from ..runtime import admission as RA

I3 = Path(__file__).resolve().parents[1]
LAB_TRANSPORT_FILES = ("two_phase_panel.py", "engineering_cohort.py", "p2_ecologies.py",
                       "stage2_admission.py", "stage2_panel.py")
LIFT_PREFIX = "ADR-0017 OWNER LIFT: Stage-2.1 transport "


def transport_files(plan_path) -> list:
    files = sorted((I3 / "modules").glob("*.py")) + sorted((I3 / "runtime").glob("*.py"))
    files += [I3 / "lab" / name for name in LAB_TRANSPORT_FILES]
    files.append(Path(plan_path).resolve())
    return files


def transport_fingerprint(plan_path) -> str:
    lines = []
    for path in transport_files(plan_path):
        rel = path.relative_to(I3.parents[1]).as_posix() if I3.parents[1] in path.parents else path.name
        lines.append(f"{rel}:{sha256(path.read_bytes()).hexdigest()}\n")
    return sha256("".join(lines).encode()).hexdigest()


def owner_lift_recorded(status_text: str, fingerprint: str) -> bool:
    return any(line.strip() == LIFT_PREFIX + fingerprint for line in status_text.splitlines())


def admit(cohort: str, family: str, index: int, plan_path, *, lift_status_path=None):
    """Return (ticket, spec) or raise. Scientific cohorts fail closed pre-lift."""
    if cohort not in RA.COHORTS:
        raise ValueError("unknown cohort")
    fingerprint = transport_fingerprint(plan_path)
    if cohort == "engineering":
        spec = ENG.engineering_world(family, index)
        seed = ENG.ENGINEERING[index]
    else:
        text = Path(lift_status_path).read_text() if lift_status_path else ""
        if not owner_lift_recorded(text, fingerprint):
            raise PermissionError(
                "ADR-0017 active: scientific cohort fails closed (no owner lift for this transport)")
        seed = P2.COHORTS[cohort][index]
        ENG.assert_not_engineering(seed)
        spec = P2.world_for(family, cohort, index)
    ticket = RA.mint(cohort=cohort, family=family, index=index, world_seed=seed,
                     world_name=spec.name, transport_fingerprint=fingerprint)
    return ticket, spec
