# I3 Stage 2.1 replay-content local mechanism: source-bound software result

**10 November 2026. Synthetic detached Mind experiment, no World/life, no viability claim.**

## Reproducibility and frozen question

The synthetic [prospective 48-snapshot plan](CONTENT_SELECTION_LOCAL_FALSIFIER_PLAN.json) and [frozen local protocol](CONTENT_SELECTION_LOCAL_FALSIFIER.md) were written before any test run. The software-only source [PR #1257](https://github.com/josselin-orta-lab/individual-zero/pull/1257), exact head `906ce1db9d1dba5ffbd6ef4718d4a12b8a321647`, was tested in [GitHub Actions run #42786987609](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42786987609).

The code creates **48 independently numbered synthetic Mind snapshots** with fixed genome and Mind seeds, each containing 12 artificially constructed internal memory transitions. On two deep copies of each same initial Mind, it performs **3 actual P1.3 `Mind._td` updates** per arm. PRIORITY chooses the highest-|TD-error| memory positions; RANDOM-CONTENT samples a genuine set of three distinct memory identities from a separate HMAC stream, without replacing an original memory, changing the count or touching either Mind's RNG. A fresh `CognitiveBudget` funds identical `CognitiveWork` in each arm and the current `BodyLaws` computes the same energy/vigilance *would-be World debit*. The starting source Mind and its RNGs remain unchanged.

**Important physical distinction:** no World ever debits that charge; neither arm is a biological life. The physical cost values are the exact **model-level bill if World debited it**, not actual energy or vigilance spent by a living simulated individual. The experiment tests a possible local learning mechanism, not whether it helps survival.

## Observed fixed-panel findings

| Exact fixed 48-snapshot local metric | Result |
| --- | ---: |
| Synthetic Mind state pairs completed | **48 / 48** |
| Replay updates per arm per state | **3** |
| Memory subset selections different | **48 / 48** |
| Final learned-value vectors different (L1 > 1e-12) | **47 / 48** |
| Mean L1 difference of learned values between arms | **0.2048207910** |
| Mean absolute update magnitude, TD PRIORITY | **0.7949866089** |
| Mean absolute update magnitude, RANDOM CONTENT | **0.9450651222** |
| Identical authorized model work | **PASS** |
| Projected energy bill per arm/state | **0.131** |
| Projected vigilance bill per arm/state | **0.176** |
| Original source Mind and both RNG streams untouched | **PASS** |
| Worlds entered / full-life steps / scientific lives | **0 / 0 / 0** |

The local execution finished successfully under **Python 3.11 and Python 3.12** with matching numerical outcomes and no reported test invariant failure. Original synthetic-only output receipts are [Python 3.11 artifact #13749343633](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42786987609/artifacts/13749343633), SHA-256 `028298217f83265cfd6529a4ebdaba23cd3d3acb470e147ae8bc2244a5e0a108`, and [Python 3.12 artifact #13749498225](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42786987609/artifacts/13749498225), SHA-256 `16849fceb208c001a9a026922dd0f38bc334cd54b4b078cae960bb847cf4ef45`. The receipts contain synthetic trial-level results and are intentionally not biological original evidence.

## Meaning, negative evidence, and limitations

The result confirms that **choosing *which* memories are replayed can change the learned-value state at equal replay count and identical model-level physical tariff**. The effect is not universal across these synthetic snapshots: one of 48 produced the same final learned-value vector despite selecting different memories. Keep that null case.

RANDOM's mean absolute update magnitude exceeds PRIORITY's on this artificial fixture. **Larger TD updates are neither known to be better nor worse** for expected system viability. The order of synthetic memories, fabricated TD magnitudes and short test horizon could affect this local numerical magnitude. Because both arms start from identical copied state and pay the same declared work, the immediate value-state difference can be attributed to the changed replay-content selection in this software experiment; it **does not** isolate its downstream value in a live closed-loop organism or establish expected survival under any ecology.

No biological fitness, life longevity, new ecology family, generalization, distributional uncertainty, independent source witness, registration, non-inferiority margin, or evolutionary stage conclusion follows from this synthetic panel. The previously closed 64-triplet GATE/RANDOM comparison remains **0/64 finite horizon survival difference** and should never be interpreted as a test of random memory-content selection.

## Scientific decision

**TECHNICAL LOCAL CONTENT-SELECTION EFFECT DETECTED / BIOLOGICAL BENEFIT UNKNOWN.** Preserve existing GATE/FIXED/RANDOM source and cohorts unchanged, and follow the independent prospective design gate in [issue #1258](https://github.com/josselin-orta-lab/individual-zero/issues/1258). The next prospective full-life experiment may cross randomized versus TD-prioritized content and GATE versus randomized replay-count policies, but only with separately registered indices, independent source review and complete real physical funding and original custody. There is **no scientific GO or I3 activation** from this probe.

This report is post-execution but references only the previously fixed software protocol, exact source SHA and independently observable CI output. No result-driven threshold or selective trial exclusion was introduced.
