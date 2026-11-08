# Exact separable cache accounting: funded, but too expensive to advance

Protocol: [STAGE1_SEPARABLE_CACHE_ACCOUNTING.md](../../STAGE1_SEPARABLE_CACHE_ACCOUNTING.md),
frozen before implementation at `7ae02075d710c622854de696c7dff2ce3d8b8add`.
Baseline: `ebc9d1894e67ac56f9e6a88f5e4bbbb26cc61cbc` (#1151).

Characterized source: `fddf08637651f7e1b5f0cf5577e3415ca4edf2e5`.
GitHub Actions run `42472340815`: Python 3.11 PASS, Python 3.12 PASS.

Software only: **no World, no life, no runtime projection mode, no adoption**.

Data summary: [summary.json](summary.json).

## Frozen classification

`CACHE_ACCOUNTING_ROBUSTLY_FUNDED`

Both the optimistic and conservative accounting arms can pre-fund and complete
all 80 frozen #1146 states. Therefore the yes/no funding result does **not**
depend on choosing the favorable compute tariff.

However the separate frozen runtime-advance rule is **false**:

`conservative_runtime_candidate_authorized = false`

The cache is fundable on these isolated states, but its mean physical bill is
far above the already-rejected Candidate-F projection.

## Results

| Metric | bundle5 lower bound | scalar1 upper bound |
| --- | ---: | ---: |
| completed states | **80/80** | **80/80** |
| selected epistemic | **32** | **39** |
| selected water-deficit | 8 | 16 |
| declined | 40 | 41 |
| mean simulated steps | 1191.1 | 5903.5 |
| mean memory items | **24,584.5** | **24,584.5** |
| mean cycles | 23 | 23 |
| mean energy bill | **7.7591** | **17.1839** |
| mean vigilance bill | **3.5322** | **12.9570** |
| max energy bill | 8.0372 | 17.8292 |
| max vigilance bill | 3.6240 | 13.4160 |
| trace builds | 1848 | 1848 |
| trace hits | 152 | 152 |
| hit fraction | 7.6% | 7.6% |

No actual-work/common-ceiling violation occurred.

The complete no-hit common ceiling is 23 cycles, 26,551 memory items and:

- 1,288 simulated steps for `bundle5_lower`;
- 6,388 simulated steps for `scalar1_upper`.

The direct exactness guard remains within the frozen 1e-10 tolerance in both
arms: max value error `1.1368683772161603e-13`, final-body error 0.

## Comparison with #1149

Frozen #1149 mean work bills on the same grid:

| projection | selected epistemic | energy | vigilance |
| --- | ---: | ---: | ---: |
| P1.3 reference | 1 | 0.5062 | 1.006 |
| Candidate-F | 24 | 1.3402 | 1.840 |
| per-step | 32 | 2.9762 | 3.476 |
| exact cache, bundle5 | 32 | **7.7591** | **3.5322** |
| exact cache, scalar1 | 39 | **17.1839** | **12.9570** |

The lower arm exactly retains the 32/80 per-step decision-relevance count, but
uses about 5.8x Candidate-F's mean energy bill and 1.9x its vigilance bill.
The conservative arm is still more expensive.

The strict arm selecting 39 rather than 32 is not evidence of better epistemic
reasoning. Its much larger common cognitive bill changes the forecast body
before options are compared. Cost is part of the state and can therefore change
the decision surface.

## What was learned

The ambiguity identified after #1151 is no longer the central obstacle:

- **compute-price ambiguity does not decide funding** on this grid: both bounds
  fund all 80 states;
- **exactness is not the problem**: the cache remains exact;
- **trace storage is the dominant engineering cost**.

Each fresh exact trace stores 1,035 charged memory items. Across the 80 states,
1,848 traces are built but only 152 later accesses hit an existing trace
(7.6%). The representation pays to retain 255 levels plus three 255-element
discounted prefix arrays even though most traces are never reused.

That is a poor physical trade: the cache saves recomputation for a small number
of hits by materializing a large exact prefix table for every miss.

## Decision

Do **not** integrate this full stored-trace cache into Candidate-G or runtime.
Do not choose `bundle5_lower` after exposure merely because it is cheaper.

The next architecture question is now narrower and better defined:

**Can exact trace reuse keep only sparse checkpoints and recompute the short
residual segment on demand, so memory falls by an order of magnitude without
reintroducing projection bias?**

This is not the rejected #1150 anchored-chunk approximation. Checkpoints would
store exact per-step prefix values; any gap used by a query would be recomputed
per-step exactly. Checkpoint spacing changes cost only, never projected value.

Freeze that representation before code. No World/life panel is authorized.
