# Agent handoff: minimal operating context

This is a **navigation and handoff contract**, not a replacement for original scientific evidence, generation contracts or ADRs.

## Five-minute restart

1. Read `config/engine-registry.json` for active runtime versus development reference.
2. Read `AGENTS.md`, `src/i3/AGENTS.md` (if present), and the first **current live handoff** section of `src/i3/docs/STATUS.md`. Treat later dated status entries as historical unless explicitly superseding.
3. For Stage7 persistence, read `src/i3/docs/studies/stage7-persistence/STAGE7_EXECUTION_LIVE_HANDOFF_2026-11-16.md` and the frozen protocol. Recheck live Actions and artifact receipts on exact SHAs; never infer completion from an older status paragraph.
4. For an open-ended next task, run `python tools/research_coordinator.py recommend`, then inspect the curated dossier and live issues/PRs.
5. Identify the smallest relevant test suite using `tests/TEST_LAYOUT.md` and `python tools/repository_layout.py inventory --kind tests --match <topic>`.

## What each source can establish

| Claim | Authority |
| --- | --- |
| Active engine and development reference | `config/engine-registry.json` |
| Executable behavior | source, generation `engine.json`, exact commit |
| Architectural permission | accepted ADR and generation contracts |
| Engineering verification | test result + CI run + exact SHA |
| Scientific result | frozen protocol, original receipts, contrasts and issued verdict |
| What to do next | coordinator suggestion **plus** human/agent review of current evidence |

Never promote a green engineering test into a scientific positive. A running job is not a completed receipt. Negative, null, and unissued outcomes must remain visible.

## Test tiers

- **T0, navigation and structure:** repository layout, imports, metadata, document links. Run on small doc/structure changes.
- **T1, focused generation unit/contract:** the changed mechanism and its negative/boundary tests.
- **T2, generation integration:** causal path, paid costs, irreversible state, replay and persistence as relevant.
- **T3, expensive engineering rehearsal:** full-scale source-exact preflight and two sealed repetitions where the frozen protocol requires them.
- **T4, scientific cohort:** prospective, separately preregistered, only after the exact T3 gate and release conditions pass.

T0-T2 never authorize T3-T4. Keep T3/T4 receipts and frozen protocols out of routine fast CI. Do not delete or rewrite historical witnesses to speed up the test suite.

## Handoff record for each agent intervention

Record in the PR body or task issue, **not another long status essay**:

```text
BASE_SHA:
SCOPE / GENERATION:
QUESTION AND FALSIFIER:
FROZEN PROTOCOL OR ADR:
FILES CHANGED:
TESTS RUN (command, SHA, result):
EVIDENCE / RECEIPTS (links and hashes):
SCIENTIFIC VERDICT (POSITIVE / NEGATIVE / INCONCLUSIVE / NOT_ISSUED):
OPEN BLOCKERS:
NEXT SAFE ACTION:
```

If evidence is missing, write `NOT_VERIFIED`; never invent a receipt. Preserve the distinction between owner authorization for internal prospective research (ADR-0022) and external attestation or runtime promotion, neither of which follows automatically.

## Documentation lifecycle

- **Normative:** registry, generation contracts, accepted ADRs, frozen protocols. Immutable where source-pinned.
- **Live:** a concise current status and one handoff pointer per active campaign.
- **Evidence:** original run artifacts, signed/sealed receipts and source-locked reports; append-only.
- **Historical:** dated reports and superseded interpretations, preserved with explicit supersession links.

Before creating a new document, check whether it belongs in an existing authoritative index. Prefer links and concise deltas over copied status paragraphs. Never mass-delete scientific archives or change preregistered thresholds as part of documentation cleanup.
