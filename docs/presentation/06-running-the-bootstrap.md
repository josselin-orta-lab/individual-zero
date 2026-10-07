# Running the bootstrap

The repository now contains a minimal executable path.

It is deliberately small:

**Smoke scenario -> Lab runtime -> Bootstrap I0 -> structured events -> JSONL artifact**

This proves that the execution, observability, configuration, and test boundaries work.

It does **not** yet claim to implement cognition.

## Requirements

- Python 3.11 or newer
- Git

No runtime Python dependency is required beyond the standard library.

## Install

From the repository root:

```bash
python -m pip install -e .
```

For isolated local development, using a virtual environment is recommended.

Example:

```bash
python -m venv .venv
```

Activate the environment using the command appropriate for your shell, then install the repository in editable mode.

## Run

```bash
individual-zero --cycles 3 --seed 0
```

Default artifact:

```text
artifacts/bootstrap-run.jsonl
```

Example summary:

```json
{"action_kinds": ["noop", "noop", "noop"], "cycles_completed": 3, "cycles_requested": 3, "run_id": "bootstrap-run", "seed": 0}
```

The no-op actions are intentional.

The bootstrap validates the action boundary without inventing an action-selection policy before that policy becomes a research question.

## Inspect the artifact

Each line is one structured JSON event.

The current sequence is:

1. `run_started`
2. `observation`
3. `step_completed`
4. repeated observation/step events
5. `run_completed`

This format is intentionally simple enough to inspect with ordinary text and JSON tools.

## Run tests

```bash
python -m unittest discover -s tests -v
```

The tests currently verify:

- deterministic output for identical inputs;
- reset behavior;
- event sequence;
- zero-cycle behavior;
- valid JSONL output;
- the deliberate bootstrap no-op policy.

## Change run parameters

```bash
individual-zero \
  --cycles 10 \
  --seed 42 \
  --run-id local-check \
  --output artifacts/local-check.jsonl
```

The seed is already part of the runtime contract even though the bootstrap I0 does not use randomness yet. Future stochastic mechanisms can therefore enter an execution environment that already knows how to record a seed.

## What comes next

The next scientific step is **not** to fill the bootstrap with arbitrary cognition.

Instead:

1. identify the first measurable question;
2. define the smallest cognitive role needed to test it;
3. perform RAI;
4. create the relevant EXP;
5. introduce the mechanism behind an explicit interface;
6. compare it against a baseline.

See [Bootstrap runtime boundary](../architecture/BOOTSTRAP_RUNTIME.md).
