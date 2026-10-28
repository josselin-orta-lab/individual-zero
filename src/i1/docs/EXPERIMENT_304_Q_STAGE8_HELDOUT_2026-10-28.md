# I1 #304 / #438: preregistered external holdout of learned-Q Stage8 influence

Date: 2026-10-28. Base: `f3beb4719d31e9848596364f2481ff4f42f83a44`. Research only, not a motor-policy change.

## Why a holdout?

The original paired M11 `dry-valley` case (#592, #593) was selected as a discovery: at step 12, canonical I1 chooses `attendre` and Stage8-Q-read-masked research I1 chooses `dormir`. The homeostatic distance favors canonical at this step by 3.5 **relative** points but both worsen from the original body; this is not a durable adaptive GO.

## Primary question and preregistered independent environments

Examine exactly two **previously unused registered world layouts for this read ablation**: `oasis` and `foraging`. For each, born identities `i1:304:heldout:<preset>:a` and `i1:304:heldout:<preset>:b`. Each identity is paired between canonical I1 and a test-process, **pre-birth** Stage8-only Q-read-masked version. Up to **18 physical steps** per arm (4 pairs / 8 lives total), with no birth selection, no survivor filtering, no retrospective extending the horizon, and no conditional search for a favorable result. The identity suffix is not an independent realization of the environment layout: the two **different registered presets** supply the environmental contrast.

Each arm owns a distinct current-generation M11 SQLite ledger, with a fully mortal canonical `birth_i1_m11`; no overrides to time, life, decisions, Q/TD update rule, P-40, UC, physical rewards, or thresholds. The variant masks `LinearTDValues.learned_value` **only within a paid Stage8 evaluation** and records the genuine value, retaining Planning's original read and all owner state.

## Primary outcomes fixed before inspecting the holdout

For each pair, report, including `NOT_EXPOSED` and censor/death:

1. Number of genuinely learned Stage8 values hidden and paid matching Stage8/Competition receipts.
2. First physically applied action divergence, or none; validate identical full command prefix, born body and world/physics digest, pre-divergence owner TD, GoalManager, Competition, fatigue, UC and P-40 at the divergence.
3. If a first matched divergence exists, evaluate the *postcommit* four-channel body and weighted distance to personally born ValueAndNeeds setpoints. Report whether **the canonical decision improves homeostasis relative to its own pre-action body**; compare this improvement with the masked arm. A relative advantage alone is insufficient for the absolute-gain flag.
4. Explicitly report fatigue and sleeping state. An immediate improvement is not a measure of survival, consolidation, delayed sleep benefit, or natural long-term reuse.
5. Compare the registered environments separately. Never aggregate the four pairs as independent physical worlds. A motor difference absent in another environment does not falsify its existence on the original dry-valley example.

## Hypotheses and interpretation

- H0-motor: No exposed, adequately matched first applied-command divergence associated with Stage8-Q read masking in this fixed holdout.
- H1-motor: At least one such matched first physical divergence with an actually learned, personally experienced Q read.
- H0-utility: At exposed first divergences, canonical does not have greater **absolute** one-step homeostatic improvement over the masked arm.
- H1-utility: Both a greater relative improvement and a *positive* canonical absolute homeostatic improvement are observed. This is an **exploratory immediate proxy** in a preselected cohort, not an adaptive GO, and must be compared with competing effects and the relevant needs.
- `NOT_EXPOSED`: no authenticated learned Stage8 read and/or no comparable motor option. `L3_NOT_ESTABLISHED`: read exposed, no changed command. `INVALID`: premature divergence or provenance/physical mismatch. An unmatched divergence is `SCIENTIFICALLY_INCONCLUSIVE`.

**No claim of useful autonomous learning, policy improvement, generalization, or durable re-use** from this small test, regardless of sign. A later preregistered longer-horizon independent world-reversal study and actual later free choices would be necessary for a global GO. If all four pairs fail exposure, do not tune parameters or add artificial affordances to turn this into a success.

## Operational controls

Reuse the exact verified #592/#593 M11 test harness. Report version digests, lived owner updates and actual charges, and preserve all negatives. The test is permitted to fail only for broken contracts or run integrity, not because it records a scientifically negative outcome. Full 4/4 exact-head CI Python 3.11/3.12 before merge. Keep I0, I1 canonical modules, `engine.json` and `CAPABILITY_INTEGRATION.md` unmodified until a real evidence-level change is verified.
