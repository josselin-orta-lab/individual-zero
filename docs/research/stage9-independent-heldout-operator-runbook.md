# Stage 9: independent held-out operator runbook

**Status: NOT EXECUTED / NOT SCIENTIFICALLY VALIDATED.** This is a procedural
handoff for an external evaluation, not an approved protocol, an observation,
a pass, INV-25 closure, or a Golden. The only normative implementation source
is 'docs/architecture/reference/en/mvp-specification-v1.2.1.md', especially
§§9.6, 13.2, 19.5, 20.3 Stage 9 and INV-25. If instructions differ, the
normative English v1.2.1 text prevails.

For the full exact schemas and scientific criteria, see
[the preregistration template](stage9-scientific-preregistration-template.md).
Do not run the deliberately synthetic test fixtures as if they were real data.

Before a held-out campaign, complete the separate
[pre-launch approval record](stage9-heldout-prelaunch-decision-record.md).
It begins at **NO-GO** and records who accepted each responsibility,
conflicts of interest, controlled custody, protocol approval, and an explicit
human release-to-run decision. A named role or a filled template is not proof
of independence. In particular, preregistration schema v2 contains the actual
held-out seeds **in plaintext**: the registration commit must initially be
made only in an independently controlled Git checkout/history that is not
accessible to developers, not on this development PR or in CI logs.
Preserve a separate independently witnessed time-stamped registration
receipt; Git ancestry alone does not establish calendar-time antedating.
The full isolated history can be examined by the authorized evaluator later
without prematurely distributing hidden worlds, seeds or bench-only oracle.


## Accountability and isolation

| Role | Holds and decides | Must not do |
| --- | --- | --- |
| Research owner | Approves **before results** the protocol, analysis thresholds, sample counts, exclusions, stopping rule and independent reviewer | Change thresholds or inclusion rules after inspecting outcomes |
| Independent world/seed custodian | Holds original physical world/layout/scenario files and unrevealed evaluation seeds, including positive/null control labels and bench-only oracle truth | Share oracle, outcome labels or unrevealed hold-out seeds with the individual or its learning components |
| Execution operator | Runs the frozen individual in separately identified world/seed cells; archives raw journals, causal-owner/Memory states, preflight receipts and replay data | Tune the implementation, seeds or protocol on held-out performance |
| Independent reviewer | Examines prospectivity, original files, real runtime, world/seed independence, oracle separation, acceptance criteria and failures | Equate matching SHA-256 digests or CI success with a physical witness |

Different roles may require separate people or explicit independent scrutiny.
Merely naming a different role or a different Git branch is not evidence of
independence. Preserve custody records and reveal necessary secrets only after
the research plan is frozen, never to the simulated individual.

## Chronological procedure

### 1. Before revealing any hold-out result

1. Freeze the exact implementation Git commit, root 'pyproject.toml', English
   v1.2.1 normative specification and parameter/ontology/equipment versions.
   The draft registration checks the actual normative file using a guarded
   descriptor; Git chronology and pre-run checkout checks must still establish
   the unchanged frozen specification bytes independently.
2. Complete and author-approve the registration JSON using the existing exact
   'stage9-preregistration-schema-v2'; designate calibration and held-out
   worlds, positive/null controls, disjoint seeds, candidate definition,
   measured endpoints, confidence method ('wilson_95'), thresholds, sample
   size, exclusions and stopping rule. Keep the oracle bench-only.
3. Deposit the signed-off prospective registration in Git at a dedicated
   immutable commit **after** the frozen implementation commit. Record both
   full 40-character commit IDs, the registration digest, approval and
   independent custody witnesses outside any individual-accessible channel.
4. Run the format check. Passing merely establishes a well-formed draft:

   ~~~bash
   python -m lab.stage9_scientific_preregistration \
     --manifest research/stage9/registration.json
   ~~~

5. Archive original bytes and SHA-256 for all physical world/layout/scenario
   manifests and the four frozen manifests. The **custody index** contains
   role-to-path mappings and the registration digest; it may be created separately and does not amend registration.
   Use the exact 'stage9-registered-physical-manifest-index-v1' JSON structure
   defined in the preregistration template.

   ~~~bash
   python -m lab.stage9_registered_manifest_custody \
     --registration research/stage9/registration.json \
     --index results/stage9/physical-manifest-index.json \
     --artifact-root results/stage9/raw-manifests
   ~~~

6. In the **actual checkout selected for execution**, before the first run,
   archive the output of this read-only source-byte preflight:

   ~~~bash
   python -m lab.stage9_frozen_worktree \
     --repo . \
     --frozen-commit FULL_40_CHARACTER_IMPLEMENTATION_COMMIT
   ~~~

   This preflight reads tracked source, package and normative specification
   bytes with guarded no-follow descriptors, rejecting detectable path
   substitutions during reading. It still cannot attest that the same
   checkout actually executed or exclude transient changes between checks.

A failed control at this point is an execution blocker, not grounds to silently
change a sealed manifest. Either correct the plan **prospectively** through a
new documented freeze and registration, or declare the attempted campaign
inconclusive. Archive who inspected results and when.

### 2. Execute and preserve raw outcomes

1. Run **all** preregistered world × seed cells, including positive- and
   null-control worlds; do not selectively drop runs or add post-hoc seeds.
2. Independently record the world's actual physics/ground-truth mechanisms and
   oracle-positive/null labels on the *bench side*. Keep them inaccessible to
   Individual Zero, including its causal model, memory, simulator and inputs.
3. Preserve the original append-only canonical journal, closed Memory and
   causal-owner snapshot, plus byte-exact replay copies for **every** cell.
   Replaying under the frozen setup must not silently reuse the original
   result files as generated outputs.
4. Compute the exact 'stage9-heldout-evidence-v2' report and its canonical
   digest. Record **naturally acquired** false contingencies only; never seed
   invented false hypotheses to improve a denominator. Include zero-candidate
   and no-effect outcomes transparently.
5. Deposit the report in a later Git evidence commit. Retain independently
   produced execution logs, runtime/environment identity, original file
   custody, seed-selection records, and independent witness notes. Do not
   retrofit Git metadata to represent an earlier approval.

### 3. Independent post-run verification

Run all of the following against the **unaltered files** and complete,
unshallowed Git history. Git chronology and frozen-source preflight reject
environment overrides capable of redirecting the repository, object store
or Git configuration (for example GIT_DIR, GIT_WORK_TREE,
GIT_OBJECT_DIRECTORY and GIT_CONFIG_COUNT). Use a clean Git environment,
investigate rejected redirections and preserve the failed audit record:

~~~bash
python -m lab.stage9_registration_chronology \
  --repo . \
  --registration research/stage9/registration.json \
  --registration-commit FULL_40_CHARACTER_PREREGISTRATION_COMMIT \
  --evidence results/stage9/heldout.json \
  --evidence-commit FULL_40_CHARACTER_EVIDENCE_COMMIT

python -m lab.stage9_scientific_assessment \
  --registration research/stage9/registration.json \
  --evidence results/stage9/heldout.json

python -m lab.stage9_heldout_artifact_custody \
  --registration research/stage9/registration.json \
  --evidence results/stage9/heldout.json \
  --index results/stage9/raw-artifact-index.json \
  --artifact-root results/stage9/raw
~~~

For an **additional single, fail-closed machine receipt**, invoke the
combined reader. It runs the Git-chronology audit, the present-checkout
preflight, the registered physical manifest audit, the raw journal/Memory
custody audit and the provisional scorer using one coherent registration:

~~~bash
python -m lab.stage9_independent_handoff \
  --repo . \
  --registration research/stage9/registration.json \
  --registration-commit FULL_40_CHARACTER_PREREGISTRATION_COMMIT \
  --evidence results/stage9/heldout.json \
  --evidence-commit FULL_40_CHARACTER_EVIDENCE_COMMIT \
  --manifest-index results/stage9/physical-manifest-index.json \
  --manifest-root results/stage9/raw-manifests \
  --raw-index results/stage9/raw-artifact-index.json \
  --raw-artifact-root results/stage9/raw
~~~

The combined output includes a deterministic machine-receipt SHA-256, all
underlying machine reports, the recorded metric status and explicit
unattested claims. The `review_blockers` field must be examined **before**
any scientific decision. It explicitly flags a report path already present
at preregistration **or anywhere earlier in its Git ancestry**
(including a different placeholder later deleted, which requires
prospectivity review), or metrics that do not meet the registered confidence
criteria. A byte-identical outcome already committed **anywhere in the
Git history reachable from registration**, even under a different path or
after deletion, is rejected rather than receiving a machine receipt.
The audit also detects JSON reports with the **same parsed content** but
different whitespace, field order or file name. For Stage-9 evidence, it
additionally treats different presentation order of registered world/seed
runs, known-cause cases and naturally acquired false-rule rows as the **same
claimed observations**, even when the report SHA-256 was recomputed after
reordering. Reordered archives predating registration are rejected rather
than counted as new independent trials. This supplementary scan is
bounded (currently at least 1 MiB per candidate blob and at most 64 MiB).
Unexamined larger Git objects are counted and become an explicit
`pre_registration_large_git_blobs_not_semantically_inspected`
review blocker. A pre-registration Stage-9-looking JSON blob containing
duplicate keys, non-finite constants (including numeric overflow such as
`1e999`) or invalid syntax is **not silently ignored**: it is recorded under
`pre_registration_ambiguous_stage9_json_blobs` with the review blocker
`pre_registration_ambiguous_stage9_json_requires_prospectivity_review`.
If even permissive parsing of such an ambiguous document reproduces the
exact archived evidence, the audit rejects the campaign outright. The scan
strictly parses all size-bounded earlier Git blobs (without trusting
filename extensions or first-byte signatures), including Unicode-encoded
JSON in UTF-8 with BOM, UTF-16 or UTF-32. A change in encoding, including
leading Unicode whitespace, cannot by itself disguise an identical report.
These heuristics cannot prove the absence of compressed, wrapped or otherwise
transformed data, unpublished results, or objects outside reachable Git
history; independent prospectivity review remains essential. A structurally complete receipt with those flags is **not** a
passing held-out campaign. A report with no flags is also **not** an
independent scientific witness. The provisional scorer also exposes
`reused_closed_memory_candidate_episodes` for distinct false-candidate rules
sharing one closed Memory episode,
`reused_closed_memory_known_case_episodes` for multiple known-cause
observations sharing an episode, and
`negative_runs_without_natural_candidates` for registered null-world/seed
cells contributing no naturally acquired candidate. These become explicit
`review_blockers` when they threaten interpretation of the pooled
confidence intervals. A Memory episode can legitimately contain multiple
distinct applied physical transitions; an episode identifier is **neither**
a uniquely independent physical trial nor an invalid observation. Likewise,
a null run can legitimately produce zero hypotheses. Do not fabricate
additional observations, drop that run, alter preregistered thresholds or
assume trial independence from unique event IDs. Preserve the original
counts and have the reviewer assess physical contexts, within-episode
dependence, run-level clustering and the registered sampling plan. The
raw-artifact reader independently recomputes these diagnostics and the
single handoff command requires exact agreement between readers.

A separate cross-run check reports any
byte-identical original journal or canonical causal-owner state in two or
more distinct registered world/seed cells. These are explicit
`cross_run_identical_archives` groups, with separate `review_blockers`
for reused journal and causal-state bytes. Even when individual per-file
SHA-256, replay, canonical journal, physical event and Memory closure
checks all pass, copying one cell's files under fresh paths does not
establish independent execution. **Byte collisions are a reason for
independent provenance review, not automatic proof that the scientific
outcome is false:** two truly independent executions can occasionally
produce identical serialized state. It writes no source or scientific result,
cannot return a Golden and cannot replace an independent reviewer. Checking
the **current** checkout does not retrospectively prove that it was the binary
actually executed; preserve the separate pre-run receipt from step 1.

The Git chronology reader also rejects aliases, noncanonical traversal and
symlinks in paths supplied for sealed registration and evidence artifacts. It
compares the committed bytes to separately guarded physical reads, not to
path-resolved aliases. The decoded registration and report used for metrics
are independently compared, under strict JSON decoding, with the objects in
the prospectively sealed and later evidence Git blobs. A transient file swap
that affects only an early JSON parse cannot substitute a different protocol
or outcome while a later physical-file comparison sees the restored bytes.
These local controls cannot attest the experimenter's history or independent
custody.

The registration, held-out evidence and both custody-index JSON readers use
guarded UTF-8 file descriptors. A syntactically valid JSON document reached
through a symlink or detectably changed while reading is rejected; this
does not prove independent physical custody or prospective approval.

Retain the manifest-file audit from step 1 and compare the physical manifests
again if custody changed hands. Physical-manifest hashing uses the same guarded
descriptor reader as raw evidence, rejecting detectable same-size in-place
changes and persistent parent-directory substitutions during reading. If any
tool reports a mismatch, block acceptance and retain the failure. The raw-artifact reader also opens each
journal, replay and archived causal-owner file through guarded regular-file
descriptors, rejecting symlink replacements of file or parent directories and
detectable in-read mutations. After each read it also checks that the named
path still resolves to the opened inode, catching persistent parent-directory
swaps even when the opened file itself was never modified. This local
filesystem safeguard requires no-follow descriptor support; it cannot
establish independent custody, prevent transient changes reverted before the
checks, or witness the actual execution. During one custody audit,
the canonical journal and archived causal-owner file are each parsed from
their own single guarded byte image, with each image's SHA-256 checked against
the registered report. Journal event, P-47 and physical-transition evidence
cannot be read from a different journal image after digest verification.
The same frozen owner-state image serves causal evidence, P-47 and
closed-Memory checks; standalone file readers still reject symlink paths. This prevents mixing snapshots
read at different moments, but does not prevent transient tampering outside
the guarded reads or establish an independent physical witness. The raw-artifact
checker validates physical event identities, same-attempt commands/transitions,
and the INV-53 condition that two separately committed attempts cannot
claim two normally completed advancements of the same world step. Every
committed attempt with physical events is also checked globally for one
command, one transition, their chronological order, and one autobiographical
commit containing both original event references, **even if that attempt
does not appear in held-out scoring rows**. Attempts with zero applied commands
and zero advancement are not misclassified as successful physical steps.
Uncommitted rollback attempts may remain in the technical journal (INV-49)
without becoming accepted physical samples. Every committed `event_refs` entry must also belong to the same
`attempt_ref` and `t_monde`. Each commit must declare a recognized
`filter_version` belonging to the versioned Stage-2 or Stage-7/DC-09
runtime policy. Referenced events must be permitted by **that exact version**:
an unknown version or a Stage-2 commit referencing Stage-7-only cognitive
content fails closed. This prevents even
unreported commits from laundering oracle, technical or foreign-attempt
events into Memory. The checker also validates canonical P-47 source
measurements, causal evidence, reviews, intervention contexts and closed
Memory references. It does **not** attest that these events occurred in the
claimed independent physical environment.

The scientific scorer produces **provisional** Wilson intervals and per-run
metrics only. A failed, incomplete, zero-denominator or non-evaluable campaign
must remain so, even if a more favorable selection of runs is available.

### 4. Independent review and decision

**INV-25 differential review (normative §§12.3, 13.3 and 21.1).** The
independent reviewer must retain a paired, input-identical comparison for each
relevant held-out safety fact, using one frozen Equipment version, identical
accessible pre-action state and command, identical random streams and
simulation budgets, and separately recorded canonical causal statuses:

1. **Without a learned safety-only fact**, retain the Equipment-based
   prediction and the external, independently computed `R_a` for that option.
2. **With the same fact established only as `etabli_pour_securite`**, retain
   the prediction and `R_a` again. They must be **causally identical** to the
   first condition. The already-existing Action Control veto must nevertheless
   make a matching dangerous command inadmissible and Planning must respect
   that fact. The safety fact must not create a simulator correction or an
   invented additional risk penalty.
3. **If a separate fact genuinely reached causal status `etablie` through
   the prospectively defined observation/review/intervention lifecycle**,
   verify that an authorized simulator correction affects only its supported
   variable and exact application context. Refuted, safety-only, unmatched or
   unresolved/conflicting evidence must not silently change predictions.

The evaluator should record the original paired input-state/command digests,
the code and Equipment identities, status and independent evidence references,
the normalized before/after predictions, admissibility outcome, `R_a`, and
any counterexample. Recompute rather than reclassify the outcomes. Use
already experienced physical transitions: **never deliberately ingest a known
toxic resource to test a safety-only rule**. Local regression coverage includes
`tests/test_stage9_canonical_corrections.py` and
`tests/test_stage9_causal_corrections.py`, but passing those synthetic
tests neither provides held-out independence nor approves INV-25. An omitted
paired measurement is `NOT VERIFIED`, not a PASS.

The reviewer must explicitly evaluate the unautomated requirements:
prospective approval before anyone saw held-out outcomes; provenance,
physical distinction and oracle isolation of worlds; disjoint seed selection;
actual frozen runtime identity; correct counterfactual/no-effect treatment;
absence of artificially seeded hypotheses; integrity and independence of
closed-Memory causal witnesses; and all Stage-9 acceptance criteria in the
English normative specification, including INV-25.

Record one transparent decision: **PASS**, **FAIL** or **INCONCLUSIVE**,
with observations, anomalies, exclusions, independently reproduced metrics,
identities and sign-off by reviewers, and links to immutable artifacts.
Publish the unfavorable and inconclusive outcomes too. A software output
containing 'scientific_verdict: null' and 'golden_stage9_frozen: false' is expected,
even when every automated checker succeeds. **No automated tool in this
runbook is allowed to change these two fields to success.**

Only an independently supported acceptance decision may be considered when
a future project owner reviews a Stage-9 Golden freeze. This document,
synthetic test results, diagnostic CI and mechanically consistent Git history
never create that freeze by themselves.
