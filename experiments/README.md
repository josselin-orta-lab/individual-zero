# Experiments

An EXP groups everything needed to understand **what was tested, under which conditions, what happened, and what decision followed**.

An EXP is scientific evidence, not a development ticket.

## When to create one

Create or join an EXP when work is intended to:

- test a scientific hypothesis;
- compare cognitive mechanisms;
- evaluate a behavior-changing reference parameter;
- replace a reference cognitive component;
- alter the global cognitive cycle or structural relationships;
- produce evidence needed for an architectural decision.

Do not create an EXP for ordinary documentation, CI, behavior-preserving refactoring, clear bug fixes, or routine software verification.

## Suggested structure

```text
experiments/EXP-0047/
├── README.md
├── config/
├── run/
└── results/
```

### `README.md`

The scientific record.

It should contain:

1. question / hypothesis;
2. RAI decision;
3. minimal implementation plan;
4. test conditions and reproduction command;
5. results and limitations;
6. decision.

### `config/`

Configuration required to reproduce the experiment.

### `run/`

Experiment-specific launch scripts or commands when necessary.

### `results/`

Useful measurements, summaries, or artifacts needed to preserve the evidence.

Avoid committing enormous disposable outputs when a compact reproducible summary is enough.

## Reference code

Reference code remains in `src/`.

An EXP points to the exact commit and modules it used rather than keeping a permanent copy of source code.

## Status

- **OPEN**: question identified, work not meaningfully started.
- **ACTIVE**: research, prototype, or execution in progress.
- **RESULTS**: results are available and documented.
- **CLOSED**: work complete for now, whether integrated, rejected, inconclusive, or superseded.

## Decisions

- `reject`
- `retry`
- `integrate`
- `candidate-I(n+1)`

Negative and inconclusive results should remain when they provide reproducible information.

## Naming

Use sequential IDs such as:

```text
EXP-0001
EXP-0002
EXP-0003
```

Do not encode the research axis into the number. One EXP may span several axes.

## Start here

Use [TEMPLATE.md](TEMPLATE.md) for a real experiment.

For a fully filled fictional example, see [../examples/example-exp/README.md](../examples/example-exp/README.md).
