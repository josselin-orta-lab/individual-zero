# Stage 9: local behavioral development diagnostic (10 October 2026)

**Classification: DEVELOPMENT OBSERVATION / REPRODUCIBLE SOFTWARE DIAGNOSTIC, NOT SCIENTIFIC ACCEPTANCE.** This record is neither a prospectively registered scientific EXP nor a held-out campaign, an independent scientific validation, INV-25 closure, a Stage-9 GO, or a Golden. The normative source remains `docs/architecture/reference/en/mvp-specification-v1.2.1.md` (especially §§8.5, 13.2–13.4, 14, 20.3 Stage 9). No normative thresholds have been derived from this checkpoint.

[Version française](stage9-development-behavior-2026-10-10.fr.md).

**Observer quickstart (French):** [minimal local diagnostic reproduction guide](stage9-behavioral-test-quickstart.fr.md).


## Question and provenance

**Question:** In the integrated Stage-9 development fixture, does the individual form a causal hypothesis from lived effects of drinking, produce testing options, and then actually select and execute a verified intervention?

1. **Local user-reported execution (2026-10-10):** A contributor ran the existing diagnostic on Arch Linux (`x86_64`, kernel `6.8.12-30-pve`, Proxmox LXC), using a `Python 3.12.15` virtual environment, an editable installation, and a `main` checkout reportedly aligned with `origin/main`. Two terminal summaries were provided in the project conversation and preserved as a [literal transcription of the provided excerpts](evidence/stage9-development-behavior-2026-10-10-local-terminal.txt). The *exact local* 40-character HEAD SHA, original `results.txt` bytes, local journal, machine-generated SHA-256 and independently witnessed execution time were **not provided**. The remote `main` tip when this documentation was prepared was [`85a5280e08dc97ed91334036ebb1d797762214cb`](https://github.com/josselin-orta-lab/individual-zero/commit/85a5280e08dc97ed91334036ebb1d797762214cb); this is **not** proof of the local checkout SHA.
2. **Separate previously archived CI diagnostic:** [Successful GitHub Actions run #38067542568](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38067542568), job [#114258148176](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38067542568/job/114258148176), on Stage-9 source commit `96abfa089fd52f12b7e35c334289088583645125` (before squash integration into main). The CI log contains the complete `stage9_hydration_contrast=` JSON record; its parsed machine fields are preserved in [this CI report](evidence/stage9-development-behavior-2026-10-10-ci-report.json). This is a copied and pretty-printed **CI** report, not a raw local capture. Its internally recorded `evidence_sha256` concerns the diagnostic payload; it does not authenticate the local execution.
3. **Field-level comparison:** All eight user-reported summaries agree with the corresponding CI rows for their reported status, counts and diagnostic reasons. This independently corroborates the reported metrics across executions of the same *development fixture*, but does not establish an independently protected scientific dataset or guarantee identical executable bytes across machines.

### Reproduction (public development seeds only)

~~~bash
# Run from the checked-out repository with Python 3.12 and the project installed.
mkdir -p artifacts/stage9-behavior-dev
git rev-parse HEAD
python -m lab.stage9_hydration_contrast_report > artifacts/stage9-behavior-dev/results.txt
sha256sum artifacts/stage9-behavior-dev/results.txt
~~~

Protocol `stage9-hydration-contrast-diagnostic-v1`; `seeds=(41, 42)` and `steps=18` by default; eight world/seed cases. The command does not expose or use any independently held-out worlds/seeds. The CI JSON is already retained in Git so its values can be audited even if the original workflow artifacts expire.

## Observed measurements

| Seed | World | Published status | Proposals | Accepted registrations | Unevaluated | Accessible contexts | Test drinks applied |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 41 | `null_water_reference` | `aucun` | N/R | N/R | N/R | N/R | N/R |
| 41 | `small_water_gain` | `hypothese_causale` | 37 | 37 | 37 | 9 | 0 |
| 41 | `recurrent_water_need` | `hypothese_causale` | 44 | 44 | 44 | 13 | 0 |
| 41 | `model_aligned_water_gain` | `aucun` | 0 | 0 | 0 | 0 | 0 |
| 42 | `null_water_reference` | `aucun` | N/R | N/R | N/R | N/R | N/R |
| 42 | `small_water_gain` | `hypothese_causale` | 39 | 39 | 39 | 9 | 0 |
| 42 | `recurrent_water_need` | `hypothese_causale` | 43 | 43 | 43 | 13 | 0 |
| 42 | `model_aligned_water_gain` | `aucun` | 0 | 0 | 0 | 0 | 0 |

- In each of the four **positive, hypothesis-producing** cases (`small_water_gain` and `recurrent_water_need` at both seeds), the published causal status was `hypothese_causale`.
- Total across those four cases: **163 proposal emissions**, **163 accepted candidate registrations**, **163 `not_evaluated` evaluations**, and **44 development-fixture moments in which the water source was accessible and water was below saturation**. Each case repeatedly emitted **one distinct option**, so these are not 163 independent candidate designs, tests, or interventions.
- **Zero proposed causal-test drinks executed, zero published physical interventions, and zero post-hypothesis drinks** across those four cases. All 163 proposal predictions were marked `equipment_input_unseen`; the observed `causal_test_planning_outcomes` was an empty list, not evidence of successful downstream choice.
- In the two `null_water_reference` controls, the reported status was `aucun` and no positive water effect was observed. The diagnostic deliberately reports several causal-test fields as **null** for these controls; “N/R” above means **not reported / not applicable**, not measured zero.
- In the two `model_aligned_water_gain` cells, status was `aucun` with `insufficient_positive_closed_episodes`. This is insufficient evidence, not a causal-learning failure verdict.
- The `recurrent_water_need` world changes both the water gain and decay. It is exploratory, **not** a single-variable controlled contrast against the null.

The full CI report also records `acceptance_status: open` and `golden_stage9_frozen: false`. Neither this copy nor the local reproduction changes those flags.

## Mechanistic diagnosis (code inspection, not an observed hidden mental state)

The world observation, episodic evidence, hypothesis publication and formation/registration of one-step `boire` test candidates are functional for the reported development cases. `equipment_input_unseen` is a missing exact-table Equipment prediction, **not by itself a veto**: `assess_executable_causal_test` can still issue a physically grounded unpredicted proposal. See [causal test planning](../../src/i0/modules/causal_test_planning.py).

However, `Stage9OptionEvaluator` deliberately marks test-causal options `not_evaluated` with no intrinsic motivational value, rather than inventing one. The normative Exploration component is responsible for intrinsic interest of causal tests (§§8.5, 13.4, 14; parameter P-48 in **Stage 11**). Therefore the zero executions in this reference implementation are consistent with an explicitly incomplete autonomous test-selection path. An Equipment coverage-only improvement would not resolve that missing intrinsic evaluation.

**Supported conclusion:** the available development diagnostic demonstrates hypothesis publication and option registration in specified known fixtures; it **does not demonstrate** autonomous intervention selection, complete causal learning, robustness on unseen worlds, superstitious-rule-rate acceptance or independent INV-25 compliance.

## Evidence quality and next action

- Preserve the linked original CI run, the CI JSON and the local excerpts **without promoting them to a held-out result**. The saved local excerpts are user-reported, not independently certified raw artifacts.
- To strengthen this local record, the operator may later supply the exact `git rev-parse HEAD`, unaltered `results.txt`, its `sha256sum`, raw journal and causal owner states, an exact time and an environment manifest. Any additional evidence must be dated when received and not backfilled as if present on 2026-10-10.
- Follow up in **development** with a focused option-evaluation/Competition diagnostic and ultimately a correctly implemented normative Exploration component. Do not inject false intrinsic values or bypass admissibility merely to obtain an intervention count.
- The separate [Stage-9 held-out prelaunch NO-GO record](stage9-heldout-prelaunch-decision-record.md), [English independent evaluation manual](stage9-independent-heldout-evaluation-manual.en.md) and [French manual](stage9-independent-heldout-evaluation-manual.fr.md) still govern any formal scientific campaign.
