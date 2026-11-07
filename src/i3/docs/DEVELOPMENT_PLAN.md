# I3: approved development path and generalization scenario

Current direction accepted by the owner on **6 November 2026**, through the
request to integrate the supplied scenario. This is the continuation of
[#1002](https://github.com/josselin-orta-lab/individual-zero/issues/1002) and
[#1026](https://github.com/josselin-orta-lab/individual-zero/issues/1026), not a
second roadmap. Decision: [ADR-0016](../../../docs/decisions/ADR-0016-i3-generalization-without-imposed-rules.md).
Integration tracking: [#1059](https://github.com/josselin-orta-lab/individual-zero/issues/1059).

**Current operational intervention: finish Stage 1 only after supplying the
smallest first-person representation of future matching opportunities that its
information calculation demonstrably needs. Stage 0 remains open; Stage 2 stays
blocked. Do not start with a Competition rewrite.** This is an evidence-driven
dependency refinement from the 7 November engineering results, not a rewrite of
the owner-supplied scenario or permission to launch full Stage 3.

## Source, scope and current reference

The [owner-supplied French report](GENERALIZATION_SCENARIO_SOURCE_2026-11-06.md)
is preserved byte-for-byte: 22,291 bytes; SHA-256
`e3a282e839c597cd610682fecb852340dd30f96ea8038874bebd2367b0a8753c`;
Git blob `934601a9258a8c5373512764a10709aa1859883a`.
Its baseline is `e4eb3e80c9dc48e131e05383d952909bd86213b7` (PR #1058).
The report's literature references and additional P5e interpretation remain
attributed to that report; this integration is not an independent reproduction
of its post-hoc analysis or a literature review. Its dated statements about
`main` are snapshots, not future live branch state.

The [pre-integration plan](DEVELOPMENT_PLAN_BEFORE_GENERALIZATION_2026-11-06.md),
[status ledger](STATUS_BEFORE_GENERALIZATION_2026-11-06.md) and
[documentation ledger](README_BEFORE_GENERALIZATION_2026-11-06.md) retain their
original bytes and original relative links. Their old "next" instructions are
historical; use this file for current priorities and [STATUS.md](STATUS.md)
for implemented/observed status. Original studies and their gates are unchanged.

The reference is P1.3 on the funded v2 substrate, adopted under ADR-0015.
P1.2 remains rejected under its original gate. P3/P4/P5 results remain bounded,
with four historical independent genetic populations, no demonstrated general
lineage advantage, and no general scientific GO. In particular, P5e's 333/342
non-top meal scores are **not** 333 Competition reversals. Its masked-curiosity
arm had no food-carrying decisions; it does not explain P5d's non-consumption
with food carried. See [P5e original results](P5E_DEVELOPMENT_RESULTS.md) and
[P5d original-only analysis](P5D_POSTHOC_COLLECTION_CONSUMPTION.md).

## Governing principle: predicted viability in one unit

Every new cognitive mechanism must contribute to the individual's predicted
**cumulative distress over its own bodily channels**, including the energy and
vigilance costs of performing that cognition. Information, inference, memory,
planning and further computation must be evaluated through those stakes, not
through an independent bonus designed to obtain a desired action.

Generic, renaming-invariant inherited parameters selected only by individual
persistence remain admissible under [ADR-0014](../../../docs/decisions/ADR-0014-i3-lignee-enjeu-de-soi.md).
No scripted drinking/eating/exploration, family-specific policy, reward shaping,
hidden-world oracle, inherited memories/maps/learned weights, postmortem work,
resurrection or old-generation runtime dependency. The generation's motor
authority, irreversible mortality and actual prepaid cognition remain intact.
I1 stays active; I3 stays unregistered; the registry is not changed.

This is a research constraint on developers, never an instruction supplied to
the living individual's mind. A poor choice or death is not automatically a
software defect. Keep adverse and null outcomes; do not tune them away.

## Ordered stages and dependencies

| Stage | Deliverable | Status / tracking |
| --- | --- | --- |
| 0 | Independent-population design, energetic mediation, complete paid Competition observation, individuality challenge, P5d uncertainty | Open in parallel; [#1060](https://github.com/josselin-orta-lab/individual-zero/issues/1060), existing #1026/#1054 |
| 1 | Information value in predicted distress, replacing additive curiosity/relevance/prudence | Engineering in progress; arithmetic works, but decision impact is blocked by sparse future-opportunity representation; [#1061](https://github.com/josselin-orta-lab/individual-zero/issues/1061) |
| 2 | Decide how much to think by value of computation | **Blocked** until Stage-1 decision boundary is resolved; [#1062](https://github.com/josselin-orta-lab/individual-zero/issues/1062) |
| 3 | Change detection, latent causes, then perceived-attribute factorization | Full stage deferred. One minimal generic future-opportunity representation may be tested early only as a Stage-1 prerequisite; do not start the Stage-3 bundle. |
| 4 | Successor features and delayed credit evaluated by current bodily distress | Deferred after the required model/budget decisions |
| 5 | Learned topology for obstacles and larger F1 worlds | Deferred; unchanged perception radius |
| 6 | Multi-family selection of generic learning dispositions | Deferred; independent lineages and random-parent control |
| Audit | Competition thresholds and physically justified switching cost | Low-priority transversal work, not the critical path |

A dependency requires an explicit result and reference decision, not an
obligation to obtain a positive result. If a gate fails, retain its previous
reference and record the failure; do not silently promote a failed mechanism
or launch all later stages as one architecture rewrite.

### Stage 0: make the experiments capable of answering the questions

Before new confirmatory comparisons, design at least **eight genuinely
independent genetic populations**; extra genomes/lives from the old four do
not increase that number. Freeze lineage sampling, genome selection, ecological
blocks, horizon, stopping rule, uncertainty method, multiplicity and compute
ceiling. Eight is a minimum design requirement, not a power guarantee.

Predeclare actual phase-specific cognition, energy/vigilance expenditure,
inactive-step fraction and lived time. Equal initial opportunities under
[P2](P2_EXIT_EQUAL_OPPORTUNITY.md) do not imply equal realized work; never bill
unperformed work to manufacture parity. Separate total treatment effects from
energetic mediation and do not condition away adverse short lives.

Reuse P5e's full already-paid Competition witness as the standard observer-side
instrument for new diagnostic studies, with on/off parity of actions, RNG,
body/world, paid work and original evidence chain. It provides no extra Mind
input. This plan does not enable a new default observer or rerun a study.

Keep the acquired-individuality question under
[#1026](https://github.com/josselin-orta-lab/individual-zero/issues/1026): same
genome, different histories, then a new prospectively common challenge. Final
memory hashes alone are insufficient. Define behavioral stability, challenge
exposure and bodily mediation without resetting a living body or memory,
cloning an experienced individual or excluding deaths before the challenge.

Keep P5d under [#1054](https://github.com/josselin-orta-lab/individual-zero/issues/1054):
why were none of 125 paid carried-food opportunities selected without scored
curiosity? Full original scores were not recorded. P5e's zero carried-food
exposure in that arm leaves the question **NOT_OBSERVED**, not resolved.
Design a bounded development-only witness with prospectively specified
exposure conditions; do not force a meal, inject food into a living state,
search favorable seeds or reinterpret the normal P5e arm as the missing arm.

### Stage 1: information value in the unit of the individual's stakes

For an exploratory option or unknown food, average over outcomes supported by
the individual's own beliefs, replan, and estimate how the information would
reduce predicted cumulative distress. Begin with the report's **two or three
actually executed and paid branches**. Include their bodily cost. Replace,
rather than stack on, additive `beta_u`, relevance and prudence. Urgency comes
from bodily projection; risk comes from predicted integrity-effect uncertainty.

Gate: survival non-inferiority and improved revision latency in a prospectively
defined fresh **family R**. Controls: frozen projection and information value
without cost, with exact semantics fixed before exposure. The report's expected
survival decrease and expenditure increase are hypotheses that may fail, not
acceptance targets to engineer. Specify generic priors, unknown outcomes,
zero-budget paths, source/genome versioning and real branch receipts in #1061.
Do not silently migrate an existing individual's genome or retain learned
state at a new birth.


#### Observed Stage-1 structural dependency, 7 November 2026

The implemented information arithmetic is no longer the primary unknown. Three
software results expose a narrower dependency in the current P1.3 substrate:

- **#1099:** without a represented future matching action opportunity, immediate
  post-trial bodily observation produced zero information value across 160
  pairwise multi-deficit states;
- **#1101:** when exact P1.3 explorer-prefix semantics were restored, the water
  mechanism retained positive information but selected an epistemic trial in
  0/80 realistic states;
- **#1105:** carried-food information under one common cognition-depleted
  forecast body was funded in 27/27 rich competing-need states, was positive in
  9/27 and raised the meal score in 14/27, yet changed the raw winner in 0/27.

Together these results show that information value can be computed, can survive
its own v2 cost, and can move an option's score, while still remaining
sub-decisive because P1.3 represents too little reusable future-opportunity
structure. More water/food score patches would therefore be local tuning rather
than a test of the general mechanism.

The next admissible prerequisite is **not full Stage 3**. It is one minimal,
generic, first-person representation of future matching opportunities, empty at
birth and learned only from personal observations. It must be renaming
invariant, paid, bounded to the Stage-1 two/three-branch envelope, and must not
assume hidden source stock, current-source persistence, schedules, world family,
or favorable outcomes. Its only purpose is to let Stage 1 ask whether learned
effect information could matter again later.

If that minimal representation does not make information decision-relevant,
retain the negative result and reconsider the architecture. Do not jump to
Stage 2, change Competition, or add an exploration bonus.

### Stage 2: decide how much to think

Execute another computation only when its expected viability gain exceeds
its cost expressed through the same distress function D, subject to physical
funding. `n_base` and `h_max` become ceilings, not instructions. Replay is
another priced computation; metareasoning itself must also be paid and bounded.

Compare survival and inactive-step fraction against a fixed budget. Include
zero-cost and equal-mean random-budget controls. Determine any matching mean
from development, never from future validation trajectories. Freeze exact
interventions, margins, receipts and stopping rules in #1062; no free evaluator
or omniscient estimate of the value of the next computation.

### Stage 3: generalization and change in the world model

Follow the report's **revised priority order**: online change detection, latent
causes, then factorized effects over generic perceived attributes with shared
priors. These are three separate mechanisms and gates, not a bundled rewrite.
Change probability can inform Stage-1 information value. Revision latency is
a gate observable. Test transfer to a previously unseen token sharing perceived
attributes with personally experienced toxicity, and include frozen-change
controls. The attributes must be sensed, not hidden toxicity labels, future
schedules or designer-coded action advice. No new sensor is silently granted.

### Stage 4: reusable value as needs change

Learn successor features over predicted bodily-channel changes and evaluate
them through **current** D. Test delayed credit with toxicity delayed by 20-50
steps and repeat the P5a value ablation on fresh, preregistered conditions.
The report hypothesizes that removing learned values should now reduce
survival. A null or adverse result must remain publishable; no tuning on the
opened gate to make the learned-value mechanism appear necessary.

### Stage 5: topology, obstacles and larger worlds

Allow adjacent impassable boundaries/walls to be perceived as such, learn a
topological map within the life, and plan within Stage-2 funding. Keep the
perception radius unchanged and prohibit inherited or hidden complete maps.
Gate: held-out family F1. Comparator: the current frontier mechanism. Freeze
the physical/sensory contract before exposure; new test substrate is distinct
from a designer-written detour or survival policy.

### Stage 6: select ways of learning, not inherited experience

Use at least eight independent populations and ten generations, recombination,
random-parent controls and multiple world families. Select generic learning
dispositions only by individual persistence; never transmit learned weights,
values, memories, maps or bodily state. Repeat P4a on new conditions and include
a learning-disabled control with explicit actual-cost semantics.

Retain the source's proposed **at least 7/8 populations with a selected-arm
advantage** as a directional gate for an eight-population design. Do not equate
it with statistical significance. The protocol must specify the gate for a
larger population count, uncertainty and multiplicity before running it.

### Low-priority transversal audit: Competition

The original P5e cohort shows six threshold-related meal-order differences
among 342 opportunities, not a generally defective Competition. A later bounded
gate may compare best predicted gain with continuity justified by a predicted
switching cost, without survival loss. Do not rewrite Competition to force
eating or promote this audit ahead of Stages 0-2.

The source mentions removing prudence both here and in Stage 1. Operationally,
Stage 1 owns that replacement; the later audit checks the resulting status,
not a second independent removal. An integrity veto can remain only if its
physical-body justification is established. Merely renaming an arbitrary
cognitive threshold a physical law is not a correction; no veto is changed here.

## World-family progression and generalization

The report supplies the following **prospective family contracts**, not already
implemented generators. Freeze mechanisms, parameter distributions, seeds and
allocation before evaluation. New F0 seeds are not a new ecological family.
Selection and validation must include whole-family separation for transfer
claims, not only disjoint seeds from one mechanism.

| Family | Novelty from the source | Target |
| --- | --- | --- |
| F0 | Existing stable, depletion and pulse ecologies | Current baseline |
| F1 | Obstacles, movement-cost terrain, maps 2-4 times larger | Stage-5 topology |
| F2 | Seasonal periodic sources | Stage-3 change/latent causes |
| F3 | Hidden delayed toxicity and shared perceived token attributes | Stage-3 transfer and Stage-4 credit |
| F4 | Moving danger zones damaging integrity | Cross-channel tradeoffs and risky information |
| F5 | Inventory as a transportable reserve | Long-horizon planning |
| F6 | Other competing I3 individuals | **Out of current scope** |

F5 proposes a new reserve-planning ecology, not the claim that current I3 lacks
an inventory. F2 must be distinguished prospectively from existing F0 pulses;
renaming an existing generator is not held-out mechanistic generalization.
Progressive generation is a proposal only, with no post-exposure retuning.

Primary endpoint: survival at a fixed horizon. Secondary endpoints: revision
latency, first drink and cognitive expenditure per lived step, with censoring,
no-exposure and death rules preregistered. Probes remain descriptive until
real cost comparability is established; the oracle is not a paid upper bound.

## Prospective gate discipline

One targeted change per gate. Use selected genomes under
[ADR-0015](../../../docs/decisions/ADR-0015-i3-portes-sous-selection.md), a frozen
source SHA and disjoint development, selection, validation and reserve manifests.
New validation allocations must be previously unopened **indices >=120**, also
checked against all earlier allocations and new-family namespaces. The original
P4 reserve **1200000..1200199 stays sealed**. A numerical lower bound is not a
license to reuse a world. No new study is authorized by this documentation.

Before exposure, freeze hypothesis, falsifier, primary contrast, practical
margins, exact independent unit, source/genome identifiers, worlds, horizon,
compute limit, missing/crashed lives, censoring, multiplicity and stopping rule.
Publish all negative/null lives, actual costs and an explicit verdict. A green
software check is not a scientific GO. Do not repeatedly run exposed validation
worlds while adjusting genes, tariffs, policy or thresholds.

## Explicit operational clarifications, separate from the source

- **Statistical resolution:** for an exact two-sided sign test with eight
  non-tied independent signs, 8/8 positive gives `2/2**8 = 0.0078125`, while
  7/8 gives `2*(8+1)/2**8 = 0.0703125`. This does not establish prospective
  power, remove multiplicity or characterize every possible statistical test.
  The source's Stage-6 directional threshold remains separate from inference.
- **Family R is undefined in the supplied scenario:** freeze its mechanism,
  first-person change evidence and latency definition before the Stage-1 gate.
  Do not silently identify it with F2, an old G2e cohort or a favorable fixture.
- **Zero-cost controls are underspecified:** distinguish zero perceived cost
  with actual physical payment from physically waived charges. The latter is
  an explicitly non-admissible diagnostic economy, never the funded reference.
  The protocol must resolve this choice rather than claim unpaid cognition is
  ordinary v2 behavior.
- **Not-yet-observed results stay unknown:** source-derived post-hoc P5e
  interpretation does not explain P5d, prove harmless lifelong meal deferral,
  demonstrate individuality, or establish the benefit of any future stage.

## Verification and next handoff

For this integration: documentation and issue coordination only, no runtime,
world, genome, tariff, registry, workflow or original study changes; zero new
study lives. Verify the exact PR diff and the four preserved source/ledger blobs.
Run `python tools/check_repo_navigation.py --scope entrypoints` in a full
checkout and mandatory CI on the exact candidate SHA. If unavailable locally,
report `NOT_RUN`; never borrow a prior PR's green status.

Future code work follows [TEST_PLAN.md](TEST_PLAN.md), focused I3 tests and
relevant generation guards. Record `question | baseline SHA | one change |
falsifier | control | observed data | costs | exact checks | verdict | next
issue`. Start with #1060. Do not use this scenario as a reason to multiply
frameworks, review gates or synthetic tests that add no scientific information.
