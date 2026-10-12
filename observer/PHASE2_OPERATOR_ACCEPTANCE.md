# Individual Zero Observer Phases 1 + 2: operator acceptance

Status: **pending operator ACCEPT / REJECT**. Passing CI is technical
readiness only, not an operator, behavioral or scientific verdict.

## Scope and evidence

- Phase 1: local authenticated operator console, fixed subprocess catalog,
  run registry, import and archive handling, cancellation and fail-closed restart.
- Phase 2: recorded journal timeline, 2D frame navigation and diagnostics,
  detached Ed25519 custody inspection, and a **local operator-owned engine
  capture** from real Stage 11 physical steps.
- The new `src/lab/observer_world_capture.py` reads the actual WorldBody
  at a committed physical boundary, *outside I0's cognition*. It writes
  positions and categorized terrain only. The Observer process does not
  import Core packages. No Oracle/Bench capability is passed to the runner.
- A verified local map is still **not** a scientific proof that simulation
  mechanics behave as hypothesized. The engine is the physical source of
  record, and that statement remains separate from independent external truth.

## Preconditions

Use an unprivileged POSIX account, read-only Core checkout, a fresh mode-0700
run root, and a localhost browser. Install the Observer as described in
`observer/README.md`. Never include private Ed25519 signing keys in archives,
environment variables sent to I0, screenshots or Observer forms.

Record OS, Python version, Git HEAD and dirty-worktree state, Observer token
handling, run identifiers and SHA-256 file digests.

## Operator checks (one final gate for both phases)

1. **Access isolation**: wrong token rejected, valid token accepted,
   logout invalidates access; no external port exposure. The Core runs
   autonomously with Observer absent.
2. **Phase 1 smoke**: bootstrap 3 cycles yields Lab events and original files
   with correct SHA-256. Cycles must not be mislabeled physical steps.
3. **Physical recorded replay**: choose `mortal_stage11` with 7 steps.
   Confirm SUCCESS, executed steps 7, `assertions_passed=true`, no Oracle or
   Bench loading, no scientific validation. Confirm `journal` and
   `world_frames` exist with intact manifest hashes.
4. **2D time navigation**: open Replay historique on that local run, select
   `journal`, move the scrubber from 1 through 7 and inspect at least three
   steps. Map positions must match the recorded
   `world_transition_experienced.position_after` for the corresponding
   `(t_monde, attempt_ref)`. The 32x32 grid, terrain legend and time labels
   must be legible. A request for step 8 must not display a guessed frame.
5. **Long-run continuity**: repeat a 600-step diagnostic in a fresh run root.
   Inspect first/middle/last frames (1, 300, 600), stable identity, complete
   unique step sequence and record digests; no rollback or resurrection.
   This is development evidence, **not** a 600-step scientific verdict.
6. **Invalid imports and custody**: mount an imported archive with an
   otherwise well-formed `world_frames`. Its source should be browsable and
   structurally diagnosed, but should **not** render an authoritative map.
   Deliberately mismatch frame position, attempt ref, journal head/count,
   SHA-256, Ed25519 key and individual identity in disposable copies. Each
   must fail closed. Never modify the original evidence.
7. **Security and mortality**: verify no `oracle_canary`, Oracle capability,
   Bench secret or privileged truth appears in exported frame/journal bytes or
   I0's input. Cancel a running diagnostic; no SUCCESS or map may be exposed
   for a cancelled, failed or interrupted run. After simulated crash, existing
   run roots must remain quarantined. Do not resume a dead identity.
8. **Archive preservation**: download original journal/frames and ZIP, compare
   independently computed hashes to the manifest, confirm that reads do not
   change originals. Re-run the independent complete journal auditor against
   trusted head/count when available.

## Classification

- `capture_integrity_verified=true`: complete local engine recording,
  Observer-owned manifest and journal/position consistency checked.
- `map_authorized=true`: *only* for technically verified local engine
  recordings in SUCCESS, not for imported archives.
- `physical_truth_verified=false`: no external Oracle-level proof is claimed.
- Scientific and operator validation remain `null` until their own gates.

Do not mark either Phase 1 or Phase 2 ACCEPTED solely because this checklist
exists or GitHub Actions are green. The operator records **ACCEPT** or
**REJECT**, with evidence, date, versions, and observed limitations.
