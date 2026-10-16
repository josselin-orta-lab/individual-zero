# Individual Zero / issue #136 — D1-B retrospective scientific report

**Date:** 2026-10-16. **Verdict:** `MECHANISM_SUPPORTED_LIMITED_WITH_SAFETY_NO_GO` in a deliberately tuned *exploratory* I1-only cohort; operational and Stage9/Stage12 scientific acceptance remain **NO-GO / PENDING**. The runner's preregistered deployment-unsafe summary field properly reads `"scientific_transfer_verdict":"NO-GO"`; it does not deny the positive nominal mechanistic witness.

## Provenance and time ordering

- D1-A must remain the archived **negative** 80-life / 960-real-step experiment with 0 actual drinks and no first-person updates: [workflow 38866267354](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38866267354), SHA `504be6c0c2b057da51d3ee4da9783c5db69e2d28`, report `docs/research/i1-issue136-d1a-negative-results-2026-10-16.en.md`.
- The separate **D1-B hypothesis**, including the enhanced common local-probe evidence preference, new north training source and t=4 world relocation, was registered BEFORE D1-B changes and physical execution: `docs/research/i1-issue136-d1b-prereg-2026-10-16.en.md`, commit `43bfacb055a0bbbdd40a530bae477d19221a43b6`.
- D1-B **actual experimental source HEAD** `0df337cea84af6ae117c67cf9bd1bc44f24d31cf`; both Python 3.11 and 3.12 passed in [GitHub Actions run 38867230098](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38867230098). Each Python version runs the **same fixed deterministic allocation**: 80 distinct mortal I1 births / 40 ON-OFF matched pairs. This is ONE scientific cohort replicated technically, **not 160 independent lives**. Raw artifacts `i136-d1b-py3.11` and `i136-d1b-py3.12` contain `lives.jsonl`, one independent `life.wal` and canonical journal per life.
- All reports refer to the unmodified nominal WorldBody engine and isolated I1 descendant; no changes to checked-in `src/i0` or `src/lab`, no Oracle or Bench feedback. A logged exogenous t=4 world relocation to the remote test field is **not** I1's chosen action or causal responsibility.

## Measured outcomes, including every death

| D1-B new-world stratum | ON lives | First real exploratory drinks ON | Admitted first-person effects ON | Full new-source transfer ON | Transfer OFF | Deaths ON / OFF |
|---|---:|---:|---:|---:|---:|---:|
| North | 8 | 8 | 8 | 8 | 0 | 0 / 0 |
| East | 8 | 8 | 8 | 8 | 0 | 0 / 0 |
| South | 8 | 8 | 8 | 8 | 0 | 0 / 0 |
| West | 8 | 8 | 8 | 8 | 0 | 0 / 0 |
| Hidden lethal east | 8 | 8 | 8 | 0 | 0 | **8 / 0** |
| **Total** | **40** | **40** | **40** | **32** | **0** | **8 / 0** |

The fixed-E, probe-only OFF controls also drank on the initial training source in **40/40** lives but were not permitted to turn that into a first-person learned model state. Total **896 real physically executed steps**, not the 960 hypothetical maximum after 8 terminal deaths at physical step 4. No technical exception, claimed-hard violation, refused UC, invalid WAL or bypass of Action Control was detected.

For the learned arm, the actual source trace in the nominal directions is:

1. At world step 1, Stage11 Exploration proposes and WorldBody executes a voluntary north move into the originally unseen local water cell `(2,1)`. This is not an operator-directed training command.
2. At step 2, the **common birth-time exploratory preference** (both arms) may propose `boire`; existing Competition and Action Control actually accept it and WorldBody raises the perceived water by **+40**.
3. At step 3, an **authorized later first-person capture** reveals this change. Only learning ON charges and admits a **bounded empirical bodily water-delta association** with both capture hashes, actual applied-command hash, per-life ID, and source step2 / observed step3. It does not identify unobserved external causes or certify safety. A second `boire` may be physically executed on that step.
4. At step 4, the Lab's explicitly logged `set_position` moves the body **as an environmental event** to a remote cell. From the new authorized capture, only learning ON proposes a `lived_transfer` single-step `se_deplacer` into a *visible adjacent* new water source, and it genuinely crosses Competition and Action Control. This is the only counted voluntary **transfer movement**; the external reposition is not counted.
5. At step 5 in the 32 safe ON cases, a new eligible `boire` is executed on the second source, with measured water rise, for example from **81 to 100** (clamped, +19). Every transfer score requires both physically applied steps, not mere proposals, admission or prediction.

**Unseen hidden-danger comparison:** For each of the eight matched ON east versus hidden-lethal-east experiments with equal index, an independent raw-artifact audit found **identical step-4 authorized pre-action capture payloads** and the **same voluntarily selected eastward command**. Nevertheless, the first WorldBody applies the movement while the second produces real death. No hidden lethal label was fed into the living model, and it never declared safe/terminal certainty. This is a genuine epistemic indiscernibility limit at first encounter, **not evidence that I1 knew which source would kill it**. It is still a severe negative real-world *decision policy* result: learning expands into unknown potentially fatal cells and creates 8 extra deaths compared with the passive fixed-E control. The previous A2.31 warning remains corroborated, not resolved.

## Resource costs and audits

The narrow water-owner operations are explicitly positive, charged in P-43 `compute_charge` receipts, with no observed refusals. In a representative eight-life nominal east stratum, **learning ON** has **128 accepted water-operation UC** vs **32 OFF**, with overall accepted journal charges **2152 ON vs 2136 OFF**. These are *actually journaled accepted operation charges*, **not CPU time or complete cross-cohort efficiency estimates**. A mortality-truncated arm cannot be interpreted as efficient simply because it spent fewer lifetime UC.

After GitHub Actions success, a separate artifact-level audit opened **all 80** Python-3.11 `canonical.jsonl`/WAL pairs and checked bytewise WAL correspondence accounting for its one canonical terminal newline, SHA-256 against each life report, genuine owner acquisition at t=3, positive physically measured t=5 water gain on nominal transfer, no post-death action, and terminal `step_closed` on the 8 lethal lives. All passed. Python 3.12 independently passed the same cohort through CI; this is software reproducibility, **not independent biological replication**. The source JSON retains the runner's generic `"schema":"i1-issue136-d1-summary-v1"` despite distinct D1-B `prereg_sha`, `input_lock_sha`, `source_sha` and life IDs; this naming carryover does not change the frozen data.

The I1-only M11 birth contract and cold-recovery smoke tests passed on both Python versions before the cohort. A further **post-result technical gate**, distinct from this preregistered scientific cohort, was added to verify that a genuinely learned t=3 water-model state survives an M11 cold restart and affects the next real t=4 decision; it is not counted as extra scientific lives.

## Scientific limitations and next safety experiment

This is **not full #136 resolution**: the initial water-probe preference and local action notion were engineered equally into both arms, and the preference was **tuned after inspecting D1-A failures**. D1-B is thus an exploratory mechanistic study, not an untuned confirmatory evaluation. Water targets are visibly adjacent **after an external relocation**, not newly discovered by unaided long-distance roaming. All rows share deterministic physics and relatively narrow development fixtures; further blind heterogeneous worlds and long independent mortal trajectories are necessary.

In the next **separately preregistered** I1 safety/decision study, restrict *assertions* to learned water-effect evidence but explicitly evaluate commitment to physically irreversible, unknown-outcome movements, with UC-bounded evidence use, conservative admissibility or abstention and independent hidden-lethal matched tests. No causal oracle, omniscient hazard classifier, after-death learning or posthoc safety prior may enter cognition. Any purported safety improvement must survive nominal-transfer/unknown-risk tradeoff and match actual realized welfare, not simply declared uncertainty. Maintain I0 as immutable control.

**Decision:** I1 experimental Draft PRs **#223 and #224 remain unmerged**, issue **#136 OPEN**, Stage9/Stage12 scientific acceptance **NO-GO/PENDING**. Mechanistic first-person learning is *limitedly demonstrated*, but behavioral safety demonstrably fails and operator acceptance cannot be inferred from CI.
