# Individual Zero · Stage 9
## Independent held-out campaign execution and scientific evaluation manual

**Manual version:** 1.1 · 10 October 2026  
**Language:** English  
**Audience:** independent world/seed custodian, campaign operator, independent scientific evaluator, protocol owner  
**Status:** OPERATING INSTRUCTIONS, **NOT** campaign authorization or scientific evidence. Default decision: **NO-GO**.  
**Repository:** `josselin-orta-lab/individual-zero`  
**Integrated branch:** `main` (Stages 1–9, including the parallel Stage 5 implementation)  
**Example integrated software baseline, not a scientific freeze:** `b304ebda7facf8ba285408e87090727dafc43bcb`  
**Integration:** [PR #20](https://github.com/josselin-orta-lab/individual-zero/pull/20) merged; historical PRs #11–#18 closed as superseded. No scientific approval was granted.

> **Read this first.** This manual explains how to prepare, conduct, preserve, and independently assess the campaign. It provides **neither** scientifically calibrated experimental parameters **nor** the withheld worlds/seeds **nor** approved scientific thresholds. These must be supplied or selected prospectively under independent control. **If any are missing, stop at NO-GO.** Never substitute repository unit-test fixtures for scientific data.

**Édition française :** [Manuel d'évaluation indépendante du Stage 9](stage9-independent-heldout-evaluation-manual.fr.md).

### Contents

1. [Understanding the assignment and responsibilities](#1-understanding-the-assignment-and-responsibilities)
2. [Prerequisites and materials to obtain](#2-prerequisites-and-materials-to-obtain)
3. [Preparing the independent computer](#3-preparing-the-independent-computer)
4. [Preparing the frozen manifests and worlds](#4-preparing-the-frozen-manifests-and-worlds)
5. [Preparing and checking preregistration](#5-preparing-and-checking-preregistration)
6. [Sealing the protocol in Git](#6-sealing-the-protocol-in-git)
7. [Creating indexes and authorization documents](#7-creating-indexes-and-authorization-documents)
8. [Preflight checks and the GO / NO-GO decision](#8-preflight-checks-and-the-go--no-go-decision)
9. [Running the campaign](#9-running-the-campaign)
10. [Finding and annotating evidence](#10-finding-and-annotating-evidence)
11. [Packaging and sealing the report](#11-packaging-and-sealing-the-report)
12. [Performing the final independent audit](#12-performing-the-final-independent-audit)
13. [Interpreting results and issuing a verdict](#13-interpreting-results-and-issuing-a-verdict)
14. [Handling anomalies without losing scientific value](#14-handling-anomalies-without-losing-scientific-value)
15. [Delivering the evidence package and closing the assignment](#15-delivering-the-evidence-package-and-closing-the-assignment)
16. [Appendices: templates and quick reference](#16-appendices-templates-and-quick-reference)

---

## 1. Understanding the assignment and responsibilities

### 1.1. The project in three sentences

**Individual Zero** is experimental software simulating an artificial individual in a deterministic world. **Stage 9** studies how the individual distinguishes correlation from causation, attributes the consequences of actions, and uses certain causal knowledge in its safety and simulation mechanisms. Your assignment is **not** to make the agent pass: it is to determine whether it meets or fails criteria **set before the experiment**, on worlds and seeds separate from those used during development.

**Glossary:**

| Term | Practical meaning |
| --- | --- |
| *held-out* | Worlds, configurations, and seeds reserved from development, unknown to developers until the authorized disclosure point. |
| *World* | Physical rules, configuration, generator, and external events constituting a simulated living environment. |
| *Seed* | Integer that controls reproducible random generation, including layout and berry identity. |
| *Cell* | One **world × seed** combination, executed and replayed. |
| *Causal journal* | Chronological sequence of canonical events connected by cryptographic hashes. |
| *Closed Memory episode* | Completed autobiographical episode included in the individual's saved Memory state. |
| *Oracle / ground truth* | Complete information about the world's causes and state. It belongs **only to the independent bench** and must not be accessible to the individual. |
| *Preregistration* | Research protocol, metrics, and choices fixed **before** inspecting reserved outcomes. |
| *Exact replay* | Second execution producing byte-for-byte identical journal and causal-state outputs. |
| *Golden* | Accepted scientific reference after complete review. **This procedure establishes no Stage-9 Golden.** |
| `etablie` | Established causal rule that may affect the simulator as permitted by the normative design. |
| `etabli_pour_securite` | Safety rule authorizing a veto **without** changing simulator predictions or artificially modifying `R_a`. |
| `INV-25` | Invariant separating predictive consequences from safety veto rules, requiring explicit review. |

### 1.2. Who is responsible for what?

| Role | Responsibility and expected evidence | Critical prohibition |
| --- | --- | --- |
| **Research owner** | Approves hypotheses, calibrated parameters, sampling plan, thresholds, counts, exclusions, stopping rules and responsible persons; signs **before** outcomes. | Changing decision rules after seeing results. |
| **Independent custodian** | Selects or holds worlds, seeds, distributions and control truth; keeps an access log. | Premature disclosure of secrets to developers. |
| **Operator** | Installs the frozen software, executes **every** cell, and preserves original journals and environment evidence. | Modifying code or dropping cells on the basis of performance. |
| **Independent evaluator** | Reviews original files, causal conditions, chronology, metrics, errors and `INV-25`; signs a verdict. | Treating CI `SUCCESS` or a SHA-256 hash as scientific certification. |

One individual may hold multiple responsibilities **only** when conflicts of interest and compensating controls have been independently reviewed and accepted. An AI agent involved in developing the software is **not** the independent evaluator.

### 1.3. Authoritative sources

- **Normative and overriding:** `docs/architecture/reference/en/mvp-specification-v1.2.1.md`, especially §§9.6, 13.2, 19.5, 20.3 Stage 9 and `INV-25`. Never edit it.
- **Pre-launch decision record:** `docs/research/stage9-heldout-prelaunch-decision-record.md`.
- **Scientific preregistration template:** `docs/research/stage9-scientific-preregistration-template.md`.
- **Original operator runbook:** `docs/research/stage9-independent-heldout-operator-runbook.md`.
- **Executor documentation:** `docs/research/stage9-heldout-executor.md`.
- **Executable:** `src/lab/stage9_heldout_runner.py` with two subcommands, `run` and `package`.

If any instructions conflict, **English normative v1.2.1 prevails**. Stop and obtain the research owner's resolution **before** results are observed.

---

## 2. Prerequisites and materials to obtain

### 2.1. Before accessing reserved data

The research owner must provide all of the following, together with references to their approvals:

- [ ] Real identities and signed acceptance of the owner, custodian, operator and evaluator, plus conflict-of-interest disclosures.
- [ ] Exact source code identified by a **full 40-character Git SHA**. The currently known integrated candidate is `b304ebda7facf8ba285408e87090727dafc43bcb`. **This is not an approved scientific freeze.** The research owner may select a different commit after inspection; if so, update every `FREEZE_SHA` reference before preregistration.
- [ ] Complete Stage-9 parameters **calibrated using authorized calibration worlds**, including relevant P-xx parameters, actually trained Equipment model and documented rationale.
- [ ] Prospectively approved definitions for known-cause worlds (**positive controls**) and worlds without the relevant causal relationship (**negative/null controls**), including generation and verification methods.
- [ ] Sampling plan, secret seeds, independence criteria, run lengths, termination, thresholds, metrics, statistical limits and invalidation rules.
- [ ] Annotation criteria for known causes, no-effect controls, attribution, **naturally acquired** false causal hypotheses and evidence from closed Memory episodes.
- [ ] Comparison plan for `INV-25` and verification of oracle/individual separation.
- [ ] An **isolated** location to retain originals and signatures with independently verifiable timestamps.

**Important:** the runner is engineering infrastructure, not an experimental design. Values from `stage9_reference_fixture.py` are **software-compatibility fixtures**, **not** authorized scientific calibration. Without an approved, calibrated parameter registry and trained Equipment artifact: **NO-GO**.

### 2.2. Scientific limitations requiring human review

1. The runner supports frozen `exact_transition_table` Equipment. It **does not train** Equipment or adapt it to held-out observations. Unknown inputs may be rejected rather than assigned invented predictions.
2. The generator uses the seed to create deterministic geometry and berry effects. The external scenario schedule is specified **per world**, not generated automatically for every seed.
3. Available external scenario operations include `set_body`, `place_resource`, `place_creature`, `remove_creature`, `set_danger_zone` and `set_lethal_zone`. **There is no general-purpose, per-seed independent random-reward generator.** If a valid negative control requires randomness not expressible through these mechanisms, develop and revalidate that capability **before freezing** or remain **NO-GO**. A world called `null` is not automatically a causally valid null world.
4. `bench-only-world-truth.json` records the actual initial and final world state and realized configuration, **not independently certified per-step causal truth**. Classifications require an independent evaluator's justification and, where needed, additional physical evidence.
5. A technically perfect run can still be **not evaluable** when there are no admissible observations or naturally acquired false causal candidates.

---

## 3. Preparing the independent computer

These instructions assume **Linux or macOS, Bash, Git, and Python 3.11 or 3.12**. The pre-integration Stage-9 branch passed **652 tests** on each version with historical diagnostics. The integrated tree, also containing Stage 5, passed **678 tests on Python 3.12**. Exhaustive validation of the combined tree on both Python versions has **not** been claimed. Untested native Windows environments require their own approved setup procedure.

### 3.1. Create an isolated workspace

On a computer or account independent of the developers, with encrypted storage and controlled access, open a terminal:

```bash
umask 077
git --version
python3 --version
```

**Expected:** Git prints a version and Python reports `3.11.x` or `3.12.x`. Otherwise, install a supported Python version before proceeding.

With appropriate GitHub access:

```bash
git clone --no-single-branch \
  git@github.com:josselin-orta-lab/individual-zero.git \
  individual-zero-stage9-private
cd individual-zero-stage9-private

# The research owner must explicitly approve THIS commit or another final one.
export FREEZE_SHA="b304ebda7facf8ba285408e87090727dafc43bcb"
git cat-file -t "$FREEZE_SHA"
git switch --detach "$FREEZE_SHA"
git switch -c stage9-independent-private

# Prevent accidental pushes to the shared development repository.
git remote remove origin

git rev-parse HEAD
git rev-parse --is-shallow-repository
git remote -v
```

**Expected:**

- `git cat-file -t` prints `commit`.
- `git rev-parse HEAD` returns **exactly** the approved `FREEZE_SHA`.
- `git rev-parse --is-shallow-repository` returns **`false`**.
- `git remote -v` displays **no** destinations.

If the custodian cannot access the private repository, the owner may provide a **complete, authenticated Git bundle** containing the chosen commit and its history. Verify its source and clone it **outside development systems**. A ZIP archive is insufficient because the tools audit Git ancestry.

> **Confidentiality.** The preregistration file stores the **actual withheld numeric seeds in plaintext**. Never push this private branch, expose it to `main` or a development PR, share it with coding assistants, or run the campaign in GitHub Actions whose logs are accessible to developers. Removing `origin` reduces the risk of an accidental push.

### 3.2. Install the environment

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
python --version
```

**Expected:** installation completes without errors; Python is 3.11 or 3.12. Independently record the Python version, OS, installed dependencies, machine and environment, date/time and operator identity, plus the output of `pip freeze`:

```bash
mkdir -p research/stage9 results/stage9/raw-manifests/frozen \
  results/stage9/raw-manifests/worlds results/stage9/receipts
python -m pip freeze > results/stage9/receipts/python-dependencies.txt
python -m pip --version > results/stage9/receipts/pip-version.txt
python --version > results/stage9/receipts/python-version.txt 2>&1
```

Do **not** execute the campaign runner's `run` command at this stage.

### 3.3. Local software verification **without reserved data**

```bash
python -m unittest tests.test_stage9_heldout_runner \
  tests.test_stage9_heldout_operator_integration -v

# Optional, broader software verification:
python -m unittest discover -s tests -q
```

**Expected:** final output `OK`, with no `FAILED` or `ERROR`. Test totals may vary if the approved code differs from this manual's candidate. Never switch source branches silently after freeze to get a green result. These are **synthetic software tests**, not evidence about the independent campaign.

---
## 4. Preparing the frozen manifests and worlds

### 4.1. Inventory of the files required **before preregistration**

The custodian retains all **original** files at:

```text
results/stage9/raw-manifests/
├── frozen/
│   ├── generator.json          # registered world generator configuration
│   ├── parameters.json         # complete Stage9 and innate safety configuration
│   ├── equipment.json          # frozen Equipment model and transition table
│   └── ontology.json           # identity/version of the ontology registry
└── worlds/
    ├── calibration-1.json     # illustrative calibration world name
    ├── positive-1.json        # illustrative known-cause world name
    └── null-1.json            # illustrative negative-control world name
```

These names are **examples only**. The exact worlds and their number must come from the approved protocol. Having one positive and one negative world is not necessarily enough for adequate statistical power.

| File | Required information | Technical validation | Scientific reviewer |
| --- | --- | --- | --- |
| `frozen/generator.json` | Version; numbers of water sources, resource cells, danger cells and creatures; resource amounts; berry benefits and toxicity; seeds applied per cell. | `stage9-heldout-world-generator-v1`; `WorldGenerationConfig.validate()`; raw-file SHA-256. | Owner and custodian. |
| `frozen/parameters.json` | Entire `Stage9Config`, inherited `Stage8Config` and earlier configs, P-xx parameters, `SafetyProtocolConfig` in `campaign` mode, protected-integrity threshold and innate rules. | `stage9-heldout-parameters-v1`; strict reconstruction of every dataclass. | Research owner, after external calibration. |
| `frozen/equipment.json` | `EquipmentArtifact`, training corpus provenance, version, `model_kind=exact_transition_table`, and `ExactTransitionRecord` entries. | `stage9-heldout-equipment-v1`; exact input index, digest and Equipment validation. | Research owner, with training provenance. |
| `frozen/ontology.json` | `protocol_version`, identity and version of the ontology registry, reference for actual definitions. | The runner checks the protocol version and raw **bytes**, not full meaning. | Evaluator, by comparison with the frozen code's ontology. |
| `worlds/*.json` | World physics, initial body parameters, version, complete external scenario and world identity. | `stage9-heldout-physical-world-v1`; `WorldPhysicsConfig.validate()`; scenario and SHA-256. | Custodian and evaluator: genuinely distinct known/null causal conditions. |

### 4.2. `generator.json`: editable structural template

**ILLUSTRATIVE STRUCTURE, NOT READY TO RUN.** Replace every `null` with a **calibrated, approved** value. Do not choose numbers merely because a validator accepts them.

```json
{
  "protocol_version": "stage9-heldout-world-generator-v1",
  "generation": {
    "version": "APPROVED_GENERATOR_VERSION",
    "water_source_count": null,
    "berry_a_cells": null,
    "berry_b_cells": null,
    "wood_cells": null,
    "stone_cells": null,
    "creature_count": null,
    "danger_zone_count": null,
    "quantity_per_resource_cell": null,
    "nutritious_food_gain": null,
    "toxic_food_gain": null,
    "toxic_integrity_delta": null
  }
}
```

All `*_count` values and `quantity_per_resource_cell` are **integers**; gains and bodily changes are **finite numbers**. `toxic_integrity_delta` must be strictly **negative**. Normative world physics uses a **32 × 32** grid and a **300-step** day, of which **100 steps** are night.

### 4.3. `parameters.json` and `equipment.json`: do not manufacture these manually

The research owner must supply artifacts that have **actually been calibrated and frozen**. The runner provides an export function for an already prepared Stage-9 runtime:

```python
from lab.stage9_heldout_runner import export_frozen_stage9_assets

# `calibrated_runtime` must already exist and come from the
# approved calibration process. DO NOT construct it using
# stage9_reference_fixture as supposed scientific calibration.
parameters_document, equipment_document = export_frozen_stage9_assets(
    calibrated_runtime
)
```

This is an **API example**, not an immediately executable Bash command: `calibrated_runtime` must be supplied. If no such object or equivalent valid JSON artifacts exist: **NO-GO**.

The root of `parameters.json` must contain **exactly** these fields:

```json
{
  "protocol_version": "stage9-heldout-parameters-v1",
  "stage9_config": {},
  "safety_config": {},
  "protected_integrity_threshold": null,
  "innate_safety_facts": {}
}
```

This example is deliberately **incomplete**. `stage9_config` contains, among other things, the `stage8`, `causal` (P-35/P-36 thresholds and rules) and `agency` (P-47 comparator) subconfigurations, and every required inherited configuration from previous stages, with their **exact versions**. `safety_config.mode` must be `"campaign"`. `innate_safety_facts` holds innate safe/dangerous positions or resource lists. `protected_integrity_threshold` must be strictly between 0 and 100. The exporter checks structural consistency **only if the supplied source data are already valid**.

The root of `equipment.json` must contain exactly:

```json
{
  "protocol_version": "stage9-heldout-equipment-v1",
  "artifact": {},
  "records": []
}
```

Again, empty objects mean **placeholders** awaiting owner-supplied data. `artifact` describes the trained Equipment (`version`, `corpus_version`, `corpus_sha256`, `model_kind`, `model_payload`, `training_metadata`), while `records` contains frozen transitions (`input_sha256`, `next_state`, `effects`, `terminal`). These must agree with the trained model's identity. Do not fill missing transitions from held-out worlds.

The minimal root shape of `ontology.json` is:

```json
{
  "protocol_version": "stage9-heldout-ontology-v1",
  "version": "ACTUAL_REGISTRY_VERSION_TO_SUPPLY",
  "artifact_ref": "PROVENANCE_REFERENCE_TO_SUPPLY"
}
```

**Important:** the runner does not automatically compare the ontology's meaning with the runtime's actual ontology; the evaluator must inspect and sign off on this comparison.

### 4.4. `worlds/*.json` files

Each world has this **exact root shape**:

```json
{
  "protocol_version": "stage9-heldout-physical-world-v1",
  "world_id": "ACTUAL_WORLD_ID",
  "physics": {},
  "scenario": {
    "id": "ACTUAL_SCENARIO_ID",
    "version": "ACTUAL_SCENARIO_VERSION",
    "events": []
  }
}
```

An empty `physics` object is **not valid for execution**. It must contain all fields produced by `WorldPhysicsConfig.as_dict()`:

- `version` (string), `width=32`, `height=32`, `day_steps=300`, `night_steps=100`, and `night_start_step` (integer position within the day).
- `initial_body` (`energy`, `food`, `water`, `integrity`, each from 0 to 100), and `initial_position` (`x`, `y` inside the world boundaries).
- `food_decay_per_step`, `water_decay_per_step`, `sleep_energy_gain`, `rest_integrity_gain`, `drink_water_gain`, `creature_damage`, `danger_zone_damage` (nonnegative numbers subject to their actual constraints).
- `action_energy_costs` (cost of **each** primitive), `berry_effects` (berries `berry_a` and `berry_b`, each with `food_gain` and `integrity_delta`), `tool_recipe` (`wood_required`, `stone_required`, `collection_gain`), `shelter_stones_required=4`.

The generator then determines the layout and berry effects from the seed. The relationship between world physics, world generation, and scenario events must be **specified and reviewed in advance**. Never change a world's physics after inspecting its score.

Example **event syntax** (illustrative, not scientific certification):

```json
{
  "t_monde": 25,
  "sequence": 0,
  "operation": "set_body",
  "payload": {"water": 75.0}
}
```

Each event is a **logged external input** occurring at its `t_monde` (from 1 through `steps_per_run`) with a unique `(t_monde, sequence)` pair. Artificial repetition, unphysical values, or feeding oracle labels into the individual invalidate the test.

### 4.5. The custodian selects the held-out seeds

The number of seeds comes from the **approved design**, never from an arbitrary number in this manual. The custodian may use a cryptographic random source to produce a private list and verify that it does not overlap calibration seeds:

```bash
python - <<'PY'
import json, secrets
from pathlib import Path

count = int(input('Already-approved number of held-out seeds: '))
calibration = json.loads(input('JSON list of calibration seeds: '))
assert count >= 2 and isinstance(calibration, list)
assert all(type(x) is int and x >= 0 for x in calibration)
selected = set()
while len(selected) < count:
    seed = secrets.randbits(64)
    if seed not in calibration:
        selected.add(seed)
path = Path('results/stage9/private-seed-selection.json')
with path.open('x', encoding='utf-8') as stream:
    json.dump({'calibration_seeds': calibration,
               'holdout_seeds': sorted(selected)}, stream, indent=2)
    stream.write('\n')
path.chmod(0o600)
print('Private selection written. Do not print the seeds.')
PY
```

**Expected:** a new private file, without disclosing numbers in terminal output. The custodian must independently verify the sampling procedure and copy the **actual** lists into `registration.json`, which is later kept in **isolated Git history**. Randomly drawing integers does **not**, by itself, prove that the worlds, lived observations, or statistical samples are independent. Never commit `private-seed-selection.json` to the shared development repository.

### 4.6. Validate files and obtain original-byte digests

Once **real, approved** JSON files exist, these checks can detect malformed frozen assets **before** preregistration is sealed:

```bash
python - <<'PY'
from pathlib import Path
from lab.stage9_heldout_runner import (
    _json_file, _frozen_parameters, _frozen_equipment, _typed,
    GENERATOR_VERSION,
)
from lab.world_generation import WorldGenerationConfig
root = Path('results/stage9/raw-manifests/frozen')
params = _frozen_parameters(_json_file(root / 'parameters.json'))
equipment = _frozen_equipment(_json_file(root / 'equipment.json'))
generator = _json_file(root / 'generator.json')
assert generator['protocol_version'] == GENERATOR_VERSION
assert set(generator) == {'protocol_version', 'generation'}
_typed(WorldGenerationConfig, generator['generation'])
assert _json_file(root / 'ontology.json')['protocol_version'] == 'stage9-heldout-ontology-v1'
print('FROZEN_MANIFESTS_DECODABLE_REQUIRES_SCIENTIFIC_REVIEW')
PY

sha256sum results/stage9/raw-manifests/frozen/*.json
sha256sum results/stage9/raw-manifests/worlds/*.json
sha256sum docs/architecture/reference/en/mvp-specification-v1.2.1.md
```

**Expected:** a manifest-decoding marker, followed by a **64-character hexadecimal digest** for each file. On macOS, use `shasum -a 256` with the same file paths if `sha256sum` is unavailable. **Matching SHA-256 values establish byte identity, not the scientific validity of a world.** Retain the digests privately.

---

## 5. Preparing and checking preregistration

### 5.1. The one protocol file read by the tools

Create, inside the **isolated Git checkout**: `research/stage9/registration.json`.

The required schema is `stage9-preregistration-schema-v2`, with **exactly** the following fields. This JSON is a **DELIBERATELY INCOMPLETE TEMPLATE**, designed to be rejected until actual values and calibration evidence replace the placeholders:

```json
{
  "protocol_version": "stage9-preregistration-schema-v2",
  "registration_id": "REPLACE_WITH_EXPERIMENT_ID",
  "author": "REPLACE_WITH_REAL_RESEARCH_OWNER",
  "normative_specification": "docs/architecture/reference/en/mvp-specification-v1.2.1.md",
  "normative_specification_sha256": "REPLACE_WITH_ACTUAL_64_HEX_SHA256",
  "frozen_implementation_commit": "b304ebda7facf8ba285408e87090727dafc43bcb",
  "world_generator_version": "REPLACE_WITH_GENERATOR_VERSION",
  "world_generator_sha256": "REPLACE_WITH_ACTUAL_64_HEX_SHA256",
  "equipment_sha256": "REPLACE_WITH_ACTUAL_64_HEX_SHA256",
  "parameter_registry_sha256": "REPLACE_WITH_ACTUAL_64_HEX_SHA256",
  "ontology_sha256": "REPLACE_WITH_ACTUAL_64_HEX_SHA256",
  "calibration_world_sha256": {
    "calibration:1": "REPLACE_WITH_ACTUAL_64_HEX_SHA256"
  },
  "holdout_world_sha256": {
    "holdout:positive": "REPLACE_WITH_ACTUAL_64_HEX_SHA256",
    "holdout:null": "REPLACE_WITH_ACTUAL_64_HEX_SHA256"
  },
  "calibration_world_ids": ["calibration:1"],
  "holdout_world_ids": ["holdout:positive", "holdout:null"],
  "positive_world_ids": ["holdout:positive"],
  "negative_world_ids": ["holdout:null"],
  "calibration_seeds": [null],
  "holdout_seeds": [null, null],
  "steps_per_run": null,
  "minimum_naturally_acquired_candidates": null,
  "maximum_superstitious_rule_rate": null,
  "minimum_known_cause_accuracy": null,
  "confidence_method": "wilson_95",
  "candidate_definition": "REPLACE_WITH_PRECISE_DEFINITION",
  "ground_truth_definition": "REPLACE_WITH_CAUSAL_AND_CONTROL_RULES",
  "independent_episode_definition": "REPLACE_WITH_INDEPENDENCE_DEFINITION",
  "exclusion_rule": "REPLACE_WITH_PROSPECTIVE_EXCLUSIONS",
  "stop_rule": "REPLACE_WITH_PROSPECTIVE_STOPPING_RULE",
  "replay_rule": "REPLACE_WITH_APPROVED_BYTE_EXACT_REPLAY_RULE"
}
```

**Never run the campaign with this sample.** Fill in the actual values privately, then validate the JSON. Example world names say nothing about the real experiment or an adequate sample size.

### 5.2. What to enter in each field group

| Fields | Type and real information to enter |
| --- | --- |
| `registration_id`, `author` | Nonempty strings, actual research identity and signed protocol reference. Independently signed timestamps are stored **separately**; the JSON schema has no timestamp field. |
| `normative_specification` | Exact path to **English v1.2.1**, unchanged. |
| `normative_specification_sha256` | SHA-256 of the normative document's original bytes at freeze. |
| `frozen_implementation_commit` | Full **approved** 40-hex code SHA. The value in the template is just a candidate. |
| `world_generator_version` | Exact generator version in `generator.json`. |
| `world_generator_sha256`, `equipment_sha256`, `parameter_registry_sha256`, `ontology_sha256` | SHA-256 of the **original bytes** of each of the four frozen manifests. |
| `calibration_world_ids`, `holdout_world_ids` | Arrays of unique world identifiers; the two sets must be disjoint. At least **one** calibration world and **two** held-out worlds (validator minima). |
| `calibration_world_sha256`, `holdout_world_sha256` | Mappings `world ID -> full physical manifest file SHA-256`. Every ID needs a hash; no duplicate physical manifest between worlds or calibration. |
| `positive_world_ids`, `negative_world_ids` | Disjoint groups jointly covering **every** `holdout_world_ids` member, at least one from each group. Classification is decided prospectively by the bench. |
| `calibration_seeds`, `holdout_seeds` | Arrays of **nonnegative integers**, distinct within each list and disjoint across lists. At least **one** calibration seed and **two** held-out seeds (software minima, not statistical power analysis). Held-out seeds are **secret**. |
| `steps_per_run` | Strictly positive integer applied to all cells, chosen in advance. Interrupted runs must be retained and dealt with according to the approved stopping/exclusion rules. |
| `minimum_naturally_acquired_candidates` | Integer ≥ 1, minimum count of genuinely, spontaneously acquired false rules; defines a required positive denominator. |
| `maximum_superstitious_rule_rate` | Numeric fraction between 0 and 1: maximum acceptable rate, fixed **before** the experiment. |
| `minimum_known_cause_accuracy` | Numeric fraction between 0 and 1: minimum acceptable attribution accuracy. |
| `confidence_method` | Exactly **`wilson_95`**; no other method is implemented by the current runner/scorer. |
| `candidate_definition` | Exact criteria for a *naturally acquired false causal rule* (unit: distinct canonical contingency per cell, not repeated observations of the same rule). |
| `ground_truth_definition` | Independent classification process for `self` / `world` / `none`, positive/null controls, and multiple-cause resolution. |
| `independent_episode_definition` | Rules establishing lived observation provenance, controlled contexts and closed Memory episodes. An episode ID does not, by itself, establish statistical independence. |
| `exclusion_rule`, `stop_rule`, `replay_rule` | Detailed texts specifying **before execution** how failures, safety blocks, rejected provenance, early stopping, matrix completeness, byte-exact comparisons and unfavorable cases are handled and reported. |

Expected total coverage is **number of held-out worlds × number of held-out seeds**. The runner follows the registered Cartesian product, not a favorable subset selected afterwards.

### 5.3. Check the completed registration

```bash
python -m json.tool research/stage9/registration.json >/dev/null
python -m lab.stage9_scientific_preregistration \
  --manifest research/stage9/registration.json \
  > results/stage9/receipts/registration-preflight.json
cat results/stage9/receipts/registration-preflight.json
```

**Expected, when every field has a valid value:**

```json
{
  "registration_status": "draft_requires_independent_git_seal",
  "registration_digest": "ACTUAL_CANONICAL_64_HEX_DIGEST",
  "launch_authorized_by_preflight": false,
  "independent_heldout_custody_attested_by_preflight": false,
  "independent_evaluator_approved_by_preflight": false,
  "scientific_verdict": null,
  "golden_stage9_frozen": false
}
```

The real output also contains an `outstanding` list. The block above is an **explanatory excerpt**, not a literal complete response.

**Meaning:** the format is internally consistent and has a canonical content identity, **but has not been independently sealed, approved, or executed**. A missing field, invalid digest, overlapping worlds/seeds, missing threshold, or noninteger seed raises an error/nonzero exit status. **STOP** if this occurs.

The `registration_digest` hashes the **canonical causal JSON representation**, not the output of `sha256sum registration.json`. Those hashes may differ; do not confuse them.

---
## 6. Sealing the protocol in Git

### 6.1. Signatures and proof of prior registration

Before any held-out execution:

1. Obtain the research owner's signature on the complete protocol, parameter values, thresholds, sample counts, exclusion and stopping rules.
2. Have the custodian attest world/seed independence, confidentiality, and possession of the original files.
3. Preserve an **independent timestamped proof of existence** separately, such as a signed record from an independent trusted witness, without disclosing seeds or withheld oracle truth.
4. Confirm that the protocol commit descends from the frozen implementation commit **without changes to `src/`, `pyproject.toml`, or the English normative specification**.

A Git commit's own timestamp **does not by itself prove** that the protocol was approved before data were seen.

### 6.2. Commit the protocol **only in isolated Git history**

```bash
git status --short
git diff -- src pyproject.toml \
  docs/architecture/reference/en/mvp-specification-v1.2.1.md

# Execute ONLY AFTER obtaining signatures and checking confidentiality.
git add research/stage9/registration.json
git commit -m "Prospective Stage 9 heldout registration"
export REGISTRATION_COMMIT="$(git rev-parse HEAD)"

printf 'FREEZE_SHA=%s\nREGISTRATION_COMMIT=%s\n' \
  "$FREEZE_SHA" "$REGISTRATION_COMMIT"
git merge-base --is-ancestor "$FREEZE_SHA" "$REGISTRATION_COMMIT"
```

**Expected:** `git diff` shows **no changes** to frozen paths; the new commit differs from `FREEZE_SHA`; `git merge-base --is-ancestor` exits with **status 0**. The isolated repository must **still have no remote**.

**Warning:** the actual numeric seeds are now stored **in plaintext in local Git history**, even if you later delete them from the working file. Confidentiality requires protecting **the full history**.

---

## 7. Creating indexes and authorization documents

### 7.1. `results/stage9/physical-manifest-index.json`

This is a **path index**, not a replacement for original manifests or a modification of the scientific protocol. Example structure to adapt to the **actual registered IDs**:

```json
{
  "protocol_version": "stage9-registered-physical-manifest-index-v1",
  "registration_digest": "ACTUAL_CANONICAL_64_HEX_DIGEST",
  "frozen_manifests": {
    "world_generator": "frozen/generator.json",
    "equipment": "frozen/equipment.json",
    "parameter_registry": "frozen/parameters.json",
    "ontology": "frozen/ontology.json"
  },
  "calibration_worlds": {
    "calibration:1": "worlds/calibration-1.json"
  },
  "holdout_worlds": {
    "holdout:positive": "worlds/positive-1.json",
    "holdout:null": "worlds/null-1.json"
  }
}
```

Replace `registration_digest` with the actual value returned in `registration-preflight.json`. All paths are **relative** to `results/stage9/raw-manifests`. They must exist, be unique, contain no `..`, and not alias any other file through symlinks or hard links. IDs must **exactly** match the sealed protocol.

### 7.2. `results/stage9/private-release-record.json`

After preregistration is committed, **and only if the scientific decision record has genuinely been approved**, prepare:

```json
{
  "protocol_version": "stage9-heldout-operator-release-record-v1",
  "registration_digest": "ACTUAL_CANONICAL_64_HEX_DIGEST",
  "frozen_implementation_commit": "b304ebda7facf8ba285408e87090727dafc43bcb",
  "registration_commit": "FULL_40_HEX_REGISTRATION_COMMIT_SHA",
  "authorization": "GO",
  "research_owner": "ACTUAL_NAME_AND_REFERENCE",
  "custodian": "ACTUAL_NAME_AND_REFERENCE",
  "operator": "ACTUAL_NAME_AND_REFERENCE",
  "independent_evaluator": "ACTUAL_NAME_AND_REFERENCE",
  "approval_evidence_ref": "VERIFIABLE_PRIVATE_SIGNED_APPROVAL_LOCATION",
  "independent_timestamp_ref": "VERIFIABLE_PRIVATE_INDEPENDENT_TIMESTAMP_LOCATION"
}
```

These **11 fields** are required, with no extra fields allowed. Identities and evidence references must be **real, nonempty, and traceable**. Set `authorization` to `GO` **only after** the genuine human-signed decision. Do not write `GO` just to unlock the runner. The software **does not cryptographically verify** those signatures or the stated people's independence. That remains the operator's and evaluator's responsibility.

### 7.3. The scientific record to be completed by people

In a **dated and signed copy** of `docs/research/stage9-heldout-prelaunch-decision-record.md`, complete sections A through D: appointments, conflicts, data custody, code freeze, preregistered thresholds, external timestamp evidence, signatures, date/time, and actual decision. **Do not edit the repository's template to pretend that approval occurred.** Retain the signed record outside repositories accessible to developers.

---

## 8. Preflight checks and the GO / NO-GO decision

### 8.1. Verify the original manifest files

```bash
python -m lab.stage9_registered_manifest_custody \
  --registration research/stage9/registration.json \
  --index results/stage9/physical-manifest-index.json \
  --artifact-root results/stage9/raw-manifests \
  > results/stage9/receipts/manifest-custody.json
cat results/stage9/receipts/manifest-custody.json
```

**Expected:**

`"manifest_custody_status": "registered_manifest_bytes_match_requires_independent_review"`

Also expect `frozen_manifests_checked` = **4**, `calibration_worlds_checked` and `holdout_worlds_checked` matching the protocol, `registration_digest` matching preregistration, `scientific_verdict: null`, and `golden_stage9_frozen: false`.

**Meaning:** all declared files exist and their **original bytes** match the registered hashes. This is **not** a scientific attestation of independent worlds or their causal mechanisms.

### 8.2. Verify frozen code **in this checkout**

```bash
python -m lab.stage9_frozen_worktree \
  --repo . \
  --frozen-commit "$FREEZE_SHA" \
  > results/stage9/receipts/frozen-checkout.json
cat results/stage9/receipts/frozen-checkout.json
```

**Expected:**

`"worktree_status": "frozen_tracked_code_matches_local_checkout"`

Also expect `frozen_implementation_commit` to equal the approved SHA; `git_head` to equal the registration commit; Git object IDs `source_tree_sha`, `pyproject_blob_sha`, and `normative_specification_blob_sha`; and `scientific_verdict: null`.

**Meaning:** the **Git-tracked source files** on disk agree with the approved frozen version under the checker's assumptions. Installed dependencies, Python caches, hardware, actually executed processes, and independent custody require **additional evidence and witnesses**.

### 8.3. Final human decision

**NO-GO is mandatory** if any required element is missing: identified owner and evaluator; independent custody; credible positive and null worlds; prospective sampling; calibrated Equipment; approved parameters; written thresholds and exclusions; consistent Git history and file bytes; authentic signatures and timestamps; oracle/agent separation; or a physically valid mechanism for the negative control.

The GO must be **signed and dated before** any reserved execution. Passing the two preceding commands grants **no automatic GO**.

---

## 9. Running the campaign

### 9.1. Final checks

From the isolated Git checkout's root directory:

```bash
# Verify that this repository has no publication destination.
git remote -v

# The runner requires HEAD to be EXACTLY the preregistration commit.
test "$(git rev-parse HEAD)" = "$REGISTRATION_COMMIT"

# The raw output destination must not exist yet.
test ! -e results/stage9/raw
```

**Expected:** no error; no remotes; `HEAD` exactly at the registration commit. **Do not run** if `results/stage9/raw` already exists: it may contain a prior attempt or failure that must be preserved.

### 9.2. Run once, **only after human GO**

```bash
# IMPORTANT: exposing held-out data is scientifically irreversible.
python -m lab.stage9_heldout_runner run \
  --repo . \
  --registration research/stage9/registration.json \
  --registration-commit "$REGISTRATION_COMMIT" \
  --manifest-index results/stage9/physical-manifest-index.json \
  --manifest-root results/stage9/raw-manifests \
  --external-go-record results/stage9/private-release-record.json \
  --output-root results/stage9/raw \
  > results/stage9/receipts/operator-run-receipt.json

cat results/stage9/receipts/operator-run-receipt.json
```

**Expected when every cell executes and replays:** an output resembling this **illustrative excerpt** (not real results):

```json
{
  "status": "operator_execution_archived_requires_external_annotation",
  "run_count": 4,
  "registration_digest": "ACTUAL_64_HEX_REGISTRATION_DIGEST",
  "external_approval_authenticated": false,
  "independent_execution_attested": false,
  "scientific_verdict": null,
  "golden_stage9_frozen": false
}
```

`run_count=4` means **only** "four cells were processed" **if** the real registration had two worlds and two seeds. For the actual campaign, confirm `run_count = len(holdout_world_ids) × len(holdout_seeds)`.

**Meaning:** the simulation and its independently regenerated replay were archived. The software **did not authenticate human signatures, measure final causal truth, or issue PASS**.

If a cell cannot complete its registered number of **applied** steps (for example, `safety_block`), the runner raises an error. **Preserve** any partially created raw folder and error log, record the failed cell, and apply the preregistered `stop_rule` and `exclusion_rule`. Do not delete/retry only unfavorable cells or change parameters after outcomes are inspected.

### 9.3. Files created automatically

```text
results/stage9/raw/
├── operator-run-index.json
├── cell-000-000/
│   ├── journal.jsonl
│   ├── replay-journal.jsonl
│   ├── causal-state.json
│   ├── replay-causal-state.json
│   └── bench-only-world-truth.json
├── cell-000-001/
│   └── ...
└── ...
```

| File | Purpose | Expected content |
| --- | --- | --- |
| `operator-run-index.json` | Inventory of cells, original/replay paths, SHA-256 values, freeze SHA, protocol digest and preflight receipts. | `protocol_version = stage9-heldout-operator-run-index-v1`; exactly the preregistered number of `runs`; `scientific_verdict=null`. |
| `journal.jsonl` | Canonical-byte primary causal journal. | Events such as `command_experienced`, `world_transition_experienced`, and `auto_segment_commit` where applicable; no invented or dropped events. |
| `replay-journal.jsonl` | Journal **actually generated** during a second execution. | Bytes **exactly identical** to the primary journal. |
| `causal-state.json` | Complete final causal-owner state, including `memory` and `causal_model`. | Canonical causal JSON. |
| `replay-causal-state.json` | State **actually regenerated** during replay. | Bytes **exactly identical** to `causal-state.json`. |
| `bench-only-world-truth.json` | Initial/final world truth, realized generated layout, actual toxic berry, scenario and seed. | **Confidential**, never passed to the individual; not sufficient proof of every per-step causal relation. |

**Protect originals:** retain an independently controlled read-only copy or custody-managed storage with hashes, access permissions, operator ID and external timestamp evidence. Do not share bench-only output with developers before the disclosure point approved by the protocol.

---
## 10. Finding and annotating evidence

The operator passes the **original** journals and causal states to the independent bench. The bench determines which observations reflect actual causes, what attributions the individual produced, which controls showed no effect, and which **false** contingencies arose naturally in null worlds.

### 10.1. Locate events in the original records

**Only on the isolated computer, after execution and with proper access:**

```bash
python - <<'PY'
from pathlib import Path
import json
root = Path('results/stage9/raw')
index = json.loads((root / 'operator-run-index.json').read_text())
for run in index['runs']:
    print('CELL', run['world_id'], 'seed=', run['seed'])
    journal = root / run['journal_path']
    for line in journal.read_bytes().splitlines():
        item = json.loads(line)
        event = item['causal_event']
        if event.get('kind') in {
            'command_experienced', 'world_transition_experienced',
            'auto_segment_commit', 'agency_comparison',
            'causal_inference_status_published',
        }:
            print('  ', item['event_id'], event.get('kind'), event.get('t_monde'))
    state = json.loads((root / run['causal_state_path']).read_text())
    memory = state.get('memory', {})
    print('  Closed Memory episodes:', len(memory.get('episodes', [])))
PY
```

**Expected:** technical `event_id` references associated with actual world steps and a count of closed Memory episodes. The operator **must not publish this output**. The evaluator must then inspect each actual record, its provenance links, observed effects and episode `event_refs`. Merely displaying an ID **is not proof of causality**.

### 10.2. Create `results/stage9/private-annotations.json`

Use this exact schema:

```json
{
  "protocol_version": "stage9-heldout-independent-annotations-v1",
  "registration_digest": "ACTUAL_CANONICAL_64_HEX_DIGEST",
  "runs": [
    {
      "world_id": "ACTUAL_POSITIVE_WORLD_ID",
      "seed": 0,
      "known_cause_cases": [
        {
          "id": "UNIQUE_CASE_ID",
          "episode_ref": "ACTUAL_CLOSED_MEMORY_EPISODE_ID",
          "observation_ref": "ACTUAL_PHYSICAL_TRANSITION_EVENT_ID",
          "ground_truth": "self",
          "attribution": "self_compatible"
        }
      ],
      "naturally_acquired_false_candidates": []
    },
    {
      "world_id": "ACTUAL_NULL_WORLD_ID",
      "seed": 0,
      "known_cause_cases": [],
      "naturally_acquired_false_candidates": [
        {
          "id": "UNIQUE_CANDIDATE_ID",
          "contingency_ref": "ACTUALLY_ACQUIRED_CAUSAL_RULE_ID",
          "episode_ref": "ACTUAL_CLOSED_MEMORY_EPISODE_ID",
          "observation_ref": "ACTUAL_DISTINCT_PHYSICAL_TRANSITION_ID",
          "causal_status": "hypothese_causale"
        }
      ]
    }
  ]
}
```

**SCHEMA EXAMPLE ONLY:** these references and seed are not actual observations and **must never be copied as evidence**. Supply **one row per registered cell**, even when both evidence arrays are empty because no admissible observation occurred. Keep the strict root and per-cell keys: arbitrary extra metadata is not accepted.

**Field meanings and sources:**

| Field | Actual source and interpretation |
| --- | --- |
| `world_id`, `seed` | Exact registered values; **each pair exactly once**. Never manufacture additional cells. |
| `known_cause_cases[*].id` | Unique case identifier within its cell. |
| `episode_ref` | ID of a **closed** episode in `causal-state.json` under `memory.episodes`. |
| `observation_ref` | `event_id` of an actual `world_transition_experienced` in `journal.jsonl`, with a matching command, applied world step and coherent autobiographical commit. |
| `ground_truth` | `self`: consequence genuinely attributable to the agent's action; `world`: external cause; `none`: **no relevant physical effect**. Independent justification required. |
| `attribution` | Actual reported classification: `self_compatible`, `world_justified`, or `uncertain`. An abstention **does not count as correct attribution**. |
| `naturally_acquired_false_candidates[*].contingency_ref` | Canonical ID of a rule **actually acquired by the individual and independently known to be false**; count the same rule **at most once per cell**. |
| `causal_status` | Actual causal-model status: `correlation_observee`, `hypothese_causale`, `testee_par_intervention`, or `etablie`. Never invent `etablie`. |

The bench must document separately: the physical justification for positive and null controls, comparable interventions, controlled covariates, independent episodes, any exclusions and negative witnesses. `INV-25` review is **additional**; it cannot be inferred from these annotation rows alone.

**Critical rules:**

- `ground_truth="none"` does **not** enter the denominator for correctly linked positive-cause cases. Crediting causal attribution despite no effect can invalidate metric eligibility.
- One physical observation cannot be counted twice within a cell, even under distinct IDs. Several distinct transitions may fall in one closed Memory episode, but this does not imply statistical independence.
- False hypotheses are counted **only if the individual truly acquired them naturally**. Never inject fake candidates to force a nonzero denominator.
- If no false hypothesis was naturally acquired, write `[]` and accept `not_evaluable` if the aggregate denominator is zero. Do **not** claim "0% superstition".

---

## 11. Packaging and sealing the report

### 11.1. Convert independent annotations into auditable evidence

With output paths `results/stage9/heldout.json` and `results/stage9/raw-artifact-index.json` **not yet present**, run:

```bash
python -m lab.stage9_heldout_runner package \
  --registration research/stage9/registration.json \
  --runs-root results/stage9/raw \
  --annotations results/stage9/private-annotations.json \
  --evidence results/stage9/heldout.json \
  --raw-index results/stage9/raw-artifact-index.json \
  > results/stage9/receipts/package-receipt.json

cat results/stage9/receipts/package-receipt.json
```

**Expected, provided structural checks pass:**

`"status": "provisional_evidence_packaged_requires_independent_review"`

The response also contains `assessment`, `registration_digest`, `evidence_sha256`, `scientific_verdict: null`, and `golden_stage9_frozen: false`.

**Meaning:** claimed case references are consistent with the files, their SHA-256 digests and the checked Memory/journal provenance. **Independent human scientific review is still required.** `assessment` may be `not_evaluable`, `below_preregistered_confidence_threshold`, or another unfavorable status **without the command failing**. **Preserve valid unfavorable reports.**

The runner creates:

- `heldout.json` in `stage9-heldout-evidence-v2` format, containing source measurements and case references by world/seed.
- `raw-artifact-index.json` in `stage9-heldout-raw-artifact-index-v4` format, recording relative paths to the four original/replay files of every cell.

If `package` fails due to a missing or unjustified reference, **do not invent evidence**. Preserve the failure and audit the originals. A purely clerical transcription correction must be dated, explained and traceable. Changing inclusion or metric rules after observing outcomes is not permitted.

### 11.2. Archive the report in the **same isolated Git repository**

```bash
# Do NOT use 'git add -A': the folder holds secrets and raw archives.
git add results/stage9/heldout.json
git commit -m "Archive Stage 9 heldout evidence"
export EVIDENCE_COMMIT="$(git rev-parse HEAD)"

git merge-base --is-ancestor "$FREEZE_SHA" "$REGISTRATION_COMMIT"
git merge-base --is-ancestor "$REGISTRATION_COMMIT" "$EVIDENCE_COMMIT"

git log --oneline --max-count=3
```

**Expected:** three chronologically intended points connected by Git ancestry: **frozen code → sealed protocol → evidence**. `src/`, `pyproject.toml`, the English specification, and `registration.json` must remain unchanged throughout the lineage.

> **Do not push** the isolated repository to a shared remote. The preregistration commit contains secret numeric seeds in plaintext, which remain visible in its Git history even if other files are removed.

---

## 12. Performing the final independent audit

The following tools do not modify journals or evidence. Run them **after committing the evidence**, inside the same isolated Git repository, with all **original bytes** still available.

### 12.1. Verify Git ancestry and immutability

```bash
python -m lab.stage9_registration_chronology \
  --repo . \
  --registration research/stage9/registration.json \
  --registration-commit "$REGISTRATION_COMMIT" \
  --evidence results/stage9/heldout.json \
  --evidence-commit "$EVIDENCE_COMMIT" \
  > results/stage9/receipts/git-chronology.json
```

**Expected:** JSON without exceptions, containing frozen source and specification identities, examined chronology, provisional metrics, and `scientific_verdict: null`. **Meaning:** Git lineage is internally coherent, **not** an independent proof of actual wall-clock time or human access conditions.

### 12.2. Independently recalculate the provisional score

```bash
python -m lab.stage9_scientific_assessment \
  --registration research/stage9/registration.json \
  --evidence results/stage9/heldout.json \
  > results/stage9/receipts/metric-assessment.json
```

**Expected:** measured indicators and an `assessment` status, without a scientific verdict. Interpret using the [status table](#132-how-to-interpret-assessment).

### 12.3. Verify raw journal bytes and closed Memory evidence

```bash
python -m lab.stage9_heldout_artifact_custody \
  --registration research/stage9/registration.json \
  --evidence results/stage9/heldout.json \
  --index results/stage9/raw-artifact-index.json \
  --artifact-root results/stage9/raw \
  > results/stage9/receipts/raw-custody.json
```

**Expected:** `"artifact_custody_status": "raw_bytes_match_report_requires_independent_provenance_review"` if all structures, hashes and admissible sources check out. **Meaning:** **software consistency** between archived originals and the evidence claimed; not independent physical proof that the experiment was genuinely held out.

### 12.4. Produce a consolidated machine receipt

```bash
python -m lab.stage9_independent_handoff \
  --repo . \
  --registration research/stage9/registration.json \
  --registration-commit "$REGISTRATION_COMMIT" \
  --evidence results/stage9/heldout.json \
  --evidence-commit "$EVIDENCE_COMMIT" \
  --manifest-index results/stage9/physical-manifest-index.json \
  --manifest-root results/stage9/raw-manifests \
  --raw-index results/stage9/raw-artifact-index.json \
  --raw-artifact-root results/stage9/raw \
  > results/stage9/receipts/independent-handoff.json
```

**Expected:** an object with:

- `handoff_status = machine_checks_consistent_requires_independent_scientific_review`, **or** `machine_checks_complete_with_explicit_review_blockers` if alerts require review.
- `review_blockers`: read the **entire list**; do not suppress warnings.
- `machine_handoff_sha256`: identity of the machine-generated receipt.
- Subreports `git_chronology`, `current_checkout_preflight`, `physical_manifest_custody`, `raw_artifact_custody`, and `provisional_metrics`.
- `independent_world_custody_attested = false`, `independent_seed_selection_attested = false`, `prospective_approval_attested = false`, `oracle_isolation_attested = false`, `scientific_verdict = null`, and `golden_stage9_frozen = false`.

**Meaning:** the software deliberately **refuses to certify** facts that require independent human judgment. The `machine_handoff_sha256` is **not** an evaluator's signature.

---

## 13. Interpreting results and issuing a verdict

### 13.1. Mandatory metrics and what they mean

| Report field | Precise meaning |
| --- | --- |
| `known_cause_cases` | Number of admissible physically causal cases (`self` or `world`); `none` does not count. |
| `correct_links` | Number of those cases with an attribution matching the actual cause. |
| `uncertain_links` | Cases where the individual abstained; **not counted as correct**. |
| `false_self_links` | Incorrect self-attributions, including those on no-effect controls. |
| `known_cause_accuracy` | `correct_links / known_cause_cases`, when denominator > 0. |
| `known_cause_wilson_95` | Two-sided 95% Wilson confidence interval for accuracy. The scorer compares the **lower bound** with the preregistered minimum. |
| `no_effect_control_cases` | Cases with no physically relevant causal consequence. |
| `no_effect_control_abstentions` | No-effect controls correctly left `uncertain`, reported separately. |
| `no_effect_control_false_attributions` | **Unjustified causal attributions** despite no effect; these block metric eligibility. |
| `natural_false_candidate_count` | Number of actually acquired rules that an independent observer identified as false in null worlds. |
| `false_established_count` | Subset of those false rules incorrectly promoted to `etablie`. |
| `superstitious_rule_rate` | `false_established_count / natural_false_candidate_count`, when denominator > 0. |
| `superstition_wilson_95` | Two-sided 95% Wilson interval for that rate; the scorer compares its **upper bound** with the registered maximum. |
| `positive_known_cause_runs`, `registered_positive_runs` | Coverage of positive worlds/seeds: every registered positive cell needs at least one physically observed positive-cause case. |
| `negative_runs_without_natural_candidates` | Null cells with no naturally observed false candidates; reviewer must assess sampling and concentration. |
| `reused_closed_memory_*` | Multiple candidate observations/cases in one closed episode: **dependence warnings**, not necessarily duplicate physical events. |
| `cross_run_identical_archives` | Journals or causal states identical across different cells; require independent explanation. |

Wilson intervals do not, by themselves, prove statistical independence of observations. The evaluator must assess the actual structure of worlds, seeds, contexts and episodes together with the preregistered analytical assumptions.

### 13.2. How to interpret `assessment`

| Value returned by code | Meaning | Required response |
| --- | --- | --- |
| `unregistered` | No research protocol supplied. | **NO-GO**; do not execute. |
| `awaiting_holdout_campaign` | Preregistration exists, but evidence does not. | No scientific conclusion. |
| `invalid_no_effect_attribution` | At least one causal attribution was credited despite no physical effect. | Not eligible; investigate and report the failure. |
| `not_evaluable` | Denominator for known-cause cases **or** naturally acquired false candidates is **zero**. | Do not call this 0% or PASS; report non-evaluable. |
| `incomplete_known_cause_world_coverage` | At least one positive cell contains no actual observed positive-cause case. | Incomplete coverage; metrics ineligible. |
| `insufficient_natural_candidates` | Fewer spontaneous candidates than the preregistered minimum. | Insufficient under protocol; never fabricate extra candidates. |
| `below_preregistered_confidence_threshold` | Lower accuracy bound is too low **or** upper superstition bound is too high. | Metric thresholds missed; report `FAIL` if observations are valid. |
| `metrics_eligible_for_independent_review` | Automated **metric** checks satisfy the prospective limits. | **Not a scientific PASS**: physical truth, independence, chronology and `INV-25` must still be reviewed. |

A Python exception or nonzero process exit indicates a **technical validation failure**, not an unfavorable score to ignore. Archive the case as it occurred.

### 13.3. Independent validation of `INV-25` and causality

Beyond the numeric scorer, the evaluator must inspect and sign off on:

1. **Actual causality:** authentic positive/null conditions; inaccessible oracle truth; controlled interventions and truly experienced, nonfabricated events.
2. **Agency attribution:** compare measured consequences, frozen predictions, and the actual attribution produced; examine **every** error and abstention.
3. **`etablie` status:** verify that simulator predictions are altered only by contingencies genuinely in `etablie` status, according to the normative mechanism.
4. **`etabli_pour_securite` status:** demonstrate using matched comparisons that a safety fact makes an action inadmissible **without changing** its `R_a` evaluation or simulator predictions, all else being equal.
5. **Provenance:** independently justify prior registration, decision chronology, closed Memory state, canonical journal events, and exact replays.
6. **Limitations:** document constraints of the exact-table Equipment, absent observations/candidates, nonindependent contexts, and Stage-11 capabilities not yet available in Stage 9.

The `run` command **does not automatically sign an `INV-25` review**. Comparisons must follow a **prospectively defined** plan and be reviewed independently. If they cannot be performed without changing the code or plan after exposure to held-out data, **scientific closure remains blocked**.

### 13.4. Signed decision form

Complete this using **original evidence**, not a machine-authored verdict:

```text
Campaign ID: __________________________________
Frozen code (40 hex): __________________________
Preregistration commit (40 hex): ________________
Evidence commit (40 hex): ______________________
Canonical registration digest (64 hex): ________
Evidence digest (64 hex): ______________________
Independent custodian: _________________________
Operator: _____________________________________
Independent evaluator: _________________________
Signed approval/timestamp evidence: ____________
Registered / executed worlds × seeds: __________
Known causal observations / accuracy: __________
Natural false candidates / falsely established: _
Confidence intervals and thresholds: ___________
INV-25: [ ] satisfied [ ] failed [ ] not verified
Oracle isolation and provenance: _______________
Incidents, exclusions, and counterexamples: ____

VERDICT: [ ] PASS [ ] FAIL [ ] INCONCLUSIVE
Rationale and original supporting evidence: ____
Independent date, name and signature: __________
Countersignature, if required: _________________
```

**`PASS`:** only when **all** normative and preregistered criteria are independently verified, with sufficient evidence.  
**`FAIL`:** valid conditions and evidence, but at least one criterion is not met.  
**`INCONCLUSIVE`:** insufficient evidence, sample size, temporal priority, provenance, null controls, equipment or independence; explain precisely what is missing.

Even a documented human PASS triggers **neither an automatic PR merge nor automatic Golden creation**. The governance process separately decides any scientific reference freeze.

---
## 14. Handling anomalies without losing scientific value

| Situation | Mandatory response |
| --- | --- |
| `ModuleNotFoundError`, wrong Python version, installation failure | Stop before GO; fix the environment and rerun **development software tests only**. |
| `registration requires exact mandatory fields` or `...schema mismatch` | Verify all 30 required fields, types, and versions; never bypass the validator. |
| `normative specification digest mismatch` | Check the **original English** normative document, source identity, and original bytes; never change the normative specification to make a test pass. |
| `physical manifest digest mismatch` | Inspect originals, paths and permissions. If already approved, any change needs documented prospective review **before** outcome exposure; otherwise mark the study inconclusive as applicable. |
| `operator seal requires complete unshallowed Git history` | Obtain the **full** Git history before execution; never manufacture Git ancestry. |
| `execution checkout must be at preregistration commit` | Check `git rev-parse HEAD` and `REGISTRATION_COMMIT`; never alter the code to bypass the check. |
| `absent, incomplete or conflicting human GO record` | **NO-GO**: locate the real signed approval; never forge an identity or GO record. |
| The `raw` output directory already exists | Do not delete it: it may contain a prior attempt or failure. Inspect it and the stopping rule; request fresh authorization if necessary. |
| Byte-exact replay fails | Report `FAIL` or `INCONCLUSIVE` under the protocol. Preserve **both** originals; never silently repair them. |
| `safety_block`, incomplete episode, interrupted run | Preserve traces, report the cell, and apply exclusion and stopping rules **fixed before** the experiment. |
| No naturally acquired false hypothesis | Zero or insufficient denominator; **never inject hypotheses to increase the sample**. |
| Missing `observation_ref` or unclosed Memory | Do not credit the case; preserve the failure and inspect the original files and protocol. |
| Nonempty `review_blockers` | Review **each** item and retain an evidence-backed explanation; never delete rows just to obtain a clean machine receipt. |
| Premature access to seeds/labels or prior examination of outcomes | Document the leak. The exposed actors no longer have a truly held-out evaluation; a **new independent plan** is necessary for a fresh scientific claim. |
| A valid negative control cannot be expressed by the current runner | **NO-GO** before exposure: report the required development change, then select **new frozen code and a new preregistration**. |

**Guiding principle:** a well-recorded unsuccessful experiment is scientific information. An experiment rewritten after its outcome is no longer prospective evidence.

---

## 15. Delivering the evidence package and closing the assignment

Separate **information eligible for disclosure** from **restricted original archives**:

**A. Report that may be shared after the protocol permits disclosure**

- Exact source code and versions, design description, sample counts, metrics and intervals, signed verdict, and limitations.
- Date/time and reference for independent preregistration witnessing; summary of checks and anomalies.
- Favorable **and unfavorable** conclusions, including `FAIL` / `INCONCLUSIVE` and any `review_blockers`.

**B. Confidential archive for the evaluator/custodian only**

- **Complete, access-controlled** isolated Git history, including all ancestors, plaintext-seed registration and evidence commit; original signatures, access records and timestamp proofs.
- All original frozen JSON assets, world/scenario manifests, withheld seeds, and documented calibration/held-out separation.
- `operator-run-index.json`, **every** original cell and its replay, `bench-only-world-truth.json`, and signed bench annotations.
- `heldout.json`, `raw-artifact-index.json`, and all receipts from section 12.
- Documentation of calibration parameters, trained Equipment, Python environment, incidents, uncredited observations, `INV-25` controls and counterexamples.

**Never transfer the isolated Git repository to the shared development GitHub repository**, because its history reveals reserved data. The custodian and owner decide any future disclosure under the protocol, after reviewing confidentiality and publication timing.

---

## 16. Appendices: templates and quick reference

### Appendix A. Strict sequence of milestones

| # | Required step | Acceptable evidence before proceeding |
| --- | --- | --- |
| 1 | Verify source and environment without held-out data | Green software tests; selected code SHA; software integration kept separate from scientific evaluation. |
| 2 | Receive parameters, Equipment, ontology, generator | Valid JSON with real values and calibration provenance. |
| 3 | Select worlds and seeds under independent custody | Calibration/held-out separation and credible positive/null controls; secrets preserved. |
| 4 | Complete preregistration | `draft_requires_independent_git_seal`, actual values, no missing fields. |
| 5 | Sign protocol, then make isolated registration Git commit | `REGISTRATION_COMMIT` descends from frozen code; separate independently witnessed timestamp. |
| 6 | Create indexes and pass preflight | Original manifest bytes match registration; frozen code unchanged. |
| 7 | Obtain real signed human GO | Identities, conflicts, custody and approval verified **before results**. |
| 8 | Execute `run` | `operator_execution_archived_requires_external_annotation`; all cells archived. |
| 9 | Produce independent annotations | Every credited reference exists in a journal and closed Memory; bench truth independently justified. |
| 10 | Execute `package` | `provisional_evidence_packaged_requires_independent_review`, including when metrics are unfavorable. |
| 11 | Commit evidence and run the four independent audits | Git chronology, provisional metrics, raw-file custody and consolidated machine receipt archived. |
| 12 | Examine `INV-25` and sign a verdict | Independent PASS / FAIL / INCONCLUSIVE report, with limitations and counterexamples. |

### Appendix B. Essential command cheat sheet

```bash
# 1. Well-formed registration, NOT independent approval yet
python -m lab.stage9_scientific_preregistration \
  --manifest research/stage9/registration.json

# 2. Original registered physical manifest identity
python -m lab.stage9_registered_manifest_custody \
  --registration research/stage9/registration.json \
  --index results/stage9/physical-manifest-index.json \
  --artifact-root results/stage9/raw-manifests

# 3. Source bytes in checkout match the approved freeze
python -m lab.stage9_frozen_worktree --repo . --frozen-commit "$FREEZE_SHA"

# 4. After a REAL GO only: execute ALL cells; never use as a diagnostic
python -m lab.stage9_heldout_runner run --repo . \
  --registration research/stage9/registration.json \
  --registration-commit "$REGISTRATION_COMMIT" \
  --manifest-index results/stage9/physical-manifest-index.json \
  --manifest-root results/stage9/raw-manifests \
  --external-go-record results/stage9/private-release-record.json \
  --output-root results/stage9/raw

# 5. After independent annotation of REAL events
python -m lab.stage9_heldout_runner package \
  --registration research/stage9/registration.json \
  --runs-root results/stage9/raw \
  --annotations results/stage9/private-annotations.json \
  --evidence results/stage9/heldout.json \
  --raw-index results/stage9/raw-artifact-index.json

# 6. After evidence is committed: consolidated machine handoff
python -m lab.stage9_independent_handoff --repo . \
  --registration research/stage9/registration.json \
  --registration-commit "$REGISTRATION_COMMIT" \
  --evidence results/stage9/heldout.json \
  --evidence-commit "$EVIDENCE_COMMIT" \
  --manifest-index results/stage9/physical-manifest-index.json \
  --manifest-root results/stage9/raw-manifests \
  --raw-index results/stage9/raw-artifact-index.json \
  --raw-artifact-root results/stage9/raw
```

### Appendix C. Three important status flags

| Flag | Operational meaning |
| --- | --- |
| `scientific_verdict: null` | **Normal**, even after every tool completes. The machine has not replaced the human scientific evaluator. |
| `golden_stage9_frozen: false` | **Normal**, even if metrics look favorable. No scientific Golden is created automatically. |
| `...requires_independent_review` | A machine consistency check completed, but independent people must still verify facts that cannot be proven from stored files alone. |

### Appendix D. Custodian's intake form

```text
Approved frozen code SHA: ______________________
Research owner and signature: _________________
Custodian and reviewed conflicts: _____________
Operator and approved scope: __________________
Independent evaluator: ________________________
Location of complete private Git: _____________
Location of encrypted originals: ______________
Independent timestamp evidence location: ______
Number of positive worlds: ____________________
Number of negative worlds: ____________________
Number of calibration worlds: _________________
Number of held-out seeds: _____________________
Run duration and stopping rule: ________________
Signed metric thresholds (reference): _________
Signed causality/INV-25 criteria: ______________
Manifest validation evidence: _________________
Decision BEFORE experiment: [ ] NO-GO [ ] GO
Signatures and date: __________________________
```

---

### Final note to the new evaluator

**Your job is to verify a claim, not to obtain a favorable outcome.** The most valuable contribution is an evidence package that allows another person to reconstruct what was decided, executed, observed and judged, including when the findings do not support acceptance.

*This guide describes the interfaces of the integrated `main` software inspected on 10 October 2026, using `b304ebda7facf8ba285408e87090727dafc43bcb` as a possible, **not scientifically approved**, starting point. The final commit must be selected and frozen prospectively by authorized independent personnel. If experimental code changes, recheck all commands and revalidate this guide before choosing a new scientific freeze.*
