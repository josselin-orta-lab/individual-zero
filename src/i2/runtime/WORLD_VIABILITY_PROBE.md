# Locked I2 exploratory world viability probe, v1

**Scope:** one fixed **seven-case** deterministic engineering probe using the
existing single-owner I2 world runtime and its unchanged researcher-defined
valuation. It is neither a statistical sample of natural environments nor
a confirmatory G4/G5 experiment; it does not reproduce the closed G1-LAB
v1-r1 factorial.

Run once for inspection:

```bash
PYTHONPATH=src python -m i2.runtime.world_viability_probe --json
```

Cases are fixed in `LOCKED_CASES` before inspection: stable, adverse,
neutral, payoff reversal, no-food, no-UC and low-energy adverse. Each has
the same programmed physical laws in both arms, an independently initialized
identity and the same initial resources, UC, energy and physical horizon.
Output records exact case parameters; observed vs no-learning endpoint;
first decision divergence; observed terminal ticks and censoring; actual
UC use; and a descriptive **same-tick, both-alive** energy delta when valid.
It refuses to promote unequal/dead/censored endpoints to a general survival
claim. Negative and null cases are retained without tuning or exclusion.

A positive delta can only mean a model-specific outcome under scripted
physical laws and a researcher-written chosen-outcome heuristic. It does
**not** establish natural autonomy, learned physiology, robustness under
new environments, real-world longevity or authenticated M11. No I1 state,
active registry, motor actuator, original v1-r1 parameter-lock or heavy
scientific cohort is changed.

## Source-pinned readout and full-window energy accounting

The unchanged locked seven-case battery additionally records each pair's
**per-physical-tick, post-action energy difference** and its cumulative sum
over the entire observed window. This is a model-specific descriptive
*energy tick-integral*, not a biological fitness measure or causal survival
estimate. It is defined only when both individuals have the **same** observed
tick sequence and remain nonterminal through the horizon. Otherwise the
integral is `null` and no postmortem energy is imputed. Even where an
integral is reported, policies can produce different later physical states:
do not call it matched pre-choice or a natural-learning GO.

The I2 test suite emits exactly one `I2_LOCKED_VIABILITY_V1_RESULTS=` line
per CI Python environment using the cached result already computed by the
four locked-battery unit tests. It does **not** execute the battery again.
Archive the exact PR source SHA, the two CI conclusions, the seven output
rows (including negative and censored cases) and all limitations. Python
3.11 and 3.12 jobs on the same source are **software reproducibility checks**,
not statistically independent samples or separate confirmatory studies.
