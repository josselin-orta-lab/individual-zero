# Stage 9: scientific preregistration template

**Status: UNREGISTERED. This file is a blank protocol template, not an approved preregistration, a scientific result, or a Golden.**

Normative reference: `docs/architecture/reference/en/mvp-specification-v1.2.1.md`, sections 9.6, 13.2-13.4, 19.5, 20.3 (Stage 9), and INV-25. The English v1.2.1 specification always prevails.

## Purpose and boundary

Evaluate whether the Stage-9 Causal Model and Action Control correctly associate actions and observable consequences in independent worlds with known causes; reject inappropriate self-attribution; avoid `etablie` for noncausal or random associations; preserve the distinction between `etablie` (simulator corrections) and `etabli_pour_securite` (existing veto rules). All causal input to the individual must come from actual accessible Perception and independently closed autobiographical episodes. World truth, random schedules and the oracle remain exclusively on the bench side.

Do not use the fixed software tests, hand-typed observations, bench-seeded false hypotheses or previous exploratory seeds to claim independent scientific success.

## Required frozen registration, **before** hold-out runs

The author or designated experiment owner must fill each item and commit the registration with its digest **before** revealing hold-out outcomes. Unfilled values mean `NOT REGISTERED` and cannot authorize Stage 9 acceptance.

| Field | Must be specified in advance |
| --- | --- |
| Registration ID, author, timestamp, immutable commit/hash | **UNSET** |
| Exact individual code commit and equipment/parameter/ontology manifests | **UNSET** |
| Objective and ground-truth classification for each causal family | **UNSET** |
| Independent hold-out world generators, physical variants, and world IDs | **UNSET** |
| Independent held-out seeds and random assignment scheme | **UNSET** |
| Calibration-world and development-seed exclusions | **UNSET** |
| Steps per run, number of independent runs and run termination rules | **UNSET** |
| Comparable exposure, controlled context, and independent episode definitions | **UNSET** |
| Expected minimum number of naturally generated candidate hypotheses (rate denominator) | **UNSET** |
| Exact superstition-rate numerator, denominator, confidence method and aggregation | **UNSET** |
| Maximum acceptable spontaneous superstitious-rule rate and uncertainty rule | **UNSET** |
| Minimum known-cause attribution performance and uncertainty/abstention rules | **UNSET** |
| Treatment of multiple causes, ambiguous comparator outcomes and interventions | **UNSET** |
| Safety-veto checks including unchanged R_a and unaffected simulator predictions | **UNSET** |
| Replay equality checks, expected artefacts, missing-run policy and analysis scripts | **UNSET** |
| Inclusion/exclusion rules, failure handling and stopping rule | **UNSET** |

**Critical:** if naturally acquired causal candidates are absent, the superstition rate has a zero denominator and is `NOT EVALUABLE`, never `0%` or `PASS`. An observation of reward alone is not an independent causal test. Do not inject a hypothesis to create a denominator. Do not select or revise thresholds after looking at hold-out results.

## Machine-readable preregistration preflight

The laboratory supplies a prospective JSON manifest containing the exact
fields checked by `lab.stage9_scientific_preregistration`, including
SHA-256 digests of the physical world+layout+scenario manifests for **every**
calibration and hold-out world. The preflight checks that two different IDs
cannot reuse the same physical world. The frozen world generator, equipment,
parameter registry, and ontology also require version-identifying SHA-256
digests. These declarations do not prove actual physical independence:
the bench must compare the manifests to each digest. Validate the draft using:

```bash
python -m lab.stage9_scientific_preregistration
python -m lab.stage9_scientific_preregistration --manifest path/to/registration.json
```

Without a manifest, the result is `unregistered`. A complete manifest is
**only a draft**, identified by its canonical digest. It remains
`draft_requires_independent_git_seal`: the evaluator must separately check
that the registration was committed before any hold-out outcome was observed,
that its world IDs correspond to physically distinct configurations, and that
none of the held-out seeds were used for calibration. JSON field validation
does **not** certify genuine world independence or Git chronology.

The utility never produces `scientific_verdict=PASS` or freezes Stage 9
from a draft. The CI stores a fail-closed readiness artifact, not a certificate
of scientific validity. Test fixture values in unit tests are **not** thresholds
selected for the research campaign.

## Held-out metric assessment (provisional, not certification)

The lab-only tool can score a prospective held-out evidence manifest, but cannot
declare Golden or a scientific verdict without independently audited physical
witnesses and Git chronology. Usage:

~~~bash
python -m lab.stage9_scientific_assessment
python -m lab.stage9_scientific_assessment --registration registration.json --evidence heldout.json
~~~

The evidence envelope must identify the frozen registration digest and
implementation commit and include every registered world × seed pair. Each run
contains its registered physical world SHA-256, original and replay journal
hashes, original and replay causal-state hashes, independently sourced
known-cause case rows with ground truth and agency attribution, and the
naturally acquired false-rule candidates in negative-control worlds. The
whole envelope has its own canonical SHA-256. The held-out evidence
protocol is `stage9-heldout-evidence-v2`: each naturally acquired
false-rule candidate must identify both its individual sample ID and its
canonical `contingency_ref`. A canonical causal rule may be counted only
once within a world/seed run, regardless of how many physical observations,
Memory episodes or candidate ID aliases mention it. The same canonical
predicate/reference may legitimately be learned in different independent
world/seed runs. A physical observation source
reference may be counted **only once within a world/seed run**, across both
known-cause cases and naturally acquired false-rule candidates. A closed
Memory episode may legitimately contain multiple distinct world transitions:
the episode identifier is provenance, **not** the physical deduplication key.
Causal establishment still requires independently controlled intervention
contexts under §13.2; safety promotion/demotion separately requires distinct
evidential episodes under DC-05. This report format does not by itself verify
those contexts or establish independent statistical sampling: an external
witness audit remains mandatory before treating provisional Wilson intervals
as scientific evidence or freezing a Golden.

The scorer recomputes attribution accuracy, abstentions, false self links,
false-rule rates and two-sided 95% Wilson confidence intervals.
Each registered positive world × seed run must contain at least one
independently observed known-positive-cause case. If a positive run contains
only no-effect controls or no causal cases, the assessor reports
`incomplete_known_cause_world_coverage` even if the pooled accuracy from
other runs looks strong; it lists the missing world/seed pairs for external
review. No missing observation is invented or silently excluded.

No-effect physical controls (`ground_truth=none`) are excluded from the
known-positive-cause accuracy denominator. Their abstentions are reported
separately; any self/world causal attribution without an observed physical
effect is marked `invalid_no_effect_attribution`, not review-eligible. It returns
"not_evaluable" if any required denominator is zero, and keeps Golden false
even when metrics meet prospectively frozen limits: raw journal/oracle
authenticity, independent world generation, prospective registration ancestry,
INV-25 and exact reproduction still need external examination.

The command-line assessor parses untrusted JSON strictly: duplicate keys
at any nesting level and non-finite literals such as NaN or Infinity are
rejected before any provisional score is calculated. This prevents two
readers from interpreting the same evidence bytes differently.

No demonstration JSON fixture or prior exploratory matrix is valid held-out
evidence; changing the registered confidence rule after seeing outcomes is
prohibited. Only "wilson_95" is implemented. The registration preflight now rejects
unsupported confidence methods before a draft can be sealed. Other
prospective confidence rules require code and tests *before* a hold-out
campaign begins. Both preregistration and evidence JSON loaders reject
duplicate object keys and NaN/Infinity constants at any nesting level.

## Experimental separation

1. **Calibration:** choose necessary parameters using disjoint worlds and seeds, following the normative parameter registry and its calibration protocols. Record their immutable hashes.
2. **Registration:** fix thresholds, run count, families, seeds/world selection, analysis and exclusion rules. Record the registration commit and SHA-256 digest before any hold-out result is inspected.
3. **Hold-out campaign:** execute independently constructed positive and negative worlds. Log full real command-to-transition provenance and the separate bench-only ground truth. Do not expose oracle, world internals or synthetic candidate labels to any individual component.
4. **Analysis:** for known causes, report correct/incorrect/uncertain outcomes without counting abstentions as correct links. For random reward, count only independently observed, naturally acquired candidates and the subset falsely established. Report the numerator, denominator, uncertainty and preregistered threshold exactly.
5. **Replay:** re-execute every accepted run under the frozen manifests; compare normalized journals, causal owner state and reported metrics. Reject silent repairs or cherry-picked seeds.
6. **Decision:** accept only if **every** Stage-9 normative criterion passes the preregistered rule, invariants and CI pass, and independent reproducibility is documented. Otherwise report `NOT EVALUABLE`, `INCONCLUSIVE` or `FAIL` with evidence. The Golden remains unfrozen.

## Existing diagnostic commands (exploratory only)

```bash
python -m unittest discover -s tests -v
python -m lab.stage9_hydration_contrast_report
python -m lab.stage9_spontaneous_superstition_matrix
python -m lab.stage9_acceptance_report
```

The CI archives `stage9-hydration-contrast-diagnostic` and `stage9-acceptance-diagnostics`. Their hashes identify **diagnostic artefacts**, not a scientific preregistration or Golden.

Random-reward diagnostics count accepted *physical hydration observations*
separately from distinct closed Memory episode identifiers. Multiple actual
world transitions may occur within one episode; duplicating the same physical
transition is forbidden, as is claiming two independent transitions
from the same applied command. The bench cross-checks both the experienced
command and transition against the **same named closed Memory episode**,
not merely a union of event references across all closed episodes. The report fields `lived_hydration_observations`
and `independent_lived_hydration_episodes` therefore measure different
units. An episode count alone is not proof of statistically independent
experimental sampling.

The current Stage-9 reference runs may legitimately produce causal-test proposals that are not scored until normative Exploration motivation is available (Stage 11); do not fake intrinsic motivation or weaken safety/competition to manufacture interventions.

## Acceptance hand-off

A completed registration identifies a freeze commit and hash, an isolated held-out evaluation set, the exact runner and output location, the bench's ground-truth custody, a reviewer who has not selected thresholds from observed outcomes, and an explicit pass/fail/inconclusive report. The Stage-9 Golden reference is frozen **only after** these conditions and the Stage-9 acceptance checks are satisfied.
