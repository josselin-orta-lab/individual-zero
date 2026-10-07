# EXP-EXAMPLE - Delayed recall with offline replay

> **Fictional example. This is not project evidence and must not be cited as a real result.**

- Axes: AXIS-MEMORY, AXIS-ARCH
- Target: I0
- Status: RESULTS
- Reference commit: example-only
- Owner / contributors: example

## 1. Question / hypothesis

### Question

Does replaying recent episodic traces during a short offline phase improve delayed recall compared with the same system without replay?

### Hypothesis

Replay will improve delayed recall accuracy on the example benchmark.

### Baseline

I0-example with replay disabled.

### Refutation criterion

The hypothesis is not supported if recall accuracy does not improve beyond the predefined uncertainty threshold.

## 2. RAI - Reuse / Adapt / Implement

A short scan finds:

- one external replay scheduler that is too tightly coupled to another framework;
- one generic queue implementation that can be reused as infrastructure;
- no suitable implementation of the exact replay policy being tested.

Decision:

**IMPLEMENT** the minimal replay policy while **REUSING** generic queue infrastructure.

## 3. Minimal implementation plan

Touch only:

- the experimental replay policy;
- the offline-phase hook;
- Lab instrumentation for replay count and trace identity.

Do not redesign the full memory architecture.

## 4. Test and reproduction command

Example conditions:

- 20 fixed seeds;
- identical training episodes;
- delayed recall after a fixed offline interval;
- baseline and replay variants share all parameters except replay.

Example command:

```text
python run_example.py --config config/example.yaml --seeds 1:20
```

This command is illustrative and does not currently exist.

## 5. Results and limitations

Illustrative result:

- baseline mean recall: 0.61
- replay mean recall: 0.67
- several seeds show no improvement
- replay increases execution time

Limitations:

- tiny synthetic benchmark;
- no long-horizon interference test;
- example numbers are invented for documentation purposes.

## 6. Decision

**retry**

Reason:

The example result is directionally interesting, but the benchmark is too weak to justify reference integration.

## Links

- Issue: example
- Pull request: example
- ADR: none
- Benchmark: example
