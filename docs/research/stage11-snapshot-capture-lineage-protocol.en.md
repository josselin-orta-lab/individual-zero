# Stage 11: geographic snapshot last-capture/visit consistency

**Predeclared before code/test edit (11 October 2026).** Isolated software snapshot integrity check, no held-out data, no scientific or Golden run. English `docs/architecture/reference/en/mvp-specification-v1.2.1.md` remains the sole normative specification.

## Observed snapshot validation gap

`GeographicExploration.export_causal_state()` can produce only two coherent categories: before any actual Perception capture, both `visits` and `last_capture` are empty/null; after at least one real capture, `visits` is nonempty and `last_capture` identifies the last physically captured site. Current `restore_causal_state()` checks that a **present** last capture points into the visit ledger, but accepts **nonempty visits with last_capture=null** when `offered` and `surveys` are empty. This impossible state could influence later novelty, replay and time ordering without corresponding Perception provenance.

## Narrow invariant

Reject any geographically exported snapshot in which `last_capture is None` differs from `visits is empty`, before mutating owner fields. Do **not** infer a fabricated physical capture, drop visits, silently repair timestamps, or alter the visit cap, survey-refresh policy, route-selection algorithm, world physics, or Action Control. Preserve the existing v1/v2/v3 snapshot schema strings and normal exported causal bytes for valid states. Keep current cross-schema refusal.

## Public unit-only gates

For three independently configured owners, (a) legacy local geographic v1, (b) observed-route survey v2, (c) opt-in physical survey refresh v3:

- A pristine empty owner snapshot round-trips exactly.
- A genuinely observed single-site owner snapshot round-trips exactly (v2/v3 optional surveys derived solely from a unit-local capture).
- A deep-copied populated snapshot with `last_capture=None` is rejected with `ValueError`, and the prospective target owner's causal export is bit-for-bit unchanged.
- A deep-copied pristine snapshot with a forged non-null `last_capture` is rejected atomically.
- Valid post-rejection physical capture and survey re-read still work. Explicitly distinguish *unit synthetic capture* from true WorldBody experimental evidence.
- Existing longer public physical replay results remain attached to their old source SHAs; no retroactive signature replacement and no Stage9 held-out.

**Pending tests: NOT YET VERIFIED. Stage11 IN PROGRESS; Stage9 SCIENTIFIC NO-GO; PR draft/unmerged.**
