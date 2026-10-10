# Stage 11: public hydration decision-funnel development diagnostic

**Date:** 2026-10-10 (GitHub CI UTC). **Classification:** DEVELOPMENT / SOFTWARE DIAGNOSTIC ONLY. This is **not** an independent held-out experiment, scientific Stage-9 acceptance, INV-25 closure, a Golden, or a claim of autonomous causal establishment.

[Résumé français](stage11-public-hydration-development-2026-10-10.fr.md)

## Exact code and software provenance

- Tested source commit: `85685f353b30c8e43355c066d98b774e22b92445` on `i0/vnext-stages-10-12`.
- [GitHub Actions quick unit run #38090244262](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38090244262), job `114325025426`: **700 tests passed** with Python 3.12, plus bootstrap smoke. Full two-version CI, 300-step goldens and scientific validation were **not** executed in this run.
- Command: `python -m lab.stage11_hydration_probe` from that source checkout.
- Diagnostic protocol: `stage11-public-hydration-funnel-dev-v2`.
- Public seed: `41`; public world: `small_water_gain`; world steps: `18`. The Stage-9 control uses the existing positive hydration diagnostic, matched schedule and frozen reference Equipment.
- Same scenario schedule SHA-256 in both runs: `42a4a3bb02e61c5d5356b4360f342158c11060be2da224b89e559882e7e5b966`.
- Control Stage-9 journal head: `2028e6ce0afed96189f07e8fca2b169fb7c6966cd80ca307e7fe7cbef0d618e7`.
- I0-vNext Stage-11 journal head: `6f37bb562e03a5ad5363b497b85e4f7adb31254b27d550337503719baa1445ab`.
- Canonical diagnostic evidence SHA-256: `bc66275858c0e143bacb9afd7d35ab59631374d594801166d829632f62f79c68`.

The CI log preserves the machine-produced `stage11_public_hydration_diagnostic=` JSON row. These digests are software integrity checks, not an independent timestamped scientific witness. The Stage-9 and vNext journals are necessarily different because the mechanisms and trace events differ; both are internally verified by their respective software runs.

## Observations

| Observable | Existing Stage 9 | I0-vNext Stage 11 |
| --- | ---: | ---: |
| Published causal status | `hypothese_causale` | `hypothese_causale` |
| Test option proposal emissions | 37 | 4 |
| Unscored test evaluations | 37 | 0 |
| Intrinsically scored test evaluations | 0 | 4 |
| Distinct intrinsically scored test options | not applicable | 1 |
| **Applied causal-test commands** | **0** | **3** |
| **Canonically verified causal interventions** | **0** | **0** |

Additional Stage-11 measurements:

- First causal hypothesis published at world step **8**.
- All **4** generated test proposals recorded `simulation_status=unavailable`, with `simulation_reason=equipment_input_unseen`.
- **2** lived causal action records remained pending; both already carried a Memory-closed physical episode and command/transition provenance.
- **0** published DC-09/AgencyComparator reports matching a causal-test option.
- **0** Global Modulation profile transitions in this specific 18-step world. This does not test activation/deactivation in other worlds.

**Observed software advance:** a causally motivated option obtains real P-48 intrinsic evaluation and can win ordinary Competition and Action Control, resulting in three applied commands. This is a statement about this fixed development fixture, not a robust or held-out effect.

**Observed missing result:** no canonical intervention was established, and no simulator correction or INV-25 finding can be inferred. A physical command, a closed Memory episode, and an accepted causal intervention are separate records.

## Mechanistic analysis, not a fabricated witness

The code path explains the missing bridge without requiring hidden-world speculation:

1. `assess_executable_causal_test` permits a physically accessible safe test when the frozen Equipment exact transition is unseen, but leaves `PlanStep.predicted_consequences=()`, explicitly **without** a numerical invention.
2. `ActionControl.record_sent_prediction` declines to open a pending comparison when there are no predicted consequences.
3. `CausalModel.promote_lived_causal_interventions` requires an independently sourced, previously published comparator report in addition to Memory-closed physical command/transition evidence.
4. The observed diagnostic contains two physically closed pending actions, **no matching published comparator report**, and consequently no promoted intervention. The third applied command need not have reached an episode-closure boundary at the 18-step cutoff.

This diagnosis identifies a *prediction availability and verified comparator handoff* problem. It does not justify synthesizing predicted water gains from world configuration, oracle labels, the benchmark, or the observed outcome itself.

## Follow-up gate (not yet completed)

- Determine whether a prospective, versioned prediction can be obtained from already experienced, independently witnessed autobiographical outcomes, consistently with §§9.5–9.6, 12 and 13 of the normative English specification. Distinguish that source from unlearned Equipment output and prevent signal double counting (INV-14).
- If no independently grounded prospective numerical prediction is available, keep the comparator and causal-intervention result **unavailable**, not zero or successful.
- Measure bounded public-world coverage across more development worlds and seeds, include null controls, retain negative outcomes, and recheck exact replay.
- Complete Stage-11 geographic exploration target generation, boredom beyond causal questions, and physically observable threat/recovery activation and deactivation.
- Preserve the separate [Stage-9 held-out NO-GO decision record](stage9-heldout-prelaunch-decision-record.md). Only a real prospective independent release may authorize a held-out campaign.

**Gate: Stage 11 IN PROGRESS. Stage 9 SOFTWARE IMPLEMENTED / SCIENTIFIC VALIDATION PENDING / NO-GO.**
