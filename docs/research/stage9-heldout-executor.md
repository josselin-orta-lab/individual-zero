# Stage 9: isolated held-out operator executor

**Status: technical operator tooling, not an approved campaign or Golden.**
Normative authority: \`docs/architecture/reference/en/mvp-specification-v1.2.1.md\`.
The [pre-launch decision record](stage9-heldout-prelaunch-decision-record.md)
must have real named personnel, independent custody and an externally signed
GO **before any execution**. The [operator runbook](stage9-independent-heldout-operator-runbook.md)
remains the master scientific chronology. This executable does not self-approve
or measure human independence.

## What the executor actually does

\`python -m lab.stage9_heldout_runner\` has **run** and **package** commands.

- **run** checks a sealed preregistration Git commit, the unmodified frozen
  \`src/\`, root \`pyproject.toml\` and normative specification, exact world and
  frozen-manifest SHA-256 custody, and a separately provided external human
  GO record. It then runs the *real Stage9Runtime*, with registered externally
  generated world geometry, causal world physics and logged external scenario
  events, for **every** world × seed cell. It runs each cell twice independently
  and saves both byte-exact, separately produced journals and full causal-owner
  states. It archives world truth only to a bench-only file outside the
  individual's accessible perception, memory or learning input. Existing
  or symlinked output paths fail closed; crashes leave incomplete artefacts
  for investigation, not a scientific result.
- **package** consumes separate *independently written bench annotations*
  referencing actual observed transitions and closed Memory episodes.
  It checks the original/replay artefacts against the operator index and
  independently audits journal/Memory provenance. It then constructs
  \`stage9-heldout-evidence-v2\` and
  \`stage9-heldout-raw-artifact-index-v4\`, checks the existing machine scorer
  and raw custody audit, and **never** returns scientific PASS or Golden.
  The runner does not invent observations, hypotheses, causal truth labels,
  exclusion reasons or a denominator. A zero candidate denominator remains
  \`not_evaluable\`.

The implementation currently supports frozen **exact-transition-table**
Equipment and operator-supplied Stage-9 config from the existing parameter
dataclasses. Future equipment architectures require a separately validated
decoder **before** scientific freeze. Parameters from historical
\`stage9_reference_fixture.py\` are *software compatibility values only*, not
calibrated scientific parameters.

## 1. Prepare frozen manifests while still on calibration data

The *independently approved* \`stage9-preregistration-schema-v2\` requires the
original bytes' SHA-256 for four frozen manifests and every distinct physical
calibration and held-out world manifest. The manifest reader checks the raw
bytes, not an arbitrarily normalized JSON hash.

Supply these JSON files through the custodian-controlled root
\`results/stage9/raw-manifests\` (or another isolated root). Do not place real
held-out data in the developer-readable branch.

| Custodied file role | Exact format |
| --- | --- |
| \`world_generator\` | \`{"protocol_version":"stage9-heldout-world-generator-v1","generation":{...}}\`; \`generation\` contains exactly all \`WorldGenerationConfig\` fields, with calibrated counts/gains and version matching \`world_generator_version\` in registration |
| \`parameter_registry\` | \`{"protocol_version":"stage9-heldout-parameters-v1","stage9_config":{...},"safety_config":{"version":"...","lethal_max":2,"mode":"campaign"},"protected_integrity_threshold":20.0,"innate_safety_facts":{...}}\` with complete, explicitly calibrated \`Stage9Config\` subtrees; numbers above are illustrative only |
| \`equipment\` | \`{"protocol_version":"stage9-heldout-equipment-v1","artifact":{...},"records":[...]}\`; exact \`EquipmentArtifact\` and its \`ExactTransitionRecord\` table; records and hashes must match the trained artifact |
| \`ontology\` | JSON object with \`"protocol_version":"stage9-heldout-ontology-v1"\`; its semantics must be independently checked against the frozen code's actual ontology registry |
| each world | \`{"protocol_version":"stage9-heldout-physical-world-v1","world_id":"...","physics":{...},"scenario":{"id":"...","version":"...","events":[...]}}\`; \`physics\` must contain the full \`WorldPhysicsConfig.as_dict()\` fields. Scenario entries have \`t_monde\`, \`sequence\`, \`operation\`, and \`payload\` |

The world-generator configuration determines an actual seeded geometry and
which of the two berry species is toxic or nutritious. Each world manifest
defines physical dynamics and a deterministic external scenario schedule.
World and seed values are **not** CLI defaults: the sealed registration is
the exact Cartesian-product authority. Every original world manifest must
have a distinct digest. The independent reviewer must still verify real
physical/causal distinction, null/positive semantics, independent sampling,
and actual world execution. The runner supports the existing
\`InjectedScenario\` operations: \`set_danger_zone\`, \`set_lethal_zone\`,
\`place_creature\`, \`remove_creature\`, \`place_resource\`, \`set_body\`.
It does not inject false causal hypotheses or grant the individual oracle
access. A random-reward/null-control schedule must be designed, seeded,
logged and preregistered explicitly rather than fabricated during scoring.

There is a Python export helper for the *already calibrated* runtime:

~~~python
from lab.stage9_heldout_runner import export_frozen_stage9_assets

# calibrated_runtime is supplied by an independently documented, approved
# offline calibration process, never by hidden hold-out feedback.
parameter_document, equipment_document = export_frozen_stage9_assets(
    calibrated_runtime
)
~~~

This function does **not** calibrate or approve anything. The operator must
serialize the returned dictionaries to ordinary strict JSON, custody their
original bytes, register their raw SHA-256 values, and confirm that their
contents match the author-approved calibration. The production loader rejects
missing, extra, malformed or incompatible nested parameters and equipment.

Example index structure, showing **illustrative path names only**, not
registered data:

~~~json
{
  "protocol_version": "stage9-registered-physical-manifest-index-v1",
  "registration_digest": "FULL_CANONICAL_REGISTRATION_SHA256",
  "frozen_manifests": {
    "world_generator": "frozen/generator.json",
    "equipment": "frozen/equipment.json",
    "parameter_registry": "frozen/parameters.json",
    "ontology": "frozen/ontology.json"
  },
  "calibration_worlds": {
    "calibration-example": "worlds/calibration-example.json"
  },
  "holdout_worlds": {
    "positive-example": "worlds/positive-example.json",
    "null-example": "worlds/null-example.json"
  }
}
~~~

IDs, paths and registered counts must match the **real** preregistration.
Never paste true held-out seeds or positive/null oracle schedules into issues,
PR comments, developer-readable files or AI conversations.

## 2. Approve and seal the experiment before outcomes

Complete the [prelaunch gate](stage9-heldout-prelaunch-decision-record.md).
In a custodian-controlled Git checkout that retains the exact selected frozen
code commit and full history, commit the complete
\`research/stage9/registration.json\` at an immutable *later* registration commit.
Preserve independent signed approval/timestamp evidence externally.

A machine-readable pointer to this **external** approval must also exist
as a separately controlled JSON file (not proof of signatures):

~~~json
{
  "protocol_version": "stage9-heldout-operator-release-record-v1",
  "registration_digest": "FULL_CANONICAL_REGISTRATION_SHA256",
  "frozen_implementation_commit": "FULL_40_CHARACTER_SOURCE_COMMIT",
  "registration_commit": "FULL_40_CHARACTER_REGISTRATION_COMMIT",
  "authorization": "GO",
  "research_owner": "ACTUAL_NAMED_RESEARCH_OWNER",
  "custodian": "ACTUAL_NAMED_INDEPENDENT_CUSTODIAN",
  "operator": "ACTUAL_NAMED_OPERATOR",
  "independent_evaluator": "ACTUAL_NAMED_EVALUATOR",
  "approval_evidence_ref": "SECURE_LOCATION_OF_SIGNED_APPROVAL",
  "independent_timestamp_ref": "SECURE_LOCATION_OF_INDEPENDENT_TIMESTAMP"
}
~~~

The CLI checks required field consistency but **cannot verify a human
signature**, whether those people are genuinely independent, or that anyone
has not inspected results. The independent operator is accountable for
authenticating the external originals. The runner is not an approval authority.

## 3. Run the complete registered matrix in isolation

**Only after a real externally witnessed GO.** From the repository root,
with \`HEAD\` *exactly* at the registration commit and no uncommitted source
changes, run:

~~~bash
python -m lab.stage9_heldout_runner run \
  --repo . \
  --registration research/stage9/registration.json \
  --registration-commit FULL_40_CHARACTER_REGISTRATION_COMMIT \
  --manifest-index results/stage9/physical-manifest-index.json \
  --manifest-root results/stage9/raw-manifests \
  --external-go-record results/stage9/private-release-record.json \
  --output-root results/stage9/raw
~~~

The output root must **not already exist**. No scientific data is accessed
without the explicit registration, manifest custody, and human GO references.
The resulting \`raw/operator-run-index.json\` is an unscored receipt. Each
\`cell-XXX-YYY\` stores its own original/replay journals and causal-owner
snapshots, plus \`bench-only-world-truth.json\` for external bench custody.
Store the original, replay and bench inputs separately under operator control.
Preserve failures and incomplete runs. Do not rerun only favorable cells.

**Important:** a \`Stage9Runtime\` seeded world may genuinely acquire zero
candidate causal rules. Do not inject extra hypotheses, relabel witnesses,
drop a negative world or change preregistered rules to manufacture a pass.

## 4. Independently annotate original observations

An authorized evaluator examines physical source/Memory provenance and
bench-only oracle truth, then writes a separate complete
\`stage9-heldout-independent-annotations-v1\` JSON document:

~~~json
{
  "protocol_version": "stage9-heldout-independent-annotations-v1",
  "registration_digest": "FULL_CANONICAL_REGISTRATION_SHA256",
  "runs": [
    {
      "world_id": "REAL_REGISTERED_WORLD_ID",
      "seed": 0,
      "known_cause_cases": [],
      "naturally_acquired_false_candidates": []
    }
  ]
}
~~~

This is **illustrative syntax**, not a valid complete campaign: enumerate
every preregistered world × seed cell. Use exactly the row schemas already
specified by \`stage9_scientific_assessment.py\`:

- Known-cause row: \`id\`, \`episode_ref\`, \`observation_ref\`,
  \`ground_truth\` (\`self\`, \`world\`, \`none\`), \`attribution\`
  (\`self_compatible\`, \`world_justified\`, \`uncertain\`).
- Naturally acquired false candidate: \`id\`, \`contingency_ref\`,
  \`episode_ref\`, \`observation_ref\`, \`causal_status\` (one of the
  scorer's actual canonical causal status values).

Each observation must be a real committed physical transition and a member
of the claimed *closed* Memory episode. The annotations must not change
what the agent learned. Retain signed ground-truth justifications, missing
observations, no-effect controls, conflicts and all failures externally.

## 5. Package and validate the original evidence

With the original isolated archived files still available:

~~~bash
python -m lab.stage9_heldout_runner package \
  --registration research/stage9/registration.json \
  --runs-root results/stage9/raw \
  --annotations results/stage9/private-annotations.json \
  --evidence results/stage9/heldout.json \
  --raw-index results/stage9/raw-artifact-index.json
~~~

This produces the exact existing v2 evidence and v4 raw index format, runs
the provisional scorer and independently audits raw journal/Memory provenance.
Its output \`scientific_verdict\` remains \`null\` and
\`golden_stage9_frozen\` remains \`false\`. A failed or zero-denominator
assessment must be retained, not repaired retroactively.

Commit the evidence JSON at a **later** evidence commit on the same isolated
Git lineage, leaving the registration and implementation unchanged. Preserve
the original files with independently controlled access. Then run the complete
read-only chronology/custody assessment via the commands in the operator
runbook, including \`lab.stage9_independent_handoff\` and the independent
INV-25 paired simulator/safety comparison. A coherent software receipt
**never** constitutes a scientific PASS or scientific Golden.

## Development-only validation

Use **synthetic/public development worlds only** to run
\`python -m unittest tests.test_stage9_heldout_runner -v\` and the ordinary
Stage-9 software reference checks. These tests are not a campaign. They
exercise the actual Stage-9 runtime path, external event logging, full
original/replay equality, frozen parameter reconstruction, strict JSON,
no implicit GO, and rejection of invented physical evidence. Neither
this document nor green CI authorizes opening hidden worlds/seeds.
