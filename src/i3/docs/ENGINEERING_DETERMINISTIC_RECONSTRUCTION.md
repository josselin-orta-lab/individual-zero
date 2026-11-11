# I3 R2: deterministic cold reconstruction from sealed native engineering steps

**Date:** 11 November 2026. **Source:** the owner-selected I3 architecture and its isolated R2/R3 native engineering step ([PR #1335](https://github.com/josselin-orta-lab/individual-zero/pull/1335), merged `38e36de4`). **Bounded claim:** a newly constructed I3 reference `Mind` and `World` can reproduce each historical **COMMITTED** action, paid decision, learning result and private RNG-dependent state from their deterministic genesis, reject any discrepancy and continue only from a fully sealed, nonterminal engineering ledger. **Not** registered M11, production state ownership, externally anchored anti-rollback, or a scientific World.

## Hypothesis and exact falsifier

Given the same canonical **on-disk I3 source**, genome, initial `WorldSpec` and life seed, each old native action and its true E/V paid result should be reproduced by the reference `Mind.decide -> World.step -> paid learning` on a **detached reconstruction World**. The new state should be identical to the in-process baseline before authorizing another motor. Replaying a stored command by force is **forbidden**: the native Mind must independently choose the same command/parameter and request the same work; the reconstructed World must independently produce the same bodily outcome, learning cost, death and Mind/World/RNG checksum. Missing or altered evidence and any PREPARED/uncertain or terminal record must fail closed.

The falsifier is an action/work mismatch, changed body/E/V charge, changed learned state hash, changed source/genome/spec, unknown sequence, lost PREPARED seal token, possible postmortem motor, or an attempt to continue by modifying the reference policy to fit stored outcomes.

## Engine and custody sequence

The new `NativeEngineeringSession.reconstruct(...)` first checks the claim against the current source/world/genome/seed, then reads the existing local R2 ledger through strict `inspect()`. It refuses any pending PREPARED motor and any DEATH/CENSORED terminal. It then creates **new private reconstruction objects** `World(spec)` and `Mind(genome, seed)` in a fresh Python process or in a separate in-process scope.

For every *already sealed* event, it calls the exact same private native decision and outcome helpers used by `NativeEngineeringSession.step()`, but **without any new ledger PREPARE/COMMIT, external I/O, or treating these historical operations as newly lived motor actions**. It requires complete equality with the historical intent and POST_PAID_LEARNING receipt, including the typed RNG-inclusive state checksums. Only after all events have been independently reproduced does it return an in-process session at the acknowledged ledger head. A later `.step()` still requires the regular CAS + durable PREPARE before a truly new native motor. Two racing copies cannot both publish the same next sequence.

This is deterministic reconstruction of a **fully simulated, closed WorldSpec**. The hidden world data are used only to instantiate the owner-side replica; the Mind receives its own `World.capture()` as before. It is not reconstruction of an external physical world's irreversible effects.

## Test and cost guard

The newly added tests exercise a detached reconstruction versus an uninterrupted independent native reference run; an actual **second Python interpreter** reopening local files, reconstructing and publishing exactly one new step, with the old process rejected as a stale writer; and hard refusal of PREPARED/crashed or terminal histories. Existing seven tests retain native reference parity, source claims and death protections. No old cohort is rerun. Exact-source Python 3.11 and 3.12 I3 CI must pass before merging.

Reconstruction re-executes prior *in-memory model-level calculations as owner verification work*, **not** as additional cognition acquired by the born individual or a free decision oracle. The experiment does not measure host execution cost as physiological E/V and cannot prove adaptive benefit. The R2 ledger also revalidates entire historical records on every new write; total validation cost can become O(n²) over the life. Both costs require profiling/optimization before a scalable generation.

## Nonclaims and future gate

A local SQLite WAL file is copyable/replacable and no **off-machine monotonic sequence anchor** or external witness exists. A hostile rollback of both reservation and ledger might be undetectable, and altered code might be present despite a local source hash. Only **fully sealed deterministic local engineering** history is reconstructible. No independent authenticated M11 cold recovery, real external World continuity, crash-proof exactly-once physical motor, source identity authority or owner-scoped scientific admission is established. Engineering process restart does **not** automatically constitute live registered continuity.

Next R2/R3 gate: independently anchored single-writer identity/sequence, safe versioned state/checkpoint codec (or bounded authenticated deterministic reconstruction contract), real interrupted-process and post-commit crash injection, cost and O(n²) throughput mitigation, and exact-source adversarial tests. I3 remains the owner-selected reference; I1 remains active; Stage 2.1 scientifically `NOT_ISSUED`, prior E3 candidate `CLOSED_NEGATIVE` and new scientific World permissions remain closed.
