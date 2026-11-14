# I3: Test plan

## Stage-6-light native-original shape/custody preflight, zero World (14 November 2026)

[`test_stage6_light_native_custody_preflight.py`](../../../tests/i3/test_stage6_light_native_custody_preflight.py) uses the [stdlib-only archive reader](../lab/stage6_light_native_custody_preflight.py) and [preflight record](studies/stage6-light-preparation/STAGE6_LIGHT_NATIVE_ORIGINAL_PREFLIGHT_2026-11-14.md). Generates fake native-format G0 (2,304) and three-generation (11,520) sealed records, then verifies all manifest and gzip digests, safe filenames, 96 per-generation World opportunities, native V2 hashes/clean claimed Git source, World snapshots, exact generic genome-v4 bounds, settled paid energy/vigilance, and fail-closed denial of source/permission tampering, malformed life/parent/World coordinates, seed collisions, hidden originals and decompression bombs. **Never** imports I3 biology, opens a World, executes life, validates real scientific independence or issues owner authorization. Source-head claims and receipt-chain endings are structural, not independently authenticated. Stage6 scientific admission remains blocked by issue #1395.

## Stage-6-light source-only G/S/R synthetic preflight (13 November 2026)

[`test_stage6_light_synthetic_transport.py`](../../../tests/i3/test_stage6_light_synthetic_transport.py) exercises the [toy transport](../lab/stage6_light_synthetic_transport.py) and [documentation](studies/stage6-light-preparation/STAGE6_LIGHT_TOY_TRANSPORT_PREFLIGHT_2026-11-13.md) using invented scalar persistence receipts, a fake G2 gene table and collision-only mock seed values. The exact fixed 11,520-row G0/S/G1/S/G2/R sequence is checked *without* any I3 engine import, WorldSpec, live Mind, genome mutation or birth. It rejects malformed/oracle-leaky receipts, absent/duplicate World coordinates, wrong censures, modified SHA seals, altered parent commitments, unauthorized state transitions and forged owner indices. Outputs are `TOY_*`, never scientific verdicts; the mock allocation never claims independence or assigns real seeds. **No live rehearsal, permission, cohort, World or index is triggered**. Scientific transport qualification and admission remain blocked on #1395.

## Stage-6-light methodology, zero-World controls (13 November 2026)

The [fixed-method preauthorization plan](studies/stage6-light-preparation/STAGE6_LIGHT_PROTOCOL_METHOD_V1_2026-11-13.md) and [non-executable manifest](studies/stage6-light-preparation/STAGE6_LIGHT_PROTOCOL_METHOD_V1.json) are tested by `tests/i3/test_stage6_light_protocol_preauth.py`. The tests assert the 16×24×G0/G1/G2 schedule, the **unique** G0 2,304 + G1/G2 4,608 each = 11,520 eventual lives, 288 **logical** World coordinates, exact two-sided sign count 13/16, null model assumptions and three neutral sentinels. Adversarial mutations of every authorization field, fake owner evidence, reopened cohort and postmortem/retry rights fail closed. They create **zero** Worlds/lives and never call a science runner. The separately archived original Git-bundle provenance check remains in `tests/i3/test_stage6_light_bundle_provenance.py`. Future full-scale engineering rehearsal and science are **not** authorized by these tests.

## Current Stage 2 checks

Current source-of-truth: [ACTIVE_SURFACE.md](ACTIVE_SURFACE.md).

| Area | Current check | Scientific meaning |
| --- | --- | --- |
| Active-surface contract | `tests/i3/test_active_surface.py` | Checks all intra-I3 imports and internal links, archived Stage-1 modules, lazy legacy runtime isolation, the closed 68/69 runner, and current ADR-0017/ADR-0019 governance; software-only checks, never a scientific GO |
| Stage 2.1 replay gate | `tests/i3/test_p13_replay_gate_mind.py` | Software/unit properties of the corrected frozen mechanism; **not** the one-shot R0-R4 scientific verdict |
| Stage 2.1 inference / power audit | `tests/i3/test_stage2_gate_design.py` and [exact power review](studies/stage2-replay-gate-selected-design/INFERENCE_POWER_AUDIT.md) | Exact software-only sign-test power sensitivity and mean non-inferiority counterexample; **REVISE / NO SCIENTIFIC WORLD**, no confirmatory GO |
| Stage 2.1 96-pair new-world B1 engineering G/R | `tests/i3/test_stage2_survival_b1_engineering.py`, [fixed first-96 protocol](studies/stage2-replay-gate-selected-design/B1_NEW_WORLDS_PAIRED_GR.md), I3 B1 new-world CI Python 3.11/3.12 | Exact 192 live funded technical FIXED/GATE transport on synthetic proposed high-range WorldSpecs, immediate sealed original G and digest-verified R, zero-inference structural-only return, forged science/seed/policy blocked before World construction |
| Stage 2.1 B1 synthetic WorldSpec compatibility/collision audit | `tests/i3/test_stage2_survival_b1_worldspec_audit.py`, [WorldSpec preflight](studies/stage2-replay-gate-selected-design/B1_PROSPECTIVE_WORLDSPEC_PREFLIGHT.md) | Exact WorldSpec SHA parity with historical P2 non-reserve seeds; full 1,500 public-root F0 spec generation and structural checking in Python 3.11/3.12; reject full/name-independent fingerprint duplicates; **no live individual, science World, owner admission or iid certification** |
| Stage 2.1 prospective B1 pair allocation preflight | `tests/i3/test_stage2_survival_b1_sampling.py`, [sampling contract](studies/stage2-replay-gate-selected-design/B1_PROSPECTIVE_SAMPLING_PREFLIGHT.md), existing B1 CI dry-run | Deterministic 1500 whole-pair world/genome/life metadata, disjoint domains, unbiased equal-family draw rule, no-shift duplicate/tampering checks, structural-only digest; **no Worlds or approved iid/owner authority** |
| Stage 2.1 optional GATE audit/motor reserve correction | `tests/i3/test_stage2_optional_audit_motor_reserve.py`, [B1 engineering failure/correction](studies/stage2-replay-gate-selected-design/SURVIVAL_B1_LAUNCH.md) | Synthetic low-energy edge prevents post-decision audit from invalidating an already admitted motor action; action/Competition unchanged; **new prospective source revision, historical 80/81 not reinterpreted** |
| Stage 2.1 autonomous B1 exact paired survival and engineering smoke | `tests/i3/test_stage2_exact_paired_survival.py`, `tests/i3/test_stage2_survival_b1_engineering_plan.py`, [B1 launch](studies/stage2-replay-gate-selected-design/SURVIVAL_B1_LAUNCH.md), `.github/workflows/i3-proposal-checks.yml` | Exact one-sided Clopper-Pearson/Bonferroni iid matched-survival bound with exhaustive small-n coverage checks and synthetic conditional-power sensitivity; 24 temporary genuine ENGINEERING lives via sealed G/R, structural outputs only, **zero science admission** |
| Stage 2.1 confirmatory survival power study | `tests/i3/test_stage2_confirmatory_survival_power.py`, [power campaign](studies/stage2-replay-gate-selected-design/CONFIRMATORY_SURVIVAL_POWER_STUDY.md) | Conditional Hoeffding independent-pair upper-size guarantees vs explicitly approximate paired discordance models, alpha/power/margin scenario sensitivity, F0 pseudoreplication guard; **scientific exposure blocked, no approved sample size or GO** |
| Stage 2.1 archived 80/81 scientific reanalysis | `tests/i3/test_stage2_development_reanalysis.py`, [phase-A report](studies/stage2-replay-gate-selected-design/ANALYSIS_CAMPAIGN_2026-11-09.md) | Read-only published plan/manifest/results/source-lock pins, verify all 36 historical gzip originals against archived reduced records, expose paired/family survival and per-assigned-life cognition, reject forged/missing receipt; **no World opened, inference or new scientific exposure** |
| Stage 2.1 three-policy control accounting | `tests/i3/test_stage2_mechanism_first_design.py`, `tests/i3/test_stage2_mechanism_first_sealed.py`, [triangular interpretation](studies/stage2-replay-gate-selected-design/PAIRED_SURVIVAL_PROFILE.md) | Reports full RANDOM−FIXED policy effects and 240-block algebraic GATE−FIXED = GATE−RANDOM + RANDOM−FIXED reconciliation, including subgroup harm. **No causal mediation or science GO** |
| Stage 2.1 paired-survival and cognition-harm profile | `tests/i3/test_stage2_mechanism_first_design.py`, `tests/i3/test_stage2_mechanism_first_sealed.py`, [paired interpretation](studies/stage2-replay-gate-selected-design/PAIRED_SURVIVAL_PROFILE.md) | Synthetic matched survivors/deaths, step-400 death, opposed family harms hidden by a zero mean, and cognition savings with earlier mortality; **descriptive only, no World** |
| Stage 2.1 replay exposure and paid parity audit | `tests/i3/test_stage2_mechanism_first_sealed.py`, [v3 custody and exposure](studies/stage2-replay-gate-selected-design/MECHANISM_FIRST_SEALED_READOUT.md) | Measures actual funded decision-audit/sleep/replay outcomes, RANDOM nominal/eligible/paid gaps and rejects impossible counters; **no causal or scientific GO** |
| Stage 2.1 mechanism-first sealed original adapter | `tests/i3/test_stage2_mechanism_first_sealed.py`, [v3 archive contract](studies/stage2-replay-gate-selected-design/MECHANISM_FIRST_SEALED_READOUT.md) | Synthetic 720-life full original G0 blocks, distinct v3 source lock, RANDOM funding and forbidden cross-protocol originals; **no World, source-owner authority, or scientific verdict** |
| Stage 2.1 mechanism-first study option | `tests/i3/test_stage2_mechanism_first_design.py`, [v3 design](studies/stage2-replay-gate-selected-design/MECHANISM_FIRST_CANDIDATE_V3.md) | 720 **synthetic** matched newborn G0 lives, complete receipt checks, restricted duration and paid per-assigned-life contrasts; descriptive only, no new World and no survival non-inferiority claim |
| Exact run_life original-schema custody regression | `tests/i3/test_stage2_sealed_selection_bridge.py`, [corrected schema contract](studies/stage2-replay-gate-selected-design/SEALED_SELECTION_BRIDGE.md) | Distinguishes reference (no ticket) from replay arms (`admission`), verifies original manifest/source/world/G0/policy/funding consistency and rejects forged self-resealed records; **synthetic only, no World** |
| Read-only sealed selection/validation bridge | `tests/i3/test_stage2_sealed_selection_bridge.py`, [custody contract](studies/stage2-replay-gate-selected-design/SEALED_SELECTION_BRIDGE.md) | Synthetic 3,840-selection/1,200-validation original-mapping checks, source-lock and gzip SHA tamper detection; no source authority, real World, or confirmatory verdict |
| Stage 2.1 finite-panel reduced-receipt contract | `tests/i3/test_stage2_finite_panel.py`, [receipt contract](studies/stage2-replay-gate-selected-design/FINITE_PANEL_RECEIPTS.md) | 1,200 **synthetic** complete identifiers, strict terminal/mortality/paid-cost checks and missing/forged rejection; not original custody or scientific inference |
| Proposed mean-survival inferential correction | `tests/i3/test_stage2_mean_survival_sensitivity.py`, [v2 candidate](studies/stage2-replay-gate-selected-design/PROTOCOL_REVISION_V2.md) | Population-level Hoeffding sensitivity and adversarial incomplete-receipt inputs only; **no World, no inference review, no scientific GO** |
| Prospective RANDOM control, 8-population design and exhausted authority | `tests/i3/test_stage2_random_equal_mean.py`, `test_stage2_gate_design.py`, `test_p13_replay_gate_mind.py`, `test_stage2_exact_transport.py` | Pure count arithmetic, genuine funded engine behavior on non-evidentiary `engineering` cases, hard-closed old scientific entrypoints; not a validation study or survival GO |
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
