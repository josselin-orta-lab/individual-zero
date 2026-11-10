"""Stage-2.1 historical transport: ENGINEERING ONLY, science permanently closed.

The original ADR-0017 owner lift was valid for the single frozen DEVELOPMENT
80/81 exposure at source 5d362e22, now completed and exhausted without retry.
Its source-locked historical receipts remain readable but are NOT reusable
permission. The legacy runner and this old admission path no longer admit any
scientific cohort, even if a STATUS ledger line records a past lift.

A future selected Stage-2.1 study needs its OWN prospective index-scoped
source lock, irreversible claim, rehearsal and separate owner authorization.
The fingerprint still covers all cognition/runtime, transport and plan files.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path

from . import engineering_cohort as ENG
from . import p2_ecologies as P2
from ..runtime import admission as RA

I3 = Path(__file__).resolve().parents[1]
CANONICAL_STATUS_PATH = I3 / "docs" / "STATUS.md"
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


def canonical_owner_lift_recorded(fingerprint: str) -> bool:
    """Only the version-controlled I3 STATUS ledger can authorize scientific Worlds."""
    return owner_lift_recorded(CANONICAL_STATUS_PATH.read_text(), fingerprint)


def admit(cohort: str, family: str, index: int, plan_path):
    """Return (ticket, spec) or raise. Scientific cohorts fail closed pre-lift."""
    if cohort not in RA.COHORTS:
        raise ValueError("unknown cohort")
    fingerprint = transport_fingerprint(plan_path)
    if cohort == "engineering":
        spec = ENG.engineering_world(family, index)
        seed = ENG.ENGINEERING[index]
    else:
        # The only past owner lift was single-use and exhausted by 80/81.
        # This legacy transport is NOT selected-study authorization, even if
        # the historical source-valid lift is present in STATUS.md.
        raise PermissionError(
            "Stage-2.1 legacy pilot closed: 80/81 consumed, no new scientific scope authorized")
    ticket = RA.mint(cohort=cohort, family=family, index=index, world_seed=seed,
                     spec=spec, transport_fingerprint=fingerprint)
    return ticket, spec


def admit_b1_newworld_engineering(*, family: str, index: int, world_seed: int,
                                  spec, transport_fingerprint: str):
    """Only guard-minted ticket for fixed PUBLIC B1 new-world ENGINEERING.

    This is distinct from the consumed 80/81 scientific transport. It
    allows exactly 96 preselected synthetic public-root unit identifiers,
    requires an exact F0 physical WorldSpec and current source fingerprint,
    and NEVER admits a B1 scientific, reserve, validation or selection life.
    """
    from . import stage2_survival_b1_sampling as SAMPLE
    from . import stage2_survival_b1_worldspec_audit as SPECS
    from . import stage2_survival_b1_engineering as B1
    if type(index) is not int or not 0 <= index < B1.PAIRS:
        raise PermissionError("outside the first 96 B1 public engineering units")
    if type(world_seed) is not int or family not in SAMPLE.FAMILIES:
        raise PermissionError("foreign B1 engineering world seed/family")
    expected = SAMPLE.preview(SAMPLE.PREVIEW_WITNESS)["proposed_units"][index]
    if (expected["ordinal"] != index or expected["family"] != family or
            expected["world_seed"] != world_seed):
        raise PermissionError("B1 engineering world not in public fixed allocation")
    if (type(transport_fingerprint) is not str or
            transport_fingerprint != B1.source_fingerprint()):
        raise PermissionError("B1 engineering source fingerprint mismatch")
    # A spoofed spec is rejected even if its name and world seed look right.
    if not isinstance(spec, RA.WorldSpec):
        raise PermissionError("B1 engineering WorldSpec is absent or invalid")
    known_spec = SPECS._construct_f0_spec(family, world_seed)
    if RA.world_sha256(spec) != RA.world_sha256(known_spec):
        raise PermissionError("B1 engineering WorldSpec digest does not match source")
    return RA.mint(cohort="engineering", family=family, index=index,
                   world_seed=world_seed, spec=spec,
                   transport_fingerprint=transport_fingerprint)


def admit_b1_newworld_development(*, case: dict, spec,
                                  transport_fingerprint: str):
    """New B1 DEVELOPMENT-only ticket; never old 80/81 or selection/reserve.

    The exact new prospective allocation and executable source are checked
    before minting; a ticket is not a replacement for independent scientific
    design review, external provenance or a global one-shot source claim.
    """
    from . import stage2_b1_development as B1
    from . import stage2_survival_b1_worldspec_audit as SPECS
    if not isinstance(case, dict):
        raise PermissionError("B1 new-development allocation requires an exact case")
    B1.match_case(case, transport_fingerprint)
    if case["cohort"] != "development":
        raise PermissionError("only new B1 DEVELOPMENT is admissible")
    if not isinstance(spec, RA.WorldSpec):
        raise PermissionError("B1 new-development source requires WorldSpec")
    expected = SPECS._construct_f0_spec(case["family"], case["world_seed"])
    if RA.world_sha256(spec) != RA.world_sha256(expected):
        raise PermissionError("B1 DEVELOPMENT must use the exact generated WorldSpec")
    return RA.mint(
        cohort="development", family=case["family"], index=case["index"],
        world_seed=case["world_seed"], spec=spec,
        transport_fingerprint=transport_fingerprint,
    )


def admit_three_arm_newworld_engineering(*, case: dict, spec,
                                          transport_fingerprint: str):
    """Central guard for new public-synthetic three-arm engineering ONLY.

    This ticket may fund FIXED/GATE/RANDOM technical lives, never scientific
    selection, validation, reserve, retired development, or a new B1 owner lift.
    """
    from . import stage2_survival_b1_sampling as SAMPLE
    from . import stage2_survival_b1_worldspec_audit as SPECS
    from . import stage2_three_arm_engineering as THREE
    from . import stage2_survival_b1_engineering as B1
    if type(case) is not dict or type(case.get("index")) is not int:
        raise PermissionError("three-arm engineering requires exact immutable case")
    if case.get("cohort") != "engineering":
        raise PermissionError("three-arm scientific and reserve cohorts closed")
    offset = case["index"] - THREE.START
    if not 0 <= offset < THREE.PAIRS or case.get("policy") not in THREE.ARMS:
        raise PermissionError("outside new three-arm PUBLIC engineering allocation")
    if case != THREE.cases()[3 * offset + THREE.ARMS.index(case["policy"])]:
        raise PermissionError("three-arm case not in frozen exact allocation")
    if (type(transport_fingerprint) is not str or
            transport_fingerprint != B1.source_fingerprint()):
        raise PermissionError("three-arm source fingerprint mismatch")
    if not isinstance(spec, RA.WorldSpec):
        raise PermissionError("three-arm spec invalid")
    if RA.world_sha256(spec) != RA.world_sha256(
            SPECS._construct_f0_spec(case["family"], case["world_seed"])):
        raise PermissionError("three-arm spec is not source-generated exact WorldSpec")
    return RA.mint(cohort="engineering", family=case["family"],
                   index=case["index"], world_seed=case["world_seed"],
                   spec=spec, transport_fingerprint=transport_fingerprint)


def admit_three_arm_newworld_development(*, case: dict, spec,
                                          transport_fingerprint: str):
    """Central, exact-source, NEW three-arm exploratory-development guard.

    New 360000..360063 indices only; never old 80/81, old B1, validation,
    selection, reserve, or the already consumed PUBLIC engineering units.
    The trusted-main pre-exposure source claim is separately enforced by
    stage2_three_arm_development.execute and its single-run workflow.
    """
    from . import stage2_three_arm_development as THREE
    from . import stage2_survival_b1_worldspec_audit as SPECS
    from . import stage2_survival_b1_engineering as SOURCE
    if type(case) is not dict or type(case.get("index")) is not int:
        raise PermissionError("three-arm development requires exact case")
    if case.get("cohort") != "development":
        raise PermissionError("only new three-arm development, never reserve/validation")
    if not (THREE.START <= case["index"] < THREE.START+THREE.UNITS):
        raise PermissionError("three-arm index not allocated")
    if case.get("policy") not in THREE.ARMS:
        raise PermissionError("unauthorized three-arm policy")
    THREE.match_case(case,transport_fingerprint)
    if (not isinstance(spec,RA.WorldSpec) or
            type(transport_fingerprint) is not str or
            transport_fingerprint != SOURCE.source_fingerprint()):
        raise PermissionError("invalid developmental source or WorldSpec")
    expected = SPECS._construct_f0_spec(case["family"],case["world_seed"])
    if RA.world_sha256(spec)!=RA.world_sha256(expected):
        raise PermissionError("three-arm WorldSpec altered from prospective source")
    return RA.mint(cohort="development",family=case["family"],
                   index=case["index"],world_seed=case["world_seed"],
                   spec=spec,transport_fingerprint=transport_fingerprint)


def admit_replay_content_newworld_engineering(*, case: dict, spec,
                                               transport_fingerprint: str):
    """New replay-content pair gate for 12 UNUSED PUBLIC engineering units.

    Separate from every spent DEVELOPMENT, SELECTION, VALIDATION or reserve
    allocation. Exact seed, policy, source fingerprint and WorldSpec required.
    """
    from . import stage2_replay_content_engineering as CONTENT
    from . import stage2_survival_b1_worldspec_audit as SPECS
    from . import stage2_survival_b1_engineering as SOURCE
    if type(case) is not dict or type(case.get("index")) is not int:
        raise PermissionError("full-life content engineering requires exact case")
    if case.get("cohort") != "engineering":
        raise PermissionError("replay-content scientific World is NOT admitted")
    CONTENT.match_case(case,transport_fingerprint)
    if (type(transport_fingerprint) is not str or
            transport_fingerprint != SOURCE.source_fingerprint()):
        raise PermissionError("unknown replay-content source")
    if not isinstance(spec,RA.WorldSpec):
        raise PermissionError("invalid replay-content WorldSpec")
    expected=SPECS._construct_f0_spec(case["family"],case["world_seed"])
    if RA.world_sha256(spec)!=RA.world_sha256(expected):
        raise PermissionError("replay-content WorldSpec not source-generated")
    return RA.mint(cohort="engineering",family=case["family"],
                   index=case["index"],world_seed=case["world_seed"],
                   spec=spec,transport_fingerprint=transport_fingerprint)


def admit_replay_content_newworld_development(*, case: dict, spec,
                                               transport_fingerprint: str):
    """Exactly allocated NEW 48-pair replay-memory content DEVELOPMENT only.

    No previously used B1, three-arm, selection, validation, reserve or
    technical-engineering source can mint this ticket. One-shot trusted-main
    remote source custody is separately required by the experiment runner.
    """
    from . import stage2_content_48_development as CONTENT
    from . import stage2_survival_b1_worldspec_audit as SPECS
    from . import stage2_survival_b1_engineering as SOURCE
    if type(case) is not dict or type(case.get("index")) is not int:
        raise PermissionError("replay-content DEVELOPMENT requires exact assigned case")
    if case.get("cohort")!="development":
        raise PermissionError("selection, validation and reserve never opened")
    CONTENT.match_case(case,transport_fingerprint)
    if (not isinstance(spec,RA.WorldSpec) or
            type(transport_fingerprint) is not str or
            transport_fingerprint!=SOURCE.source_fingerprint()):
        raise PermissionError("wrong replay-content developmental source")
    expected=SPECS._construct_f0_spec(case["family"],case["world_seed"])
    if RA.world_sha256(spec)!=RA.world_sha256(expected):
        raise PermissionError("content WorldSpec is not exact frozen generator output")
    return RA.mint(cohort="development",family=case["family"],
                   index=case["index"],world_seed=case["world_seed"],
                   spec=spec,transport_fingerprint=transport_fingerprint)


def admit_water_replay_observer_engineering(*, case: dict, spec,
                                            transport_fingerprint: str):
    """Two UNEXPOSED PUBLIC-synthetic technical indices for observer neutrality.

    The only minting route for the observer GATE-vs-random-content engineering
    preflight. No scientific development, validation or reserve authority.
    """
    from . import stage2_water_replay_observer_engineering as OBS
    from . import stage2_survival_b1_worldspec_audit as SPECS
    from . import stage2_survival_b1_engineering as SOURCE
    if type(case) is not dict or type(case.get("index")) is not int:
        raise PermissionError("exact observer engineering case required")
    if case.get("cohort") != "engineering":
        raise PermissionError("no scientific observer cohort admitted")
    OBS.match_case(case, transport_fingerprint)
    if (not isinstance(spec, RA.WorldSpec) or
            type(transport_fingerprint) is not str or
            transport_fingerprint != SOURCE.source_fingerprint()):
        raise PermissionError("observer engineering source changed")
    expected = SPECS._construct_f0_spec(case["family"], case["world_seed"])
    if RA.world_sha256(spec) != RA.world_sha256(expected):
        raise PermissionError("observer WorldSpec is not the exact generated F0 source")
    return RA.mint(cohort="engineering", family=case["family"],
                   index=case["index"], world_seed=case["world_seed"],
                   spec=spec, transport_fingerprint=transport_fingerprint)


def admit_water_divergence_newworld_development(*, case: dict, spec,
                                                transport_fingerprint: str):
    """New 510000..510023 observability DEVELOPMENT, exact sources only.

    Different from all consumed scientific cohorts and PUBLIC engineering,
    with a separate remote one-shot source claim before any World birth.
    """
    from . import stage2_water_divergence_24_development as WAT
    from . import stage2_survival_b1_worldspec_audit as SPECS
    from . import stage2_survival_b1_engineering as SOURCE
    if type(case) is not dict or type(case.get("index")) is not int:
        raise PermissionError("exact newly allocated developmental case required")
    if case.get("cohort") != "development":
        raise PermissionError("water divergence selected/validation/reserve forbidden")
    WAT.match_case(case,transport_fingerprint)
    if (not isinstance(spec,RA.WorldSpec) or
            type(transport_fingerprint) is not str or
            transport_fingerprint!=SOURCE.source_fingerprint()):
        raise PermissionError("wrong water divergence source or WorldSpec")
    expected=SPECS._construct_f0_spec(case["family"],case["world_seed"])
    if RA.world_sha256(spec)!=RA.world_sha256(expected):
        raise PermissionError("water divergence WorldSpec altered")
    return RA.mint(cohort="development",family=case["family"],
                   index=case["index"],world_seed=case["world_seed"],
                   spec=spec,transport_fingerprint=transport_fingerprint)
