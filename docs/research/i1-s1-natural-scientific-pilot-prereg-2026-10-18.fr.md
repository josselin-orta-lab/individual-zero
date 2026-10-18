# I1 natural scientific campaign S1 — preregistration (2026-10-18)

Status: PREREGISTERED / NO SCIENTIFIC VERDICT. No historical broken cohort is an oracle.

## Locked experimental object
- Canonical I1 code/base commit: `f87cbc15a34f9b0f2a43749bb2b3377a45401b84`.
- The runner must checkout **this exact commit**, not the branch's changing HEAD.
- Existing immutable external world inputs: `src/i1/lab/world_presets/*.json`, each recorded with its SHA256 in the runner's report.
- No cognitive-code, body physics, UC, cognition, temperament, mortality, journal schema, I0 or M11 changes are permitted. No H1/H2 and no old experimental trajectories as comparison or acceptance evidence.
- Individuals receive local information only. No forced command, privileged oracle, rollback, resurrection or dead-life retry.

## Questions / pilot design
Six pre-existing worlds: oasis, foraging, dry-valley, empty-land, hazard-edge, blocked-route.
Pilot: **3 newborn mortal WAL lives per world; 60 maximum requested steps per life**, fixed birth seed 246, total maximum 1,080 life-steps. This is an **instrumentation and descriptive feasibility pilot**, not a statistically independent map sample. Its worlds have unequal initial bodily reserves and physically fixed geometries. Document physical deaths, censoring and technical failures, without replacement. M11 complementary runs and main cohort (12 per world, <=300 steps) require a separate reviewed protocol amendment after verifying pilot data.

## Locked definitions
- Observer numerator **applied physical commands**: join unique technical `command_experienced` and `world_transition_experienced` by (life, world step, attempt_ref); transition proves a physical advancement. A terminal `dead` command still counts as physical execution. Ambiguous/multiple candidate matches are unverified and excluded from proven numerator, separately counted.
- Denominator: actual unique `step_closed` world-step occurrences, not requested steps nor repeated technical events. Cross-check with report step count. If missing or incompatible, label metrics NOT_OBSERVED.
- Applied commands per step = verified applied commands / actually closed steps.
- Distribution by primitive = verified applied commands of that primitive / all verified applied commands. Share of steps containing a primitive = distinct closed steps with this primitive / closed steps. Action count by step may be >=1; never force a 100% per-step frequency normalization.
- Behavioral categories are descriptive and based on observed primitives: se_deplacer movement, collecter collection, manger/boire physiological intake, dormir/attendre rest, other primitives individually identified. No asserted internal intentions.
- Stage10: count distinct emitted `stage10_sleep_entered`, `stage10_consolidation_batch_frozen`, `stage10_consolidation_pass_checkpointed`, `stage10_consolidation_work_deferred`, `stage10_consolidation_publication_deferred`, `stage10_consolidation_committed` by unique journal identity. A committed event is **not** proof of a nonempty published owner state. Detailed owner deltas, UC and durable M11 publication are NOT_OBSERVED in this pilot unless separately evidenced.
- Learning: trajectories in WAL prove physical outcomes, not subjective cognitive updates. No positive learning claim without an observable first-person event -> owner delta -> subsequent choice -> confirmed outcome chain. Apparent improvement has geography, needs, chance and mortality-survivorship alternatives.
- Negative and unobserved outcomes remain in the sample. No acceptance criterion demands survival, consolidation or learning.

## Evidence and integrity gate
Use existing `tools/run_i1_world_preset.py` and immutable WAL files, independently replayed by `i1lab.journal.HashChainedJournal.audit_durable_wal` already invoked in the preset runner. Scientific analyzer is **external post-run Python reading reports and WAL bytes**; it must never instantiate a runtime, read arbitrary operator truth into cognition or write into a living artifact. Reject bad schemas, missing files and inconsistent hashes. Label unavailable action source, owner states and cognitive claims NOT_OBSERVED rather than guessing from location/inventory.

Each scenario writes a fresh output directory, immutable report and custody files; artifacts must be archived, with SHA and environment digest. Any technical failure halts interpretation for that execution and is reported explicitly. Decisions after pilot: continue, amend instruments, inconclusive or stop. No scientific GO from green CI alone.

## Statistical and scientific disposition
Report per-life as well as pooled ratios, exact denominators, mortality and truncation; avoid treating actions/steps within one life as independent replicates. Comparative outcomes across unequal worlds are descriptive. Main experiment remains BLOCKED until pilot integrity and observability is verified. `stage10_nonempty_publication` and `first_person_learning` are NOT_OBSERVED unless new genuinely validated independent evidence is collected.
