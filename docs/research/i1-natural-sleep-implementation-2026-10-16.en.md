# I1: natural sleep and waking recovery (new-birth implementation)

Date: 2026-10-16. Status: implementation only; no newborn execution or scientific validation. Branch descended from experimental PR #241; no change to original I0, Lab or frozen A2.38/A2.39 cohorts.

## Mechanisms restored

Use `from i1lab.i1_natural_sleep import enable_natural_sleep_birth` **after** the isolated I1 fork has been generated. Before creating a fresh I1 autonomous mortal runtime:

```python
world_config, stage10_config = enable_natural_sleep_birth(
    world_config=world_config, stage10_config=stage10_config,
)
# Pass world_config and stage10_config as the usual birth arguments.
```

The existing Stage10 fatigue accumulator now rises with genuine waking UC consumption (`fatigue_gain=0.7`) and recovers during actually applied sleep (`sleep_fatigue_recovery=0.3`). Independently, real unconsolidated autobiographical episodes and memory occupancy create consolidation pressure (`consolidation_weight=0.25`, bounded). Night contributes a modest additional `0.20` to pressure. The fatigue weight is `0.65`, and Stage10 Competition's intrinsic weight is `0.9` (rather than the reference fixture's `4.0`). These are experimental configuration values, **not calibrated thresholds or guaranteed sleep frequency**.

An admitted physical sleep command gains `3.0` energy per step via the existing WorldBody rule, while the normal physical consumption of water and food continues. **Physical energy is not added to P-40 intrinsic sleep pressure**: Stage4 Value/Needs can separately motivate an energy recovery goal; the real body changes feed the existing lived TD reward and learning mechanisms. There is no rule forcing an energy-poor individual to sleep.

Actual consolidation uses Stage10's six-pass algorithm, incremental paid pending-episode index and bounded P-42 envelopes (640 UC per sleep step, 2560 per sleep period). Individual passes may defer when they exceed the remaining work budget; no synthetic memory evidence is created. Sleep duration is bounded at six steps, with reduced-perception wake alerts for critical food, water, energy, integrity and nearby dangers. Waking restores the ordinary Competition, Stage9 and Action Control paths. An alert merely wakes the individual: it does not choose a survival command.

Both physical and sleep config versions contain `i1-natural-sleep-fatigue-memory-night-energy-v1`. The frozen actual configs are included by the existing M11 birth contract. Applying the helper twice is refused. The original historical birth configurations are unchanged and are not silently retuned.

## Scope and scientific constraints

This change supplies normal configurable motivation and actual recovery, **not** evidence that an independently born I1 has spontaneously slept, consolidated, survived or improved its choices. No tests or new lives were executed under the earlier operator request to avoid additional testing. Calibration requires separate prospective physical populations. Review PR #239 when choosing eventual normative constants.
