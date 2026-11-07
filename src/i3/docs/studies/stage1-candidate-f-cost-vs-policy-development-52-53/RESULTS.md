# Stage 1 Candidate-F cost versus policy: 52/53 execution result

**ENGINEERING FAILURE. PANEL INCOMPLETE. NO CAUSAL FALSIFIER VERDICT. NO RERUN.**

Prospective protocol: PR #1141. One-shot execution: PR #1142.

## Exact custody

- protocol merge/base: `d4ec51d772cbbf2a04130add099b5a7a0050b0f9`
- exact execution source: `e10365f605c6e919af1651a5c20f335ae6fd5f40`
- protocol SHA-256:
  `81a02daf0e18a98f31d044b11c4d62300e826ea60dbc16ac4eb40b8277373c47`
- source snapshot SHA-256:
  `023ce9a68a3828350cf9c742b1e36be47b839a0751878eae625dcf2bc6c1df98`
- Actions run: `42422888044`
- Py3.11 job: `128554911329`, PASS
- Py3.12 job: `128554911583`, PASS
- one-shot job: `128555252896`, execution step FAILED
- artifact: `13593974371`
- artifact digest:
  `sha256:385f01bf8bdad25cd83c5fa3ddd8be94d63109119e0c6b75356d8a0be0c3cbbf`
- immutable evidence commit:
  `60c5ae22c0b381865ec81678015c41efc1b9d975`
- evidence tree:
  `382f8a9aeb587045c8e27b2c7dfbcc10362d459c`
- archived files: **16**
- complete original lives archived: **12** (`life-00` through `life-11`)
- successfully reduced cases before failure: **11**

All available originals were archived despite the execution failure.

## Failure point

The failure occurs while reducing the twelfth original life:

`stable-53-g902:candidate_f_shadow_upper_cost_reference_controller_v1`.

That physical life itself completed normally:

- terminal: dead;
- lived steps: 286;
- death cause: zero water;
- upper-cost controller decisions: 286;
- candidate-private branch commits: 176;
- retained private branches: 18.

At step **177**:

- Candidate-F shadow work was physically paid:
  `cycles=3, memory_items=347, simulated_steps=0, replays=0`;
- the post-shadow body left plain P1.3 unable to fund its processing base;
- P1.3 therefore correctly returned `NO_PROCESSING_BUDGET`;
- P1.3 reference-choice work was exactly zero;
- total runtime decision work was exactly the paid shadow work;
- cumulative v2 settlement and the sequential audit agreed with gap 0;
- no motor action was admitted.

The Stage-0 revision receipt then raised:

`ValueError: processing status contradicts paid base block`.

## Root cause

This is an **observer contract mismatch**, not a controller billing mismatch.

`stage0_revision._resource_events` historically interprets the funding status
as a statement about the **entire decision-phase work vector**:

- `NO_PROCESSING_BUDGET` implies zero decision work;
- any other status implies at least the three-cycle P1.3 base block.

That contract was correct while one Mind owned the whole decision phase.

The upper-cost causal control deliberately has two sequential paid computations
inside one physical decision phase:

1. Candidate-F shadow cognition;
2. P1.3 decision cognition.

Its public funding status belongs to the P1.3 motor controller. Therefore
`NO_PROCESSING_BUDGET` means **P1.3 processing was not funded**, while earlier
shadow work may legitimately have been paid.

The original life proves exactly that configuration at step 177.

The revision endpoint's semantic question remains unchanged: whether the P1.3
actor paid its local processing block. It must therefore validate
`reference_choice_work` for this explicit upper-cost policy, while continuing
to validate total decision work for ordinary one-mind policies.

See [observer failure audit](POSTHOC_OBSERVER_FAILURE_AUDIT.md).

## Partial outcomes are not the preregistered result

Three complete matched blocks were reduced before failure:

- stable-52-g901: reference dead 308, Candidate-F dead 115, upper-cost dead 115;
- stable-52-g902: reference dead 115, Candidate-F dead 115, upper-cost dead 115;
- stable-53-g901: reference censored 400, Candidate-F dead 89, upper-cost dead 174.

For stable-53-g902, reference is censored at 400, Candidate-F dies at 89 and the
archived but unreduced upper-cost life dies at 286.

These partial stable-family observations do **not** evaluate the frozen
engineering continuation rule. Depletion and pulse were never generated, and
the protocol required all twelve matched blocks.

No causal, survival, mediation or Stage-1 conclusion is drawn from this partial
prefix.

## Allocation decision

**Do not rerun 52/53.**

The preregistration explicitly required stop-and-archive with no retry or
replacement. The 52/53 allocation is therefore closed for this mechanism,
including ungenerated remainder cases.

After the observer contract is corrected and software-tested against the exact
archived failure shape, any new diagnostic must use a separately frozen fresh
development allocation.

No selection, validation or reserve world was opened. The frozen ADR-0015 omega
gate remains failed. P1.3 remains reference and I3 remains unregistered.
