# Issue #317: physical out-of-sight corridor finding (2026-10-18)

## Provenance and protocol

- Exact engine SHA: `1446a78a54c95b289e1f5654313d84849f5383df` (core multi-hop algorithm unchanged since `0128f4a18631dc5c7d5752b65b06d27787a26ca4`).
- Actor-free `memory-corridor` preset, 300 maximum steps, seeds 1141, 1142, 2027, 2028; [physical workflow #39169736198](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39169736198).
- All four lives completed and the independent `tools/audit_i1_spatial_navigation_314.py` hash-chain validations passed. Archived WAL artifacts: `i1-317-corridor-{seed}`.
- Preset obstacles make a short surveyed passage, with witnessed water and food at spawn and other observable entities along it. An environment shape is a test condition, not an I1 oracle or scripted decision.

## Authenticated physical outcome

| Seed | Lifetime | Physically applied memory actions | Out-of-perception multi-hop first steps | Fully arrived from outside perception | Actual learned-TD subsequent memory actions |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1141 | 300, alive at horizon | 9 | 0 | 0 | 6 |
| 1142 | 300, alive at horizon | 4 | **2** | 0 | 2 |
| 2027 | 300, alive at horizon | 1 | 0 | 0 | 0 |
| 2028 | 300, alive at horizon | 2 | 0 | 0 | 0 |

**World step 71 of seed 1142:** following his own observations of `sighting:wood:9:8`, I1 stands at (11,8), with wood at (9,8), not currently visible. The option `...wood:9:8:at:9:8:from:11:8:via:10:8` reaches Competition threshold and is admitted by Action Control. An authenticated `se_deplacer` reaches (10,8). At step 72 the owner logs `i1_place_memory_intention_continued` with expected observed position (10,8), new proposal `...from:10:8:via:9:8` and *bounded* carried accumulator 0.25. The subsequent memory evaluation remains below the actual new threshold (approximately 0.443), and sleep is legitimately selected. **No forced continuation or arrival occurs.** A similar remote first hop happens at step 86, with continuity at 87; sleep again wins.

This proves *one physically initiated return to a previously seen, currently invisible entity-place*, with two replicated events in one individual and verified one-step intent continuity. It **does not** prove a completed multi-hop return, exploitation of the wood, or improved survival.

The first remote crossing (step 71) is **unlearned** in Stage8, while the second (step 86) includes a previously published TD value. This confirms experience can participate later but does not establish that the resource is intrinsically beneficial. Across all 4 lives all 4 are alive at the 300-step censoring horizon; this is not a survival comparison because the corridor was designed for mechanistic validation.

## Diagnosed continuation pressure, not a reason to override the sleeper

At step 72, carried memory evidence is 0.25; memory accumulation grows on cycles 1 and 2 to about 0.282 and 0.334, still below the configured engaged threshold. A separately eligible sleep candidate wins. At step 87, carried memory evidence is again 0.25; memory accumulation progresses across 3 cycles to about 0.428, below the engaged threshold. Sleep is selected. Stage10 night/fatigue/sleep and Competition operate through their legitimate channels. Their arbitration cannot be bypassed to force completion of a remote trip.

**Architectural priority after this test:** establish whether the memory intention survives interruption by other legitimately selected actions or during the mandatory multi-step sleep period, and whether a personally witnessed entity-place could maintain a bounded *deliberative* commitment separate from a particular motor option. Any cross-sleep persistence must survive M11 cold restore, be contradicted by current perception, and still allow urgency, danger, exhaustion and learned-negative evidence to win normally. Avoid increasing intrinsic value or reducing thresholds just to obtain arrival.

## Scientific gate

The mechanical bootstrap and first-hop/continuation are physically demonstrated in one independent world and one seed. **Full remote return, repeated generality and learned post-return usefulness remain NO-GO.** No modification to I0, main, PR #316, physical death, TD reward, or action veto.
