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
