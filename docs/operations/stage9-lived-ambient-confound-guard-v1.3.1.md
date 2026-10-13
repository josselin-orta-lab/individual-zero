# Stage 9 development note: first-person ambient injury control

**Status:** software correction proposed; Stage 9 remains **NO-GO** and
requires independent scientific verification and operator approval.

**Base dependency:** [PR #77](https://github.com/josselin-orta-lab/individual-zero/pull/77)
redacts the simulator's hidden damage-source fields from autobiographical
transition effects while retaining the complete append-only technical journal.

## Failure previously possible

The Stage-9 `ingest_closed_autobiographical_episode` code took a decrease
in integrity after eating as direct DC-05 toxic-food safety evidence. It
excluded alternative creature/zone injuries only by consulting
`effects.creature_damage` and `effects.danger_zone_damage`, two physical
attribution fields that belong to WorldBody's **hidden technical record**.
With PR #77 in place those fields are rightly absent from I0's view. Their
absence cannot be interpreted as evidence that no alternative injury occurred.

An ordinary, non-toxic berry eaten inside an unknown damaging zone can
produce exactly the same observed food, body and action history as toxic
food on clean terrain. Without additional observations the cause is not
identifiable from that single experience.

## Conservative software rule

A harmful food exposure is eligible for DC-05 evidence and downstream
numeric causal-correction or hypothesis observations only when the Causal
Model has an **actually applied, non-ingestion `attendre`** control:

- at the same perceived (x, y) position during the immediately preceding
  world step;
- with independently captured integrity **unchanged** during that control;
- with a matching applied command and physical transition, both present in a
  closed, authorized DC-09 autobiographical episode;
- with the next-step Perception integrity matching the body state and the
  pre-food integrity;
- with provenance validated and retained within the Causal Model's
  snapshotted state.

If any component is missing, or waiting was itself harmful, the meal is
still physically executed and its full technical causal journal and
first-person memory remain intact, but it receives **no unwarranted DC-05
harm credit or numeric/correlation evidence**.

Previously admissible no-harm exposure observations remain possible. The
existing safety threshold, single-owner Causal Model publication, previous
life mortality rules, epistemic projection, and Oracle/Bench separation
are unchanged.

Controls are observed passively from genuinely applied decisions. This
does **not** schedule extra waits, force feeding, relabel an unexecuted
command as a physical trial, or use oracle knowledge. Expired controls
are retired unless their immediately following food exposure remains
awaiting a closed Memory episode.

## Limits and review

A clean wait on a previous step is **not definitive causal proof**:
future scenario injections, time-varying hazards, a creature arriving
between steps, hidden compensation by healing and unmeasured physical
changes remain possible. In particular, it must not be called a verified
absence of all confounding.

The current rule is a conservative development safeguard, not a sufficient
final design for toxic-food science. It can withhold valid toxic-food safety
evidence when I0 has no matched control, or when Memory closes different
segments out of order. This is preferable to a false established safety
claim, but warrants a separate operator review and scientific campaign
with contrasts, controls, uncertainty and falsification thresholds.

## Software validation

Run `python -m unittest tests.test_stage9_lived_evidence tests.test_stage9_lived_ambient_confound -v`,
followed by the full Python 3.11/3.12 software matrix and Stage-11
irreversible 600-step diagnostics after the security branch is integrated.

The tests include real `WorldBody` execution with a hidden damaging
zone, benign `berry_a`, authentic Stage-2 autobiographical projections,
and independently verified Causal Model evidence provenance. The full
technical journal still contains the zone damage; I0 must not learn its
physical label.

**Neither the test count nor a green CI reverses the Stage-9 NO-GO.**


## Visible competing-cause software gate (follow-up to issue #89)

An actually perceived adjacent creature in the food-step Stage-3
`PerceptualCapture` is a **plausible** independent physical source of
injury. The Stage-9 Causal Model now stores a boolean
`visible_creature_at_exposure` with the pending, externally applied,
goal-motivated food action. For a harmful outcome, this lived cue blocks
**all three** DC-05 harm safety admission, numerical outcome correction and
observational causal evidence. The hidden technical field
`effects.creature_damage` is not inspected to decide eligibility.

The optional boolean is validated during state restoration. False/absent
cues are omitted from exported snapshots to preserve historical owner
digests. The stage-10/11 behavior is not retroactively relabeled as a
scientific finding, and no action is injected to manufacture controls.

New real-physics tests include a creature **visible** on I0's own
cell or one cell away during its meal at simulated night, with positive
creature damage. A visible creature farther away is not treated as a
concurrent injury source for the food step,
after an independently closed clean wait; compare against a food-harm
world with an invisible dynamically activated danger zone and another
world with a genuinely harmful berry. Those last two can have **the exact
same first-person autobiography and accessible body telemetry** despite
different physical causes, while their technical causal archives differ.
The read-only external verifier checks both exports against externally
trusted full-count/head anchors, with cognitive/Oracle/Bench imports denied
in a fresh process. Its success certifies internal hash consistency, **not
the truth of an inferred causal mechanism**.

**Deliberate remaining limitation:** no purely first-person method can
discriminate two worlds with the same observable experience and different
unobserved causes. A previously clean wait is not proof of safety for a
zone that activates on the meal step. Further contrasts, held-out
interventions, independent scientific review and explicit operator
acceptance are required before scientific causal validity can be claimed.
**Stage 9 stays SCIENTIFIC NO-GO.**


## Issue #89 final epistemic admission contract

For the current v1.3.1 implementation, a post-ingestion integrity loss is classified as follows:

- **perceptible sufficient competitor present**: retain the lived episode, but create no food safety credit, no food causal observation and no numeric correction;
- **control absent or itself harmful**: retain the lived episode, but create no food safety credit, no food causal observation and no numeric correction;
- **clean immediately preceding lived control, no perceptible competitor, then harm after eating**: retain an `ambiguous_food_association`; do not credit DC-05, do not create a food causal observation, and do not create a numeric correction;
- **clean control and no harm after eating**: this remains an admissible lived no-harm observation under the existing demotion logic;
- **technical journal shows hidden physical cause**: operator/auditor information only; it never changes the cognitive classification above.

Changing position, repeating the meal, or accumulating more autobiographical episodes does **not** convert an ambiguous harmful association into a food-specific etiology. A hidden dynamic hazard can follow the same meal schedule and positions. Cryptographic journal integrity likewise cannot supply the missing causal information.

This contract deliberately prefers withheld attribution over fabricated causal certainty.

## Minimal normative delta proposed for operator review

The current v1.2.1/v1.3.1 vocabulary conflates two propositions that issue #89 shows are not generally equivalent:

1. repeated consumption of an item is empirically associated with harm strongly enough to justify a safety veto;
2. the item itself is toxic.

The present `CanonicalSafetyFacts.item_status()` maps learned `toxic_item + etabli_pour_securite` directly to `known_toxic`. Under observational equivalence, that label is stronger than the accessible evidence can justify.

A future, separately versioned specification should therefore consider the smallest semantic split:

- retain `toxic_item` and the causal lifecycle for etiological claims;
- add a distinct safety-use proposition such as `consumption_harm_risk` whose meaning is explicitly **empirical risk association, not physical toxicity**;
- permit its promotion from `n_sec` independent lived harmful consumption episodes under DC-05-style provenance and perceptible-competing-cause gates, without claiming hidden causes were excluded;
- let Action Control veto consumption from this safety-use proposition while reporting the reason as learned empirical risk rather than `known_toxic`;
- never use that safety association as a simulator correction, causal intervention result, or proof that the food caused the injury;
- keep Oracle, Bench and the complete technical journal outside cognition.

This delta would regain conservative safety learning without inventing causal identifiability. It is **not implemented or normative in v1.3.1**. Until explicit operator approval and a new versioned specification, the software must fail closed on harmful food etiology, and the cost is delayed or absent learned toxic-food vetoes in otherwise indistinguishable worlds.

Historical Stage 9 remains **SCIENTIFIC NO-GO** regardless of the operator's decision on this delta.
