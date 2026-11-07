# Stage 1 cost-reduced local information: frozen development diagnostic

Status before execution: **PROSPECTIVE DEVELOPMENT ONLY, NOT A SCIENTIFIC GATE.**

Continues issue #1061 after exact-cost PRs #1071-#1074. Runtime baseline before
this protocol and before any new world exposure:
`3b09edfcc369059ea8e706d89ed8415ecfc31ff5`.

The earlier Stage-1 development panel at indices 44/45 is immutable and is not
rerun, replayed for tuning, or used to choose cases below.

## Question

Does the previously observed funding collapse, specifically the transition from
`NO_FUNDED_SCORE` to prolonged `NO_PROCESSING_BUDGET`, persist after removing
only exact duplicate computation while preserving the conservative common
forecast body?

This is an engineering-development question. The candidate still differs from
P1.3 in repertoire, stationary ignorance prior and episodic partition, so this
panel cannot isolate information value, establish non-inferiority, demonstrate
generalization, or promote I3.

## Frozen new cases

Use exactly the three existing P2 F0 ecologies: `stable`, `depletion`, `pulse`.

Use development indices **46 and 47 only**, corresponding to P2 development
world seeds **2046 and 2047**. Repository allocation history before this freeze
places P5b at 20-25, P5c at 26-31, P5d at 32-37, P5e at 38-43, and the first
Stage-1 diagnostic at 44/45. Stage-0 already identifies development 44-49 as its
design envelope. No current I3 allocation was found for 46/47 before this freeze.

Use G0 genome seeds **901 and 902**, with no selection or tuning.

For zero-based family ordinal f, world ordinal w and genome ordinal g:

`life_seed = 7410000 + 1000*f + 10*w + g`.

Each pair receives the same family, world, genome, life seed and horizon. Pair
policies are `reference` then `local_information_v1`.

Fixed order: family, index, genome, policy.

Total: **12 matched pairs / 24 lives**, horizon **400**, maximum **9600 physical
steps**. Two G0 genotypes are not independent populations.

No selection, validation or reserve world is opened. P4 reserve
1200000..1200199 stays sealed.

Machine-readable runner:
`python -m i3.lab.stage1_cost_reduced_diagnostic --plan`.

Canonical plan SHA-256:
`d9d8145db42c28108bcf5e3593a4957b7ec86152d89d991be89c4767fdca1025`.

No retry, replacement seed, sequential favorable stopping, horizon extension,
individual reset, forced resource, clone or resurrection.

## Prespecified observations

Preserve every complete original trace, funding phase, resource sidecar,
Competition witness and decision diagnostic before reduction.

For every life report:

- physical death/censoring and lived steps;
- actual paid cognition by phase and per lived step;
- physical inactivity separately from chosen waiting and sleep;
- every funding status;
- first funding failure;
- first `NO_PROCESSING_BUDGET` step;
- whether any later `FUNDED` decision occurs after that first processing failure;
- longest consecutive unfunded run;
- positive water/food uptake and first positive water step;
- collection/consumption and personally mapped cells;
- paid information-option count, positive information increments > 1e-12, and
  fully empirically supported options;
- Stage-0 revision receipt, keeping `NO_EXPOSURE`,
  `EXPOSED_NO_REACQUISITION` and `REACQUIRED` distinct.

A positive information increment is descriptive arithmetic only, not a
behavioral-benefit test.

## Frozen engineering continuation rule

For the candidate aggregate only:

`inactive_fraction <= 0.50 AND positive_water_uptakes > 0`.

If true, record only that the **previous computational-paralysis bottleneck is
no longer dominant on this bounded panel**. It does not make Stage 1 pass.

If false, retain cost sustainability as the immediate blocker. Because measured
remaining dominant work after #1074 is unique rollout computation, further
reduction must be treated as a Stage-2/value-of-computation policy question,
not disguised as another transparent optimization.

The rule is not a survival endpoint and is not applied to the reference arm.

## Execution and custody

Full exact-head I3 software checks under Python 3.11 and 3.12 must pass first.

A temporary one-shot job may execute only on the initial `opened` event, first
attempt, same repository, exact branch
`i3/stage1-cost-reduced-development-20261107`, and exact baseline above.
The runner rejects the wrong source SHA, wrong protocol digest, dirty I3 source,
or any candidate/runtime/world/physics/receipt change relative to the frozen
baseline.

Archive each original gzip before reduction. Upload all originals as an Actions
artifact even on partial engineering failure. The archive step may create only
a new evidence branch parented by the exact execution source, under
`src/i3/docs/studies/stage1-cost-reduced-development/original/`.

A crash is an engineering failure, never a physical death. Completed originals
remain publishable. No scientific GO, activation, selection, validation or
reserve exposure follows from this diagnostic.
