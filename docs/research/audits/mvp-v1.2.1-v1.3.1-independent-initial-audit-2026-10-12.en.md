# Individual Zero: independent MVP v1.2.1 / v1.3.1 conformance review

**Inspection date:** 2026-10-12 (Europe/Paris)  
**Frozen source baseline:** `7297793c73a24764747f43db82910a7e94fb7ab7` on protected `main`  
**Normative sources:** `docs/architecture/reference/en/mvp-specification-v1.2.1.md` and `mvp-specification-v1.3.1.md`. Both exact paths were present and read.  
**Evidence level:** GitHub remote tree/selected-source inspection, normative text, open PR metadata, and external CI job status. **No local Python tests were executed** because the working container could not resolve github.com and a complete checkout was unavailable. Consequently no runtime correctness is independently certified by this review. This is a **bounded initial audit**, not a completed exhaustive audit.

## Authority and mapping

* v1.2.1 retains architecture, stages 1-13, six cognitive phases, 53 numbered invariants, 58 numbered parameters and DC-01..DC-17 except where expressly superseded.
* v1.3.1 §10 expressly replaces v1.2.1 §18 lethal rollback/checkpoints/masks and former INV-27/28/29/39/49 rollback-specific obligations with forward-only terminal mortality, the no-rewind rules (§§2-4), and checks M-01..M-20 (§9). Retain the non-conflicting safety parts.
* v1.3.1 expressly restores the exhaustive canonical SHA-256 journal and its independent verification, which v1.3.0 had proposed to remove; snapshots cannot recover older committed states of the *same* mortal identity.
* v1.3.1 additionally requires Oracle/Bench independence, epistemic isolation, dual technical/consolidated history, and separately identified development / operator / scientific gates.
* Superseded historical tests remain useful legacy compatibility evidence but must not be presented as v1.3.1 acceptance.

## Current findings (the commit above, no proposed code fixes merged)

| ID | Priority | Classification | Source | Code location | Observation | Resolution | Residual risk |
|---|---|---|---|---|---|---|---|
| IZ-001 | P1 | Confirmed incomplete | v1.3.1 §4, §9 M-11 | `src/lab/journal.py:87-156`; `src/lab/stage11_sleep_runtime.py:24-42` | Exclusive fsynced WAL exists and integrated birth requires a fresh WAL. No verified atomic restore of the *latest coherent current runtime state* after nonterminal crash was found. WAL audit returns receipt, not runnable state. | Open | Recovery could lose applied state or resume from older state; no M-11 certification. |
| IZ-002 | P1 | Confirmed partial | v1.2.1 §15.6, INV-23/24/47; v1.3.1 §§4,5.3 and M-08 | `src/lab/stage10_runtime.py:581-657` | Live six-pass runtime code was merged during this inspection. Publication intentionally defers semantic active-form changes and handles only an identity rebase of already published Q/κ/precision/causal owner states. | Open | Full synchronized semantic owner rebase not established. |
| IZ-003 | P1 | Confirmed incomplete | v1.2.1 §17.7, INV-34; v1.3.1 §2, M-13 | `src/lab/stage5_runtime.py:154-175` | Mortal copy creation intentionally fails closed, pending distinct birth-time lineage and journal-prefix custody. | Open | Normative copy feature unavailable for mortal I0. |
| IZ-004 | P1 | Confirmed partial | v1.2.1 §20.3 Stage 12, §16, DC-07/14; v1.3.1 §7 | `src/i0/modules/stage12_detectors.py` exists; `src/lab/stage12_runtime.py` absent on baseline | Four lived-only detectors are merged, but unified Stage12 runtime, operator controls, degraded-mode campaign and acceptance are not present on this baseline. | Open; review PR #84/#90 and experimental #88 separately | Stage12 not software-complete. |
| IZ-005 | P2 | Confirmed incomplete | v1.2.1 §20.3 Stage 13; v1.3.1 §7.3 | `src/lab/stage13_final_preregistration.py` | Structural preregistration preflight is present, but final independent campaign, module-wise verdicts, controlled held-out trials and operator approval have not happened. | Open | Scientific claims unverified; stage stays in progress. |
| IZ-006 | P1 | Confirmed plausible misattribution path, behavioral reproduction not independently rerun | v1.2.1 §13, DC-05, INV-25; v1.3.1 §6, M-10 | `src/i0/modules/causal_model.py:1180-1279`; `src/lab/epistemic_guard.py` | A food exposure with reduced integrity can produce `toxic_item` evidence when hidden ambient damage is removed from lived effects. A known hidden competing cause is no longer present to veto credit. PR #93 supplies matched lived ambient control and a real WorldBody negative test but is not on audited baseline. | Open | False learned safety attribution under latent confounding. Historical Stage9 scientific NO-GO unchanged. |
| IZ-007 | P1 | Confirmed unguarded path, fault effect requires execution | v1.3.1 §4, M-03/M-04/M-09 | `src/lab/stage10_runtime.py:791-862`; `src/lab/stage4_runtime.py:932-1084` | Stage10 catches consolidation errors but not every later sleep or waking owner callback failure after physical closure; PR #83 explicitly adds broad fail-stop fault injection. | Open | An uncertain cognitive owner state could remain with mortal status active. Requires fault injection. |
| IZ-008 | P2 | Confirmed remaining historical mode, production activation needs decision | v1.3.1 §§2-3, §9 M-04 | `src/lab/stage2_runtime.py:346-488`; `src/lab/safety_protocol.py:110-190`; `src/lab/snapshots.py:212-277` | Default historical fixture retains lethal checkpoint/rollback, while `autonomous_mortal=True` selects forward-only. The specification explicitly permits historical fixtures but not active I0 life fallback. No complete entrypoint/use-site classification performed. | Open verification | Wrong constructor/default could still select old behavior. |
| IZ-009 | P2 | Confirmed documentation/verification gap | v1.3.1 §7.1, M-14/15/20 | `.github/workflows/ci.yml`; `src/lab/stage11_autonomous_600_step_probe.py` | 600 actual Stage11 steps are checked in manually requested full CI; only such branch-SHA evidence was inspected, not rerun on frozen main, and it does not cover all modules (notably Stage12 and full sleep). | Open | Tests on other PR heads cannot certify combined main or science. |

**Confirmed-by-inspection is not equivalent to an independently executed failing test.** Counts: P0 = 0 confirmed by this review; P1 = 6 records (IZ-001/2/3/4/6/7); P2 = 3 (IZ-005/8/9); P3 = 0. P0-level invariants remain **unverified** and possible failures cannot be excluded.

## Stage-by-stage evidence

| Stage | Code observed on baseline | Software assessment | Operator | Scientific |
|---|---|---|---|---|
| 1 Execution substrate | `stage1_runtime.py`, scheduler, bus, determinism, journal, snapshots, tests | Implemented; historic deterministic evidence only, v1.3.1 no-life-rewind integration not fully retested | historical approvals not independently reauthenticated | not verified |
| 2 World/body/bench | `world.py`, `stage2_runtime.py`, `oracle.py`, `bench.py`, `mortal_execution.py` | Separate legacy vs mortal paths, physical parity tests present | not reauthenticated | not verified |
| 3 Reflex | `stage3_runtime.py`, `action_control.py` | Implemented; mortal reflex parity requires fresh integrated run | not reauthenticated | not verified |
| 4 Minimal cognition | `stage4_runtime.py`, gating, needs, goals, competition | Implemented; fault containment of integrated cycles pending | not reauthenticated | not verified |
| 5 Temperament/copies | `stage5_runtime.py`, traits, battery | Temperament exists; mortal copying blocked (IZ-003) | not reauthenticated | not verified |
| 6 Equipment/simulator | `stage6_runtime.py`, planning/simulator/corpus | Implemented, cross-stage performance unverified | not reauthenticated | not verified |
| 7 Memory | `stage7_runtime.py`, `memory.py`, provenance/policy tests | Implemented with restrictive autobiographical projection; negative security tests exist | not reauthenticated | not verified |
| 8 TD/precision/κ | `stage8_runtime.py`, corresponding modules/tests | Implemented; long-life postcut and mortal integration require tests | not reauthenticated | not verified |
| 9 Causal/agency | `stage9_runtime.py`, `causal_model.py` | Implemented but ambient confounding issue IZ-006 | not reauthenticated | historical scientific **NO-GO** |
| 10 Sleep/consolidation | `stage10_runtime.py`, six-pass test integrated in later main | Six-pass mechanism present but semantics rebase/terminal fault matrix incomplete | spec records historical approval; **not a new v1.3.1 approval** | not verified |
| 11 Exploration/modulation | `stage11_runtime.py`, `stage11_sleep_runtime.py` | Implemented; standalone mortal 600-step program exists; combined coverage incomplete | spec records historical approval; **not a new v1.3.1 approval** | not verified |
| 12 Metacognition | `stage12_detectors.py` only, runtime on PR #84 | Incomplete | not approved | not verified |
| 13 Scientific campaign | structural preflight module only | Campaign not conducted | not approved | not verified |

## Consolidated v1.3.1 check matrix (normative §9)

Each state is a **bounded code/CI evidence assessment**, not a passing test assertion.

| Check | State | Evidence / reason | Finding |
|---|---|---|---|
| M-01 | Partially conforming | Mortal send once and close logic in Stage2; failures across later owners still untested | IZ-007 |
| M-02 | Not verified | `mortal_execution.py` and world physics tests exist; full combined hazards parity not executed here | — |
| M-03 | Partially conforming | Terminal gates / postdeath journal seal present; exceptions in all phases not fully guarded | IZ-007 |
| M-04 | Partially conforming | Mortal dispatch omits checkpoint; historical default persists, no full entrypoint map | IZ-008 |
| M-05 | Not verified | Physical state parity tests exist, no frozen-main independent replay executed | — |
| M-06 | Not verified | Control/veto source read; full matched-case parity not executed | — |
| M-07 | Partially conforming | Hash journal, lived projections, separate SlowHistory; end-to-end parity untested | IZ-002 |
| M-08 | Partially conforming | Live passes and identity owner rebase only | IZ-002 |
| M-09 | Partially conforming | Scenario prevalidation and halt logic; combined fault matrix unrun | IZ-007 |
| M-10 | Partially conforming | Explicit projection allowlist, recursive rejection and negative tests; in-process Python remains non-sandboxed | IZ-006 |
| M-11 | Non-conforming / not completed | WAL without coherent current-state crash restoration | IZ-001 |
| M-12 | Partially conforming | Full hash journal/WAL and offline verifier; production coverage and crash closure not all tested | IZ-001 |
| M-13 | Non-implemented for mortal copies | Mortal copy is deliberately rejected | IZ-003 |
| M-14 | Not verified | 3.11/3.12 CI exists, but no same-SHA full validated main run | IZ-009 |
| M-15 | Partially conforming | Governance and historical NO-GO preserved; new operator acceptance missing | IZ-009 |
| M-16 | Partially conforming | Blocked Oracle/Bench import tests and standalone mortal path exist; full integration parity not rerun | — |
| M-17 | Partially conforming | Oracle read-only capability with tests; adversarial world owner access not fully shown | — |
| M-18 | Partially conforming | Bench separate trace/audit import, standalone test exists | — |
| M-19 | Partially conforming | `independent_journal_audit.py` standalone code and adversarial tests; future/unexamined kinds remain a limit | — |
| M-20 | Not verified on baseline | A 600-step Stage11 probe + PR-run CI evidence, no fresh frozen-main end-to-end all-stage execution | IZ-009 |

## Invariant inventory

The preserved v1.2.1 §21.1 lists **INV-01 through INV-53**, but INV-27, 28, 29, 39 and 49 have historical lethal-rollback conditions superseded by v1.3.1 (§§2-5). Other invariants must not be assumed green. Example families: owner and epistemic boundaries (INV-01..03), cognition and scheduling (INV-04..22), sleep and postcut (INV-23/24/47), safety/causality (INV-25/26), lineage (INV-30/34), physical/technical journal (INV-33/44/52/53), degraded mode (INV-46/48). **No comprehensive 53-item runtime validation was executed here**; unresolved cases remain `Non vérifié`, not PASS.

## CI, repository and verification scope

* Inspected protected main, current git tree, active open PR descriptions/base branches and selected CI results; multiple PRs marked TEST ONLY and explicit DO NOT MERGE (#88, #86, #85).
* `pyproject.toml` supports Python `>=3.11`, zero declared runtime dependencies; `ci.yml` quick PR Python 3.12 and manual full Python 3.11/3.12. Existing `agent-b-stage10-validation.yml` is branch-specific and should not be treated as final default-branch proof.
* The previously successful full PR #93 CI run does **not** prove that PR is currently merged or that its downstream interactions are verified on main. Same principle applies to #74/#80/#84.
* Local `git clone` and `git ls-remote` failed with `Could not resolve host: github.com`. GitHub connector remote file/metadata reads succeeded, but cannot substitute for end-to-end Python runs. No local package build, full suite, security scan, permission audit or cold-start install was performed.
* Source changed during audit from `6c3f251` via `04b9aeb` to frozen `7297793`. The above code conclusions were checked against `7297793` where relevant. Future changes to main require a fresh SHA-specific run.

## Suggested operator and engineering verification (do NOT mark passed until executed)

```bash
git clone https://github.com/josselin-orta-lab/individual-zero.git
cd individual-zero
git checkout 7297793c73a24764747f43db82910a7e94fb7ab7
python3.11 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
python -m compileall -q src tests
python -m unittest discover -s tests -q
python -m unittest tests.test_epistemic_journal_isolation tests.test_independent_journal_audit tests.test_stage10_live_sixpass_runtime tests.test_stage10_live_postcut_and_halt -v
python -m lab.stage11_autonomous_600_step_probe --steps 600
python scripts/audit_mvp_v1_3_dependencies.py --root . --json-out /tmp/i0-impact-7297793.json
```

Repeat full suite under Python 3.12 in an independent fresh venv; retain `git rev-parse HEAD`, test exit codes, exact configuration, logs, head/count hashes, fixtures, and 600-step numerator/denominator. For Stage10 verify real sleep entry, six UC-paid passes, semantic active-form rebase and forced exception before/after physical effect. For M-11 hard-kill disposable independent processes and prove last coherent current-state restart without replay, old-snapshot revival or missing physical transition. For Stage12 run actual degraded modes, console and mixed 600-step coverage on an explicitly approved integration branch. For M-10 add adversarial nested read and oracle/bench noninterference tests. Operator independently signs stage gates after reviewing actual evidence, never based on this static report alone.

## GitHub disposition

Initial read-only findings committed only to an isolated audit branch. No source files, historic results, world physics, main or existing agent branches modified. No operator approvals and no scientific GO are inferred. A follow-up fully executed audit must update this document with outcomes and close only reproduced/resolved findings.
