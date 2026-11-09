# I3: Test plan

## Current Stage 2 checks

Current source-of-truth: [ACTIVE_SURFACE.md](ACTIVE_SURFACE.md).

| Area | Current check | Scientific meaning |
| --- | --- | --- |
| Active-surface contract | `tests/i3/test_active_surface.py` | Checks all intra-I3 imports and internal links, archived Stage-1 modules, lazy legacy runtime isolation, the closed 68/69 runner, and current ADR-0017/ADR-0019 governance; software-only checks, never a scientific GO |
| Stage 2.1 replay gate | `tests/i3/test_p13_replay_gate_mind.py` | Software/unit properties of the corrected frozen mechanism; **not** the one-shot R0-R4 scientific verdict |
| ADR-0017 execution custody | `tests/i3/test_stage2_execution_pipeline.py` | Two-phase G/R, engineering cohort and sealed-rehearsal mechanics; never evidence by itself |
| Stage-2.1 first-exposure original custody | `tests/i3/test_stage2_development_80_81_archive.py` | Read-only hash and identity verification of 36 immutable originals, one-shot source lock, G/R result and prospectively calculated RANDOM-EQUAL-MEAN mean; never reopens a World or asserts favorable outcomes |
| Corrected R0-R4 falsifier | `lab/stage2_replay_gate_falsifier.py` | **Executed once: `REPLAY_GATE_CAPACITY_SHOWN`**, R0-R4 PASS; no World/life. Machine result is preserved under `studies/stage2-replay-gate-software/` |

Historical suite-size statements below certify their own dated commits only.
They are not the current I3 test count.


| Level | Scope | Status |
| --- | --- | --- |
| Software contract | `tests/i3/test_core.py` : closed genome, physical model v4, vital currency, capacities, local capture, irreversible death, blank-slate newborn, exact replay, token-renaming invariance, no default abstention, no preferred `attendre` action, time budget | Implemented |
| G2 gate | Preregistered behavioral falsifier, replay, and <= 1 ms/step | Preregistered |
| P2 | Three mechanistically distinct ecologies, four disjoint cohorts, sealed reserve, funded two-phase probes, exact cost control and development-calibrated static tariff | Software tests implemented; scientific validation not established |
| P3 | Lineage without inherited memories, random-parent control, 72 distinct Worlds, 864 evidenced lives and reconstruction of 48 G2 genomes | Implemented and run on selection only; no scientific GO or P4 validation |
| P4 | Validation of fixed G2 genomes (P4a), computed and paid ablation without retaining effects/values (P4b), paired individual histories and 48 new World conditions in total | Two first preregistered experiments completed: P4a 288 lives, P4b 576 lives; realized cognitive cost differs between conditions; no scientific GO |
| P5a | Three paid retention ablations, 48 G2 genotypes, 24 new Worlds, four genetic populations and complete phase-cost witnesses | First preregistered screen executed: 1,152 lives. Without learned effects, 0/288 survive versus 112/288 normal; without values 117/288, without replay 119/288. Exploratory n=4 and divergent realized costs. [Results](studies/p5a-paid-component-screen/RESULTS.md) |

## Foundation controls

`tests/i3/test_foundation.py` adds software-only checks for valid cognitive
work, explicit payment shortfalls, pending replay bills, sensorimotor updates
independent of learned updates, and full-world/source manifests. Four original
development-fixture hashes check behavioral parity. These are not held-out
scientific evaluations. See [development plan](DEVELOPMENT_PLAN.md) for the
open funding gap and the approved P1.3/P2/P3/P4 sequence.

## Funded substrate v2 (#1004)

`test_funded_cognition.py` adds pre-computation allowance, strict physical debit,
transaction rollback, exhaustion/inactivity, immediate bounded replay and
no-postmortem-work checks. `test_foundation.py` now expects overdraft rejection
and v2 phase evidence rather than the historical observer-only shortfall and
pending-replay behavior. Historical v1 hashes are retained but are not v2 parity
targets. No historical result is rewritten to make tests pass.

Current focused suite: 66 tests (62 at #1004, plus the probe checks below). The
[funding contract](COGNITIVE_FUNDING.md) records exact model limits and a
development-only adverse differential. Engine activation, a 1 ms performance
guarantee, learning benefit and lineage outcomes are NOT established by these checks.

## Laboratory probes under v2

`test_lab_probes.py` runs both probes on development cases where they used to
raise under v2, and checks that every command pays `PROBE_WORK` first, that a
motor command also leaves the next bill funded (otherwise the probe sleeps), and
that an unpayable bill gives null commands with zero work. These checks make the
probes executable; they do not validate them as comparators (P2).

| Revisable beliefs (P1.3) | `tests/i3/test_place_beliefs.py`: inherited revision rate, gene sampled last, visible cell equals current observation | Implemented |
| Selection gate v2 | `lab/selection_gate_v2.py` (ADR-0015); G2e adopted P1.3 | Implemented |

## P2 controlled engineering validation

`test_p2_ecologies.py` checks source-stable world replay, distinct ecology mechanisms,
world invariants, no hidden capture, historical cohort exclusion, reserve locking,
individual-to-probe paid-work receipts and rejection of altered frozen tariffs.
`lab/p2_validation.py` offers a development-only diagnostic and a development-
calibrated static tariff. Neither output is a selection result nor a held-out
comparison. For prospective studies, report full paid-cost coverage instead
of calling any heuristic an optimal ceiling. See
[P2 contract](P2_ECOLOGY_AND_PROBE_CONTRACT.md).

## P5b prospectively evaluated readout mechanism

[Registered P5b source and design](P5B_HELDOUT_PREREG.md);
[complete original evidence and costs](studies/p5b-paid-readout-heldout/RESULTS.md).
All 48 fixed G2 genotypes, 24 novel world indices 72–95, four
independent genetic populations, 1152 paid lives, no retry or reserve
use. Full readout survival 98/288, action-specific prediction
masked 0/288, action-agnostic personal prior 0/288,
learned sleep forecast masked 90/288. Three predeclared
population-level contrasts, n=4 exact p floor 0.125, no
confirmatory significance. Phase-paid activity, score witnesses
and original SHA custody verified. No global GO.

## P5c paid curiosity/risk score-addend prospective screen

[Preregistered protocol](P5C_HELDOUT_PREREG.md) and
[complete original experiment](studies/p5c-paid-score-addends/RESULTS.md).
24 new validation worlds 96–119, all 48 fixed G2 genotypes,
1152 original paid lives, four matched score-component interventions.
Normal censored survival 110/288, discard curiosity 4/288, discard
uncertain-meal risk 105/288, discard both 7/288. Curiosity
normal-minus-intervention per genetic population [+21,+41,+22,+22]
survivors per 72; exact two-sided p=0.125, Holm p=0.375,
so no conventional confirmatory inference or global GO.
Independent original-custody checks all experiment identities,
actual phase charges, computed/applied score terms, and no
postmortem work, without any additional study life.

| Carried-food future reuse | `tests/i3/test_carried_food_future_reuse.py`: default equals #1102, repeats bounded by carried units, branches stay personal rows, information only from branch disagreement, every plan paid, renaming invariance | Implemented |
| Carried-food raw-rank audit | `tests/i3/test_stage1_carried_food_rank_audit.py`: audit boundary (no runtime, no World built or stepped), descriptive placement | Implemented |
| ω innate expectation | `tests/i3/test_omega_innate_expectation.py`: default = zero-mean prior, mean shift ω·s with spread kept, bounds, identical paid work across ω, personal-support paths and genome untouched, falsifier fixtures = #1101 | Implemented |
| Projection accounting | `tests/i3/test_projection_consistency.py`: default is the reference, unknown mode rejected, unit chunks identical, trapezoid exact for linear distress, identical paid units, smaller projection-equivalent gap | Implemented (opt-in, not promoted) |
