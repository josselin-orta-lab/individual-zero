# Stage 11: local risk and physical reflex-capture correction (development v2)

**Recorded 2026-10-11 UTC+02, after failed diagnostic, before the next validation run.** This does not amend the normative English v1.2.1 specification, the original preregistered public development protocol, any Stage-9 evidence or the held-out NO-GO.

## Negative first pass preserved

- [GitHub Actions #38111815099](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38111815099), source `b9e9c627928c76bbf3032c4f75b61fc023217338`: the larger unit suite ran **753 tests with 3 failures**. The prior reference/hydration regressions did not appear among the failures. **This was not a passing CI result.**
- Two failures came from the observed creature layout: a successful reflex bypasses all cognitive cycles. Perception had a truthful initial capture, but Stage-11 Exploration's visit ledger updated only in its Phase-1 producer. A physically observed reflex-only site was missing from the ledger. The strict ledger-vs-Perception check correctly failed.
- The third failure was not an absent alert emission. The newly proposed local physical creature alert was retained with uncalibrated initial κ reliability 0.5; the reference Gatekeeper safety-preemption threshold is 0.8, so **no security-preempted S_t slot** existed. P-23 (§6.4) actually specifies a **retained risk alert** in S_t as input to modulation, not necessarily a reserved security-preempted slot. The test incorrectly demanded preemption.

## Versioned corrections (not threshold fitting)

1. A default-no-op step-open capture hook in the shared Stage-4 runtime preserves historical Stages 4–9. Stage-11 Exploration now records a real perceived location **before reflex dispatch/checkpoint**, and still designates all geographic targets through Phase-1 Planning. This preserves one real capture per step and allows a reflex-only step to count as a physically observed visit. It never counts a proposal, rollback movement, or uncaptured post-command destination as a new location.
2. Global Modulation still uses independently retained S_t; it now recognizes the narrow, source-typed, locally observed creature alert retained in S_t, even when ordinary κ calibration has not placed it into the reserved security slot. The **declared risk=1 is a local precautionary indicator only**. No κ reliability counter, Gatekeeper threshold, safety veto or scientific causal evidence is modified. Unknown/other risk sources cannot borrow this special identification.
3. The software diagnostic reports `local_risk_retained_st_steps` and `risk_preempted_st_steps` separately; it must never describe the former as actual Gatekeeper security preemption.
4. Changed journal event order and observation accounting require new public **software protocol IDs**: `stage11-public-local-modulation-dev-v2`, `stage11-public-frontier-coverage-dev-v2`, and `stage11-public-frontier-layout-robustness-dev-v2`. The older v1 diagnostic receipts are historical, not silently overwritten.

## Outcome requirements before declaring success

- **Trapped public creature:** verify a retained real local alert in S_t, threat profile entry, then phase-consistent exit after an externally logged creature-removal input, repeated complete local scans, hysteresis and distinct-world-step confirmations. Do not invent security preemption.
- **Body recovery:** verify an energy=20 state triggers a distinct-world-step recovery entry; an externally logged set_body(energy=80) at step 5 is subsequently perceived and permits exit. No internally chosen sleep/recovery action is credited.
- **Physical reflex traversal:** every physically perceived site, including a reflex-only step, belongs in the versioned geographic visit ledger. An unobserved final movement must not be credited as an additional site.
- **Multi-layout public controls:** obstacle, corridor, creature and known lethal; no visits to known lethal positions or occupied creature cells; provenance, exact replay and internally verified journals preserved.
- **No scientific acceptance:** no Stage-9 held-out, INV-25, Stage-9 Golden, generalized safety or new model calibration from these tiny public windows.

**Gate status prior to follow-up CI: NOT YET VERIFIED. Stage 11 remains IN PROGRESS.**
