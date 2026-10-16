# MVP v1.3.3 — migration, evidence and next scientific campaign

**Reference main SHA:** `0dee00823c3256223bb503d2a9eccd8cc0ac6408`. This file is an implementation handoff, **not** a claim of scientific acceptance.

## Requirement → code → verification → disposition

| Requirement | Component | Present change | Test / evidence | State |
|---|---|---|---|---|
| V133-MDL-01,02 | `src/i0/experimental/stage6_visible_delta_shadow.py` | Typed six-component output, explicit all-unknown hazard fields | `test_stage6_v133_shadow_contract.py`; A2.30 ZO/ZS | Experimental, software CI pending |
| V133-MDL-03 | `fit_external_lab_shadow` | External-only scope and corpus hash; rejects ingestive and terminal examples | Negative tests; original sealed ZS/ZT audits | Partial: complete source authentication belongs to external custody, not this API |
| V133-MDL-04 | same | OOD/unsupported/unstable/boundary/ineligible abstention | Negative tests; ZO 16/16 clamps | Experimental |
| V133-MDL-05 | isolated namespace | No imports from active planner/Action Control, no `predict` or `dispatch` | Structural test | Inactive by design |
| V133-MDL-06 | no live runtime change | No UC charged or claimed | PR diff; require future lives | Scientific untested |
| V133-MDL-07 | M11, Stage10/11 unchanged | No owner or snapshot migration | PR diff and #217 historical cross-stage run | Regression not rerun on this PR |
| V133-MDL-08 | next campaign protocol | Explicit separate approval gates | See below | NO-GO activation |
| V133-MDL-09,10 | normative bilingual spec | Exact version and preserved invariants | QA below | Operator review pending |

## Deliberate exclusions

The original research model in `scripts/run_stage12_issue110_b_a230zo_factorized_heldout.py` assumes precisely 16 training worlds and two action groups. The v1.3.3 shadow API is a **new, stricter software research candidate**, not the identical already-validated model and not a replication. It requires at least eight training examples per action, rejects terminal training, treats unstable deltas as unavailable, and never infers physical safety. These changes themselves require prospective evaluation. No change to `EquipmentPrediction`, `FrozenTableEquipment`, `SimulatorPlanner`, `WorldBody`, Stage9/DC-05, GA dual-scope, Action Control or M11.

## Next campaign pre-registration skeleton (not yet executed)

**H0:** relative to the exact model, factorized shadow predictions do not materially improve *valid* prospective partial numerical coverage once hidden intervention and distribution-shift errors and honest abstentions are scored. **H1:** shadow improves six-delta coverage in nominal contexts, while never issuing safety/terminal claims, with quantitatively acceptable errors under prospectively fixed thresholds. **Safety falsifier:** any `safe=True`, `terminal=False`, new unseen adjacency or postmortem lived evidence is an immediate NO-GO.

Freeze a new SHA, fresh training and heldout seeds/identities, scoring script and denominator before physics, then score paired noninterfering shadow/exact forecasts at times *strictly before* actual autonomous commands. Add distinct externally controlled lab hazard cohorts that expose the information-theoretic limits without training I0 with hidden truth. Collect matching controls, missed candidate actions, physical deaths, UC effects of any later opt-in cognition, and uncertainty from first-person evidence only. Use two Python versions only for code repeatability. Ensure independent artifact custody and a reviewer distinct from the physical producer. No adjustment of thresholds after looking at failures.

**Required decision record:** software tests PASS/FAIL, archived data quality, 6-delta error distribution, false-safety assertions, distinct source/heldout life counts, prospective temporal proof, complete journal/M11 provenance, cost and policy impact, autonomous behavior comparison, operator GO/INCONCLUSIVE/NO-GO. NO-GO is the standing deployment decision until authorized.

## Publication checklist

- [x] Historical specifications untouched.
- [x] Separate English normative and French informative v1.3.3 files.
- [x] Explicit isolated research predictor, no live wiring.
- [x] Adversarial software tests committed.
- [ ] Review actual PR CI on both Python 3.11/3.12.
- [ ] New independent preregistered scientific campaign.
- [ ] Explicit operator authorization for any autonomous activation.
