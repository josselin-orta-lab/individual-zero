# I3 P5e: full paid choice competition witness (development-only)

Tracking [P5d #1054](https://github.com/josselin-orta-lab/individual-zero/issues/1054), following the [original-only eating analysis](P5D_POSTHOC_PAID_EATING.md). Experimental hypothesis: when food is carried and `manger` is already proposed and prepaid, the absence of a meal may be due to other options' higher scores, retained evidence accumulators, a threshold crossing, or final control rejection. **We do not yet know which mechanism dominates.** The 125 P5d carried-food steps without scored curiosity had 125 paid eating options but zero eating; 95 were best among *resource-only* scores, not all options.

This increment is **software-only instrumentation**, not an experiment. The next actual study needs an independently sealed development-only schedule before running more lives. It does not reopen P5d original worlds 32–37 or P5c validation worlds 96–119. P4 reserve remains closed.

## Scope and boundaries

The optional flag `run_life(observer_full_competition=True)` enables the existing paid P5c decision score diagnostic and returns a distinct external `observer_full_competition` sidecar. An observer reconstructs no score or plan. Only already funded scores from the actual `Mind.decide` loop, and already executed decisions from `Mind._compete` and `Mind._admit`, are copied. No `World` or hidden resource truth is admitted to the mind; no extra simulation, no second admission, no further RNG and no new metabolic or cognitive cost rate.

The witness labels each original observation as `POST_DECISION_PRE_PHYSICS`. It contains the entire paid candidate set across rest, resource, movement and exploration; base return, applied and discarded curiosity/risk addends, uncertainty and first paid forecast; its shuffled evaluation order; normalized competition evidence; previous accumulators, intention, thresholds, actual paid cycles and threshold/fallback selection mechanism; actual pre-control winner; the real controller's trial order and admission status; and finally the admitted action. The observer separately preserves the pre-decision body/inventory and original work counters. If no score could be paid, the competition is explicitly **NOT_EXECUTED**, with no fabricated winner.

All values are external receipts. In particular the `accumulators_before` and `accumulators_after_residual` are **copies of internal decision evidence**, not accessible cognitive inputs, and the new sidecar is not included in `trace_head` or `evidence_head`. The unobserved original hidden-world schedule, unchosen counterfactual outcomes, hypothetical action's costs, future consequences and causal impact remain **NOT_OBSERVED**.

## Parity and falsifiers

The software gate requires `PYTHONPATH=src python -m unittest discover -s tests/i3 -p 'test_*.py'` on Python 3.11 and 3.12 and `python scripts/check_engine_repository.py --json` plus `python scripts/check_engine_contracts.py --json`. Focused controls compare the exact same development genome, environment and life seed under ordinary and curiosity-discard scoring, observer off/on, plus combined P5d resource observation. They compare original life and evidence hashes, real cognitive/learning receipts, original actions, learned model and spatial-belief signatures and RNG-sensitive accumulator competition. Synthetic falsifiers reject duplicated/unfunded options, invented admitted choices and inconsistent score arithmetic. Preserve adverse/null data, postmortem work boundary and all paid phases.

**STOP** if any opt-in parity, exact-source check, generation boundary, or cost conservation fails. A full candidate score vector does not establish causal mediation: same-genome intervention lives diverge in physical history from step 1–2 in the original development study. Future science requires a separately frozen development diagnostic and ultimately independent genetics/ecologies with prospective validation indices >=120. No tweak to innate food/curiosity scoring, genetic selection or rescue policy is authorized by the existing observations.

I1 remains active; I3 is unregistered, not GO.
