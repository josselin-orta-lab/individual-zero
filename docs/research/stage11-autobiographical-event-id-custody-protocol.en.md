# Stage 11: autobiographical projections must preserve technical event identity

**Software regression contract registered 2026-10-11 before the remote code change.** Normative authority: `docs/architecture/reference/en/mvp-specification-v1.2.1.md`, sections 17.4–17.5, DC-09, INV-27, INV-44 and INV-49. Development-only. This is neither a scientific protocol, a held-out result, a historical Golden nor approval to alter Stage 9's NO-GO status.

## Reproduced defect, isolated baseline

`AutobiographicalPolicy.project()` starts from the trusted `JournalEntry.event_id`, then copies permitted names from the producer's `causal_event`. When a policy includes `event_id` and the payload also provides that key, the latter silently overrides the real occurrence identifier in the autobiographical projection. A local fixture using exact Git blobs of `src/lab/journal.py` and `src/lab/journal_views.py` reproduced `projected[0]["event_id"] == "fabricated"` even though `JournalEntry.event_id` was a separate 64-character identifier and the technical journal still verified. This is an incorrect projection, not a mutation of the technical journal.

## Minimal correction and frozen checks

1. The trusted occurrence identifier is always `JournalEntry.event_id`; no field supplied by the causal payload can replace it, even when a versioned policy explicitly lists `event_id`. Leave all other allowed projection fields unchanged.
2. Append a physically neutral synthetic `observation_perceived` with `attempt_ref` and an additional conflicting causal `event_id`. Under a policy allowing `("event_id", "t_monde")`, commit its actual technical reference and project it. The projected identifier MUST equal the journal entry's actual identifier, never the producer-supplied string.
3. Check that projection does not modify the hash chain, that the legitimate `AutoSegmentCommit` remains the sole added event, that `attempt_ref` is absent from projected output, and that the original journal, snapshot, and view tests remain green in a strictly labeled **isolated Python 3.13** harness.
4. No change is permitted to the normative specification, normal policy semantics, existing causal journal event bytes, historical Goldens, WorldBody, Planning, Exploration, or Stage 9 verdict. Whole-repository tests, Python 3.11 and Goldens must be marked **not run** until actually executed.

This gate addresses identity provenance within an in-process cooperating API, not arbitrary hostile Python access to private runtime state.

**Stage 11 IN PROGRESS; Stage 9 scientific NO-GO; PR #25 Draft/unmerged.**
