# Exact death-truncated per-step projection: structural PASS, cost parity not reached

Protocol: [STAGE1_DEATH_TRUNCATED_PER_STEP.md](../../STAGE1_DEATH_TRUNCATED_PER_STEP.md),
frozen before implementation at `5fe2edb52f73e133178fbd77c579b2f9b6149c04`.

Baseline: `f2a541b2783261a02e65511ddfbb8a9aab070c57` (#1152).
Characterized source: `0c3dc70d1de64a3c62c5e60e7ac6e1392b0fd549`.
GitHub Actions run `42472935275`: Python 3.11 PASS, Python 3.12 PASS.

Software only: **no World, no life, no runtime projection mode, no adoption**.

Data summary: [summary.json](summary.json).

## Frozen verdict

`DEATH_TRUNCATED_PER_STEP_EXACT_PASS`

The candidate reproduces the existing 255-step per-step projection at
floating-point-noise scale while settling only the endpoints actually reached
before the first predicted vital zero.

The separate frozen cost-parity result is:

`candidate_f_cost_parity = false`

Therefore:

`runtime_candidate_authorized = false`

## Exactness

| Frozen check | Observed |
| --- | ---: |
| 486-case max option-value error | **2.22e-15** |
| 486-case max pairwise decision bias | **1.33e-15** |
| 486-case max final-body error | **0** |
| nonlinear-set max option-value error | **1.78e-15** |
| nonlinear-set max pairwise decision bias | **2.00e-15** |
| nonlinear-set max final-body error | **0** |

The candidate remains far below the frozen 1e-12 limits.

## Candidate-G parity on the frozen #1146 grid

The common forecast ceiling remains exactly the per-step ceiling:
18 cycles, 201 memory items and 1288 simulated steps per state. Early death is
not used to make the forecast body cheaper.

Observed decisions nevertheless reproduce the prior per-step arm exactly:

| Metric | Per-step #1149 | Death-truncated |
| --- | ---: | ---: |
| evaluated | 80 | **80** |
| selected epistemic | 32 | **32** |
| selected water-deficit | 8 | **8** |
| selected other-deficit | 24 | **24** |
| declined | 40 | **40** |

No actual-work/common-ceiling violation occurred.

## Actual work

All **400/400** projection calls reached predicted death before step 255.

- earliest predicted death: **46**;
- mean predicted death step: **168.06**;
- latest predicted death: **199**;
- actual paid projection steps: **67,224** total;
- mean paid projection steps per call: **168.06**.

Across the complete 80-state Candidate-G kernel:

| Work / bill | Mean | Max |
| --- | ---: | ---: |
| cycles | 18 | 18 |
| memory items | 201 | 201 |
| simulated steps | **853.3** | 1002 |
| energy | **2.1068** | 2.4042 |
| vigilance | **2.6066** | 2.904 |

Compared with the frozen #1149 per-step mean of 1288 simulated steps,
death truncation removes **434.7 steps/state**, about **33.8%**, without
changing decisions or projection values.

Compared with the frozen Candidate-F bill:

| Projection | Mean simulated steps | Energy | Vigilance | Selected |
| --- | ---: | ---: | ---: | ---: |
| Candidate-F | 470 | 1.3402 | 1.840 | 24 |
| per-step | 1288 | 2.9762 | 3.476 | 32 |
| death-truncated per-step | **853.3** | **2.1068** | **2.6066** | **32** |

The exact candidate is substantially cheaper than raw per-step, but still
roughly 1.57x Candidate-F's energy bill and 1.42x its vigilance bill.

## Interpretation

This result eliminates two false necessities:

1. exact projection does **not** require paying all 255 endpoints when death is
   predicted earlier;
2. exact projection does **not** require the large stored prefix cache rejected
   by #1152.

Irreversible mortality itself supplies an exact stopping boundary.

The remaining gap to Candidate-F is now much smaller and cleaner: approximately
383 simulated steps/state separate this exact candidate from Candidate-F's mean
470-step baseline. Memory is no longer the issue: the candidate is back at the
same 201 memory items as #1149.

## Next architecture question

Do not add a persistent cache yet.

The next smallest exact question is whether **identical or common prefixes of
the five projections evaluated inside one Candidate-G state** can be computed
once and reused before their projected bodies diverge.

This is different from the rejected full-trace cache:

- reuse is decision-local;
- only already-computed exact prefix state/reward accumulators are retained;
- no 255-element trace or prefix table is materialized;
- after divergence each branch advances independently per-step;
- predicted death still truncates each branch exactly.

First run a descriptive structural probe that measures the exact common-prefix
lengths and theoretical saved endpoint evaluations on the frozen #1146 calls.
Do not implement a new runtime representation unless that probe shows enough
reuse to plausibly close the remaining cost gap.

No World/life panel is authorized.
