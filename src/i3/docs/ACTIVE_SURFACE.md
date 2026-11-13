# I3 active surface

This is the short operational map for developers and agents. It does not replace
scientific evidence or ADRs. See the
[code/dependency audit](I3_DEPENDENCY_AUDIT_2026-11-09.md) for archival
rationale, checked references and deliberate compatibility boundaries. The machine-readable authority is
[`../ACTIVE_SURFACE.json`](../ACTIVE_SURFACE.json).

## Current research decision (13 November 2026)

[ADR-0021](../../../docs/decisions/ADR-0021-i3-stage2-internal-hold-no-verdict.md) and the [internal C01/RP-A1 disposition](STAGE2_C01_INTERNAL_DISPOSITION_2026-11-13.md) record `HOLD_NO_VERDICT` for the general Stage-2 question **without a mandatory external reviewer**. This is not a scientific Stage-2 negative/positive closure: `NOT_ISSUED` remains canonical; E1/E3 are negative only on frozen candidates. Keep all scientific World admissions closed, P1.3 funded-v2 unchanged, I3 unregistered and I1 active. Parallel R1/R2 M11 engineering remains permitted under ADR-0020, but not engine release.

## Current state

- **Reference:** P1.3 on funded v2.
- **Stage 1:** closed negative under ADR-0018.
- **Current stage:** Stage 2.1, replay gate.
- **Canonical Stage-2.1 status:** `REPLAY_GATE_CAPACITY_SHOWN`.
- **ADR-0017:** **owner-lifted on 9 November 2026** for fingerprint `dcada9e2…f1` and the frozen DEVELOPMENT 80/81 pilot only.
- **I3:** proposal only, unregistered.

**Current research handoff (11 November 2026, after E3):** The [Stage-2 stop and closure-readiness assessment](studies/stage2-replay-gate-selected-design/STAGE2_POST_E3_SCIENTIFIC_STOP_ASSESSMENT_2026-11-11.md) is the **current operational decision**, not the older cost-only #1302 handoff. The precommitted [E3 native VISIBLE-versus-paid-discard result](studies/stage2-replay-gate-selected-design/E3_NATIVE_PAID_BRANCH_DELIVERY_RESULTS_2026-11-11.md) had **equal modeled optional computation in both arms**, one intermediate native score difference among two informed *synthetic/unpaid* histories, but **zero** legal native motor changes; the separate empty-history control was null. [Exact-source CI #43065730480](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43065730480) passed **1,148/1,148 I3 software tests each** on Python 3.11 and 3.12. **This precise E3 candidate is CLOSED NEGATIVE** without post-exposure retuning. It is not a general cognition/survival failure; Stage-2 scientific verdict remains **NOT_ISSUED**. The old [cost-identifiability result](studies/stage2-replay-gate-selected-design/COMPUTATION_VALUE_IDENTIFIABILITY_RESULTS_2026-11-11.md) remains intact as historical E0 data, not the current launch instruction.

**Immediate gate:** do not create another replay head, new synthetic fixture/seed search or Stage-2.2/2.3 controller just to obtain an action. Future research requires a **genuinely distinct** first-person paid information mechanism that passes a separately frozen **no-World native-action** falsifier. The older external C01 review requirement has been replaced **for the documentary HOLD only** by the internal source-traceable disposition; it does not establish broad scientific closure. Only then consider independent ecological sampling/NI power, true physical two-currency/learning cost, exact G/R custody and a **new, separately scoped owner-index authorization**. Current `next_scientific_action` encodes this hold, **not** permission to create a World; no new World opening is authorized. Keep `fresh_lived_worlds_allowed=false`, consumed studies closed, P1.3 unchanged and I3 unregistered.

The corrected R0-R4 software falsifier executed exactly once and passed.
The hardened transport passed 36/36 G/R rehearsals on Python 3.11 and 3.12
with the **same exact content fingerprint** `dcada9e2…f1`, verified after
merging PR #1220. The owner lift is recorded in [STATUS.md](STATUS.md).
The **single prospective DEVELOPMENT 80/81 pilot has now completed**:
36/36 original lives generated, 36/36 reduced, zero structural failures;
[descriptive findings](studies/stage2-replay-gate-development-80-81/RESULTS.md).
It reduced replay and pooled paid cognition, but did **not** establish survival
non-inferiority. The owner-lifted scope is **consumed** and 80/81 is closed
without retry. All additional Worlds, validation, selection, reserve and
confirmatory gates remain closed until newly frozen authorization. The current
legacy `stage2_panel.execute()` and `stage2_admission.admit()` are now hard-closed
for all scientific cohorts, even when the historical owner-lift entry exists.
The new random-control policy is an engineering-only opt-in, not a new lift.

## Active scientific surface

Only these files define the current scientific intervention:

- `modules/p13_replay_gate_mind.py`
- `modules/stage2_random_equal_mean.py` (RANDOM-EQUAL-MEAN control)
- `lab/stage2_replay_gate_falsifier.py` (historical one-shot, do not rerun)
- `docs/STAGE2_LAUNCH.md`
- `docs/STAGE2_REPLAY_GATE.md`
- `docs/studies/stage2-replay-gate-software/RESULTS.md`

Stage 2 must not import Stage-1 laboratory helpers. If it needs one, first ask
whether the concept is genuinely current or whether historical machinery is
leaking back into the design.

## Active engineering surface

These files support ADR-0017 execution custody and are not themselves evidence:

- `lab/engineering_cohort.py`
- `lab/two_phase_panel.py`
- `tests/i3/test_stage2_execution_pipeline.py`
- `runtime/admission.py` (World-bound admission tickets)
- `lab/stage2_admission.py` (engineering tickets only, old science hard-closed)
- `lab/stage2_panel.py` (engineering rehearsal only; old pilot `execute` disabled)
- `lab/stage2_random_equal_mean.py`, `lab/stage2_gate_design.py` (software-only design)
- `tests/i3/test_stage2_random_equal_mean.py`, `tests/i3/test_stage2_gate_design.py`
- `tests/i3/test_stage2_exact_transport.py`
- `docs/studies/stage2-replay-gate-development-80-81/` (frozen plan,
  sealed rehearsal, completed immutable scientific originals and descriptive result)

The supplied 68/69 pilot runner is **archived**, not an active transport:
`archive/stage2/development_68_69.py`. Its historical observations cannot
be reused as prospective evidence. The historical transport was owner-lifted only for the frozen DEVELOPMENT
80/81 pilot; its authority is consumed. This does not retroactively legitimize the supplied 68/69 run.

## Compatibility-only Stage 1

Stage-1 candidate code is archived under `src/i3/archive/stage1/`
for retained compatibility tests and regression tooling.
They are listed in `ACTIVE_SURFACE.json`.

Their presence does **not** mean Stage 1 is open. Do not extend them into a new
candidate or use them as the current scientific handoff.

The [Stage-1 historical document catalogue](../archive/stage1/DOCUMENTS.md)
links to the frozen protocols and results at their unchanged evidence paths.
Older Stage-1 scientific runners and retired tests already moved to
`archive/i3/stage1-2026-11-09/`. Evidence under `docs/studies/` stays at its
stable paths for citation and custody.

## Read order

For current development, read only:

1. `docs/STATUS.md`
2. this file / `ACTIVE_SURFACE.json`
3. `docs/studies/stage2-replay-gate-selected-design/STAGE2_POST_E3_SCIENTIFIC_STOP_ASSESSMENT_2026-11-11.md`
4. the specific **frozen** source, protocol and tests you are auditing; read `docs/STAGE2_REPLAY_GATE.md` for the historical gate, not as an instruction to relaunch it

Read `DEVELOPMENT_PLAN.md` when changing stage boundaries or ordering. Read
older Stage-1 documents only for a named historical question.

## Drift alarms

Stop and re-evaluate if a change does any of the following:

- reopens the now-closed DEVELOPMENT 80/81 panel or any other World without
  a separately frozen protocol and fresh owner authorization;
- dispatches replay-gate cognition without a matching canonical owner lift,
  exact transport fingerprint and full-WorldSpec-bound ticket;
- changes the frozen replay-gate formula or R0-R4 rules after the canonical
  software verdict;
- treats the formally passing but flat S1 R3 fixture as proof of graded cost
  sensitivity;
- imports Stage-1 lab helpers into active Stage-2 science;
- creates another Stage-1 candidate;
- reuses supplied 68/69 as prospective evidence;
- launches Stage 2.2 or 2.3 while the scientific Stage-2.1 verdict is `NOT_ISSUED`;
- retunes the frozen E3 synthetic states after the **0/2** native action result or relabels a score-only difference as a living motor and body improvement.

The purpose of this map is not to erase history. It is to stop history from
pretending to be the present.
