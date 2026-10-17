# Observability for I1: observer versus subject

The Lab's external evidence includes world layout, physics, a full technical journal, storage receipts and sometimes operator-only world truth. The individual does **not** get these capabilities. Its admissible inputs are restricted first-person perceptions, bodily telemetry and its lived autobiographical projection.

## Existing observation surfaces

- `tools/run_i1_world_preset.py` can create unforced mortal lives with WAL or M11, with externally recorded world-step receipts and outcome summaries; see [WORLD_PRESETS.md](WORLD_PRESETS.md).
- `tools/campaign_report.py` reports known CI evidence, gaps and unverified scientific claims. It cannot assert a completed GitHub workflow on local metadata alone.
- `runtime/journal_views.py` projects allowed autobiographical events; the complete `runtime/journal.py` remains Lab-owned.
- `runtime/i1_cognitive_publication.py` validates owner evidence, but published nonempty useful forms must be established from actual lived records before claiming success.

## Read-only cognitive diagnostics

Use `tools/inspect_i1_world_report.py` on a JSON report from a world preset. It **does not import a runtime, execute a step, open a writable SQLite ledger, recover a dead individual or return any data to the individual's cognitive processes**. It reports only observable physical changes and explicitly marks goal selection, competition, UC, autobiographical attribution and owner publications **NOT_OBSERVED** where the source report does not contain that evidence.

The same report may contain operator-only world layout and danger coordinates. The inspector must not reproduce those fields in its limited public summary. In the technical artifact they remain for an authorized external audit, never as individual memory.

## Next observability increment

A genuine cognitive trace requires a **separately reviewed, read-only observer at already existing causal boundaries**. That design must establish that observations do not charge or alter cognition, inject privileged data, or bypass atomic M11 ownership. Until that interface is validated, do not claim the external report proves why a choice was made.

## Interpretation rules

- Inventory quantity is not physical satiety.
- Plan proposal is not Action Control admission; command admission is not success.
- Visible outcome compatibility is not proof of causal authorship.
- A journal record is not necessarily an autobiographical fact.
- An online update is not a Stage10 consolidated publication.
- Mortality is terminal. Read-only audits may describe an ended life, never resurrect it.

## Observation capability matrix and passive evidence design

| Surface | Physiology / life | Cognitive proposals / UC | Publications / permanence | Boundary |
| --- | --- | --- | --- | --- |
| `tools/run_i1_world_preset.py` WAL report | Per-step physical body, position, inventory, execution and terminal status | **NOT_OBSERVED**: no option competition or UC series | Durable technical WAL head and audit count, **not** owner deltas | Operator-only report, never supplied to I1 |
| Same runner with M11 | Committed world-step/generation receipt and terminal lifecycle | **NOT_OBSERVED** | SQLite audit, pending intent and `may_recover`; no full owner diff in report | No arbitrary cold replay to inspect a dead life |
| `tools/inspect_i1_world_report.py::inspect` | WAL last state and delta (from first captured step), M11 physical values **NOT_OBSERVED** | Explicit `NOT_OBSERVED` fields | Stage10 nonempty publication **NOT_OBSERVED** | Redacts world layout/canaries from result; never mutates individual |
| Authorized technical journal | Append-only causal `JournalEntry` and physical occurrence refs | `compute_charge`, `s_t_published`, `competition_cycle` *if actually emitted* | Stage10 batch, pass, deferred and committed events *if emitted* | Journal access is external, not a permission to teach hidden data |
| Authenticated M11 current image | One authoritative committed world and owner roster | Persisted causal owners, versioned contracts | Active advisory owner rows and `SlowHistory` committed state | Read-only audit / authenticated current generation only |

**Three distinct questions:** (1) Did a source event exist? (2) Could the individual perceive/experience it? (3) Was a corresponding owned cognitive state actually modified and durably retained? None implies the next. An event labelled `stage10_consolidation_committed` cannot answer question 3 without owner-state evidence.

A future externally controlled cognitive observer should consume **only already committed, immutable artifacts**, should include source SHA and genesis identity, and should redact `environment.layout`, hidden canaries, unavailable safety facts and operator-only predictions from anything shared with cognition. It must not import an active runtime, open a second mutable M11 writer, invoke `run_step`, or recompute missing subjective beliefs. For each phase claim it should report `OBSERVED` with cited immutable event refs, `NOT_OBSERVED` for an absent measurement, and `UNVERIFIED` for an unvalidated evidence claim. No automatic scientific GO.

For causal measurement consult [LIVED_EVIDENCE_WALKTHROUGH.md](LIVED_EVIDENCE_WALKTHROUGH.md); for missing UC and Stage10 evidence consult [UC_AND_SCHEDULING.md](UC_AND_SCHEDULING.md) and [CONSOLIDATION_AND_PUBLICATION.md](CONSOLIDATION_AND_PUBLICATION.md). The standard preset JSON alone cannot certify cognitive arbitration.
