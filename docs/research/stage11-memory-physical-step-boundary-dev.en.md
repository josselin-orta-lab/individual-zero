# Stage 11: versioned Memory boundary for physical-event custody

**Status: software development only, before integration verification.** This mechanism does not change the Stage-9 baseline, independent held-out status, or canonical Causal Model proof requirements.

## Reproducible problem in the public fixture

At seed 41, public `small_water_gain`, three-visit development policy:
- Physically applied test steps at 24-step cutoff: **8, 9, 10**.
- Immediately after each command, the canonical Causal Model recorded a pending physically applied test for that step.
- After later Memory ingestion, only steps **8 and 9** remained as closed physical action witnesses; the prospective P-47 report concerned **step 10**.
- Same pattern for the distinct 32-step schedule: applied **9, 10, 11**, only **9** remained physically closed; report concerned **11**.
- No matching closed physical action + P-47 report existed, so **zero interventions** were admitted. This is a legitimate result under the current evidence gate, not evidence that the comparator is wrong.

## Narrow root-cause candidate

Reference `MemoryConfig.max_episode_steps=2`. In `EpisodicMemory.ingest_autobiographical`, a `max_length` boundary was evaluated for **every** autobiographical event. Events for one world step can include both `command_experienced` and `world_transition_experienced`, and the sorted first event of a boundary world step could prematurely close the episode before its paired physical event is ingested.

The canonical `CausalModel.ingest_closed_causal_action_episode` correctly refuses an episode containing only one half of this physical pair. The problem to test is segmentation, **not** the proof requirement.

## Versioned I0-vNext-only experiment

The opt-in `EpisodicMemory(..., atomic_world_step_length_boundary=True)` defers a **max-length** closure until the final event of the same world step **in the current new-event batch**. Named boundary triggers (goal change, prediction error, zone change) retain their existing rules; this flag does not relax those or promise to merge unrelated episodes.

- The Stage-11 runtime selects a distinct MemoryConfig version `p34-stage7-reference-v1+atomic-world-step-length-v1` before birth, installs that variant before the first step, and includes its `boundary_semantics` in snapshots.
- Every earlier Stage-7, Stage-8 and Stage-9 runtime continues to instantiate the original Memory implementation with the flag **false** and the same snapshot schema and config version.
- Snapshot restoration checks that a stage-11 atomic-boundary snapshot cannot silently enter historical Memory.
- Unit tests check that command/transition of one world step stay in the same max-length-closed episode when present in the same batch; this is a software contract, not artificial causal evidence.
- Public Stage-11 hydration diagnostics remain pure observations; no forced hypothesis, synthetic event, oracle, or training label is inserted.

## Acceptance boundary

A Memory episode with two physically witnessed events is not itself a confirmed causal intervention. A distinct independently closed P-47 report, exact physical command/transition, matching times and variables, and the Causal Model's original phase-5 and n2 gates must **all** still hold.

Inspect any changed public results, record negative outcomes and recheck deterministic replay. **No Stage-9 held-out or scientific Golden GO.**
