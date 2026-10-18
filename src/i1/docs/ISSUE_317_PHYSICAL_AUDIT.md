# I1 issue #317: independently authenticated paired physical audit (2026-10-18)

**Status: decision bootstrap SOFTWARE GO; one physically applied, recalled-site step demonstrated; remote navigation and learned re-use SCIENTIFIC NO-GO.** This is not a survival GO or an instruction to close #317. I0 and witness PR #316 are untouched.

## Immutable provenance and physical custody

- Reference: untouched `main` commit `9ad819f2ae61df9de3408d68defbff66525513ee`.
- Corrected engine: `c775281862c177ed35d87331bd97fad35c0d326e`, within draft PR #318. Later changes before this report affect test code, documentation and workflows only, not the I1 decision implementation.
- Treatment: GitHub Actions [run #39163777292](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39163777292), eight independent autonomous mortal WAL lives.
- Paired control and independently verified comparison: [run #39164274266](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39164274266), including artifact `i1-317-paired-summary`. The comparison requires exact code commits, matching world preset and physics digests, matching seeds, consistent life identity, durable WAL hash-chain verification and journal-head equality.
- Worlds: `oasis`, `foraging`, `dry-valley`, `blocked-route`, seeds 1141 and 1142, horizon at most 300 each. Each simulated death remains final. No controlled actor, no injection, no rollback.
- The regenerated I1 source / structural CI [run #39164277270](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39164277270) passed. This cannot substitute for physical evidence.

## Complete paired outcome

| Pair | World steps (control → corrected) | Moves (control → corrected) | Memory Competition crossings | Applied memory steps | Returned remembered sites |
| --- | ---: | ---: | ---: | ---: | ---: |
| blocked-route 1141 | 204 → 204 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| blocked-route 1142 | 204 → 204 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| dry-valley 1141 | 176 → 176 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| dry-valley 1142 | 176 → 176 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| foraging 1141 | 230 → 230 | 1 → 1 | 0 → 2 | 0 → 1 | 0 → 1 |
| foraging 1142 | 227 → 227 | 37 → 37 | 0 → 0 | 0 → 0 | 0 → 0 |
| oasis 1141 | 300 → 300 | 38 → 38 | 0 → 0 | 0 → 0 | 0 → 0 |
| oasis 1142 | 300 → 300 | 51 → 51 | 0 → 0 | 0 → 0 | 0 → 0 |

The same six of eight individuals die in both arms. Average observed steps: 227.125 for both. Moves: 127 for both. Drinks: 2 for both. Eaten actions: 7 → 8; collected: 7 → 8. Consolidation commits: 73 → 72. Total accepted requested UC: 66,569 → 66,611 (+42). Counts are descriptive paired data, not population-wide causal estimates or a guaranteed survival benefit.

## Source-derived quantitative diagnostic

The corrected `foraging/1141` WAL contains two independent memory alternatives reaching the fixed threshold simultaneously at world step 10, cognitive cycle 3:

- `sighting:berry_a:9:8` and `sighting:wood:7:8`.
- Last five observations of the berry candidate accumulator before/at crossing: 0.32284061315334034, 0.39332493944699637, 0.4309680929739673, 0.4836412340368298, **0.5453353911605493**.
- Last instantaneous evidence: 0.0378. Threshold: 0.5. Maximum observed accumulator / threshold for this life: **1.0906707823210986**.
- One of those two crossed alternatives is admitted, sent as `se_deplacer east`, physically applied and followed by observed position `(9,8)`, as attested by the sealed WAL. The other crosses but is not admitted.

**Important correction to automated reporting:** the initial paired artifact erroneously contains `max_accumulation_over_threshold: 0.0` for every life because `competition_cycle.traces[*].threshold` and `accumulator_after` are encoded by the canonical WAL serializer as `{"$f64": "0x..."}`, not bare numeric JSON. That metadata field is **invalid and must not be used**. The correct values above were independently recovered by hex-float decoding the actual authenticated WAL; the original journal and evidence are not rewritten.

**Scope of the behavioural proof:** at world step 10, the berry at (9,8) was **still visible immediately east** in the `perceptual_capture.agency_visible_adjacent` row. This proves the explicit memory-provenance cognitive proposal was causally involved in one physical step toward a previously seen entity. It **does not demonstrate remote retrieval of a currently unperceived site**. The next hop and final destination are the same cell. Calling this a remote return would inflate the scientific claim.

A real `td_update_published` occurs at step 11 with `previous_signature=memory_place_return:sighting:berry_a:9:8` and includes that memory signature in `updated_signatures`. Nevertheless, **all 563 subsequent/overall memory evaluations in that life are marked `unlearned`**; none exhibits a learned memory value used in a subsequent decision. The TD reward is physiological variation across an experienced transition, *not* verified causal proof of the berry's intrinsic helpfulness. This prevents a scientific claim of learned site-usefulness or autonomous experience-based re-selection.

## Other contextual findings

- Treatment `foraging/1142`: 72 memory assessments, zero crossings; maximum real accumulator/threshold is about 0.2472.
- Treatment `oasis/1141`: 243 memory assessments, zero crossings; maximum about 0.8436.
- Treatment `oasis/1142`: 40 memory assessments, zero crossings; maximum about 0.5082.
- Treatment `blocked-route/1141` and `dry-valley/1141`: no memory evaluation or physical movement, despite ordinary cognitive UC and survival expenditure.
- The score in `src/i1/modules/stage11_evaluator.py` is confidence-weighted informational interest plus independently available Stage8 evidence. Active need pressure controls which goal is active; there is no direct pressure multiplier on memory intrinsic evidence. Absent learned entity-goal usefulness, adding such a multiplier could create a fictitious physiological preference. Do **not** solve by `if thirsty: seek water`, fabricated TD, arbitrary threshold changes or guaranteed memory wins.
- Memory-option identity now persists for the same previously observed entity-place, origin and next hop, not across materially changed motor plans; the remaining lack of demonstrated multi-hop intent is a distinct validation gap.

## Scientific gate

SOFTWARE GO for the proven single-hop accumulation/bootstrap defect, **SCIENTIFIC NO-GO for end-to-end memory-guided autonomous navigation and learned efficacy**. A held-out paired cohort and a simple genuine *out-of-sight* route with no forced motor output are still needed. Explicitly observe Stage8 learned memory evidence influencing a later accepted physical decision. Monitor survival, vital need changes, sleep, CPU/UC, consolidation and M11 cold recovery. Do not use the initial buggy maximum-ratio field or earlier broken I1 experimental cohorts as proof.
