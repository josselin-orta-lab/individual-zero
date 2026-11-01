# Curated research dossiers: from candidate links to auditable questions

The [incremental corpus index](RESEARCH_CORPUS.md) finds possible document relationships. This dossier layer adds **carefully selected source roles and precise boundaries** to help research agents inspect the evidence and propose meaningful next work. It is neither an automatic scientific classifier nor a formal approval.

The machine-readable seed is [`config/research-dossiers.json`](../../config/research-dossiers.json); the read-only examiner is `tools/research_dossiers.py`.

## Research questions with named records

The initial seed covers four distinct cases:

| Dossier | Reported assessment | What is actually linked | Key gap to verify |
| --- | --- | --- | --- |
| `I1-A1C-TARGETED` | `NO_GO` | Original A1-C preregistration, a later post-hoc diagnostic, a dated I1 status summary | Original primary outcome record, independent M11 archive custody and replication |
| `I1-A2R-REWARD` | `NOT_EXECUTED` | Frozen prospective protocol and I1 status summary | No 96-life cohort exists; **do not invent a result or run it to fill the dossier** |
| `I1-A235B-COMPETITION` | `INCONCLUSIVE` | Original prospective preregistration and reported results | The intended natural contested-opportunity condition was not met; **software CI PASS is not scientific confirmation** |
| `I2-G1-INDEPENDENT-REVIEW` | `REVIEW_REQUIRED` | Proposal contracts and G1 review requests, plus dated I2 status | Independent architectural/scientific decision, living M11 safeguards, birth and motor authority are not established |

These are **dated, source-reported assessments**, not new independent verdicts made by this tool. I1 remains the active generation. I2 remains an unregistered, non-living proposal. The seed is deliberately small; many historic research records have not yet been curated.

## How agents inspect dossiers

From a complete local repository checkout:

```bash
python tools/research_dossiers.py audit
python tools/research_dossiers.py list
python tools/research_dossiers.py show --id I1-A1C-TARGETED
python tools/research_dossiers.py gaps
python tools/research_dossiers.py compare --left I1-A1C-TARGETED --right I1-A2R-REWARD
```

All commands are read-only. The audit checks structure and source byte identity using the exact **Git blob SHA** and an in-file quotation marker. Any modification to a pinned source, even when the quoted words survive, requires source reconciliation. The source-level result `PIN_MATCH` proves only document identity, **not correct scientific interpretation**.

Each dossier has an explicit protocol/cohort/endpoint/contrast identity to prevent comparisons of superficially related studies. A1-C and A2-R cannot contradict each other merely because both concern I1 and L3: they have different protocols and populations, and A2-R has not been executed. Even identical identities and differing reported assessments yield only a **potential disagreement to review**, not a proven contradiction.

### Distinguish structural checks from source freshness

`python tools/research_dossiers.py audit` is strict: a moved Git source blob, even with the same quoted marker, is reported as a failure. `python tools/research_dossiers.py audit --structure-only` validates schema, roles, reference scopes and generation safeguards while exposing source drift in `source_status` and `source_review_required`.

The single lightweight navigation CI permits **only** an unchanged-marker blob drift in documents explicitly classified `current_status_snapshot`; no historical protocol, result, review proposal, or other pinned source may silently drift. A dossier depending on a changed status remains `REVIEW_SOURCE_CHANGES_FIRST` until reconciled; no independent approval is inferred.

## The agent's research decision sequence

1. Begin with [global scientific status](RESEARCH_COORDINATOR.md), its question/gate graph and negative findings.
2. Explore candidate relationships with `python tools/research_corpus.py review --topic study:A1-C`. Do not promote lexical matches into evidence.
3. Open the [curated dossier](../../config/research-dossiers.json), inspect each linked source at its exact Git SHA, and check original preregistration, analysis, traces, controls, independent units, date, source code SHA, M11 custody and downstream counterexamples.
4. Leave any missing artifact explicitly in `review_gaps`. The queue shown by `gaps` is a **review queue**, not a list of authorized experiments.
5. Choose the smallest falsifiable next intervention, identify its scientific dependencies and use [task routing](AGENT_CONTEXT.md) only after selecting the research question.
6. Record the source pins, actual evidence limitations, a potential falsifying result and explicit review status in the [handoff](AGENT_HANDOFF.md).

The dossier manifest may be edited only to **document** newly inspected sources or corrected scopes. New findings and independent decisions must first exist in their owning scientific source; adding an `APPROVED` label to the manifest does not approve a gate.

## Maintenance and permissions

When a source changes: inspect the exact diff against the pinned blob, reconcile the claim and update the dossier pin in a reviewable PR. Keep the old research record intact and make supersession explicit.

```bash
python tools/research_dossiers.py audit
python -m unittest discover -s tests -p test_research_dossiers.py -v
python tools/research_coordinator.py audit
```

Never use dossier completion to launch a mortal cohort, alter `config/engine-registry.json`, register I2, grant motor/recovery authority or infer generalized learning. A closed GitHub issue is not equivalent to independent review. Historical I0 and earlier I1 reports retain their original provenance.
