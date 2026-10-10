# I0-vNext development register

**Classification:** development-only; no scientific Stage-9 acceptance.

- Git branch: `i0/vnext-stages-10-12`
- Integrated I0 software starting point: `773cd84557d661977568c318413510096d15fed0` (`main`, 2026-10-10)
- Normative specification: `docs/architecture/reference/en/mvp-specification-v1.2.1.md` (unchanged)
- Stage 9: **SOFTWARE IMPLEMENTED / SCIENTIFIC VALIDATION PENDING / NO-GO**. The independent held-out procedure is not authorized. Historical results are immutable.
- Stage 11: **IN_PROGRESS**, P-48 Exploration and later Global Modulation; no science acceptance claimed.
- Stage 10: NOT_STARTED.
- Stage 12: NOT_STARTED.

Development-only source: [Stage-9 behavior](stage9-development-behavior-2026-10-10.en.md) and [Stage-9 NO-GO](stage9-heldout-prelaunch-decision-record.md). Public seeds 41 and 42 may be used for non-held-out comparisons; no result from I0-vNext retroactively validates the Stage-9 implementation.

The I0-vNext branch must not be merged into `main` automatically. Use targeted local Python tests before commits and draft pull requests without CI labels while the GitHub Actions quota is constrained.

## First P-48 software increment (2026-10-10)

- Added `src/i0/modules/exploration.py`: canonical-causal-proof-based intrinsic interest, visit counters, habituation, stagnation/noisy-TV guard, derived exploration temperament coefficient, snapshot restoration.
- Added `src/i0/modules/stage11_evaluator.py`: additive intrinsic score for safe causal-test options. Ordinary Stage-8 extrinsic evidence and Competition remain in force; Stage-9 evaluator is unchanged.
- Added `src/lab/stage11_runtime.py` and `stage11_reference_fixture.py`: additive cycle phase-1 Exploration hook, logical UC envelope, logs, snapshot owner and vNext-only runtime.
- Added `tests/test_stage11_exploration.py`: seven targeted unit/integration/replay tests. **Repository-wide execution not verified**: the available local container cannot clone this private GitHub repository (DNS/network restriction). A local standalone draft of the Exploration module passed five isolated tests, but this does **not** certify the committed integration code.
- Still missing: integrated CI/test execution on actual checkout, side-by-side public-world diagnostic, intrinsic targets beyond causal tests, boredom, modulation profiles/hysteresis, Stage 10 and Stage 12. No behavior change is asserted without a run.
- Important limitation: the development fixture injects immutable temperament parameters derived by the Stage-5 reference fixture. Complete I0-vNext temperament mapping integration and preregistration of P-15/P-48 values remain open.
- Before review: run `python -m unittest discover -s tests -p test_stage11_exploration.py -v` on the branch, repair failures, then compare public-development worlds without accessing held-out materials. Use a draft PR without `ci-unit` / `ci-full` labels unless necessary.


## Stage-11 P-23/P-24 modulation increment (2026-10-10)

- `src/i0/modules/global_modulation.py`: normal, threat, exploration and recovery profiles; explicit versioned weight multipliers and entry/exit thresholds; step-counted confirmations; immediate threat priority; unknown state suspends exit confirmation; exact snapshot/replay.
- `src/lab/stage11_runtime.py`: phase-0 profile freeze **from the previous published S_t**, phase-2 score multipliers, recorded transitions and ownership; `S_t` records the active versioned profile plus development-only boredom/need indicators derived before phase 1.
- `src/i0/modules/gatekeeper.py` and `src/lab/stage4_runtime.py`: backward-compatible optional selection-time multiplier and hook methods; reference Stage-4--9 paths supply `None` and the former `normal` S_t profile, so historical configuration and intended causal behavior remain untouched. **Full historical golden regression is still to be verified.**
- New dedicated P-23/P-24 unit and Stage-11 integration/replay tests. Parameter numbers and the recovery multiplier are strictly **software-development values**, not frozen campaign P-23/P-24 calibration.
- Boredom currently covers stalled, physically grounded causal-test questions only. Independent geography/target coverage, verified threat-clear producers, and Stage-10/12 functionality remain incomplete; in the absence of a verifiable threat-clear input the threat profile deliberately does not exit merely because an alert vanishes.


## Stage-11 causal-test behavior diagnostic (public inputs only)

- Development runner: `python -m lab.stage11_hydration_probe` (public seed 41, 18 steps, known `small_water_gain` world).
- A distinct fixed public Stage-9 software control is executed with identical seed, original food-reward schedule, reference Equipment and physical water parameters. The runner rejects a mismatched reward schedule digest.
- Measured separately: proposal emissions, intrinsically evaluated options, actual applied causal-test commands and independent Memory-closed physically verified interventions. Neither proposals nor choices are counted as physical evidence.
- Both journals remain independent; test output records both head hashes and a canonical digest, with `scientific_verdict: null` and `golden_stage9_frozen: false`.
- The runner is a **development regression probe**, never a held-out campaign or a Stage-9 Golden. It does not settle P-48 calibration, coverage, the noisy-TV science criterion, INV-25 or independent Stage-9 acceptance.


## Verified development checkpoint: 2026-10-10

- Latest independently reexecuted **software test suite** for I0-vNext: 700 / 700 tests under Python 3.12, plus smoke, on commit `85685f353b30c8e43355c066d98b774e22b92445`, [CI #38090244262](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38090244262). This is not independent **scientific** verification and does not check the full Golden matrix.
- [English exact public diagnostic and limits](stage11-public-hydration-development-2026-10-10.en.md); [French summary](stage11-public-hydration-development-2026-10-10.fr.md).
- The fixed 18-step positive hydration fixture produced **3 applied I0-vNext test commands versus 0 in Stage 9**, **4 P-48-scored evaluations**, but **0 verified interventions**. All four test options had `equipment_input_unseen` and no test-specific published AgencyComparator evidence. Do not treat this as scientific intervention acceptance.
- Global Modulation P-23/P-24 and a partial P-48 Exploration producer are integrated; Stage 11 remains **IN_PROGRESS**. Full exploration target coverage, threat/recovery behavioral gates, independently grounded prospective test prediction, Stage 10, Stage 12 and scientific held-out review remain outstanding.

## Stage 11 controlled development results and Stage 10 formula foundation (11 October 2026)

- Software CI checkpoint: Python 3.12 quick suite **715/715 unit/integration tests passed** and three-cycle smoke check passed at commit `996778582b159ab633325ba14626c07567994214` ([run #38090942472](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38090942472)). No claim is made for exhaustive historical Golden or Python 3.11 here.
- The public `stage11-public-hydration-funnel-dev-v3` (seed 41, `small_water_gain`, 18 steps) confirms **2 applied causal-test drinks**, **2 closed physical action records**, **2 stagnant Exploration visits**, **no published P-47 test-specific comparisons**, and **0 accepted causal interventions**, while the Stage-9 control still executes 0 causal-test drinks. This is a reproducible development fixture, NOT a scientific held-out result.
- The optional read-only `LivedWaterPredictor` passed independent provenance/chronology software tests but produced **0 prospective forecasts** on that same 18-step public fixture, even with the predictor enabled. This null result is retained; the mode does not amend frozen Equipment, Causal Model, or scientific thresholds. Increased time horizons, alternative public-world opportunity schedules, and independent prospective prediction verification remain untested.
- P-48 now records physically executed exploratory actions as visits *even when no intervention is scientifically credited*, and suppresses stale intrinsic proposals after repeated stagnation. It does not count proposals, planning or rollbacks as learning evidence.
- Added a separately testable **Stage-10 formula-only foundation**: `src/i0/modules/sleep_pressure.py` and `tests/test_stage10_sleep_pressure.py`. It implements stateless DC-13 P-39/P-40 fatigue, consolidation/sleep pressure, and P-41 wake precedence, with explicit injected coefficients and no homeostatic-energy double counting. **It does not enter sleep, run consolidation, or install a new owner.** All numeric values in the tests are software fixtures, not calibrated science.
- **Next integration requirements:** Metacognition and Health must become the sole fatigue/sleep-pressure owner; freeze sleep pressure once at world-step opening; allow an ordinary `dormir` option with P-15/`m_a`; respect Action Control, reduced perception, and the maximum-sleep cap. Consolidation then requires cut-point ownership, transactional passes, interrupted resumption, coherent h/Q/κ/precision rebase, and atomic commit. These are not yet implemented or accepted.
- Branch and PR remain development-only and unmerged. Stage 9 scientific NO-GO and independent INV-25 held-out sign-offs are unchanged.
