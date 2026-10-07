# Bootstrap run example

> Illustrative technical example. Not scientific evidence.

After installation:

```bash
individual-zero --cycles 2 --seed 7 --run-id example
```

A run summary has the form:

```json
{"action_kinds": ["noop", "noop"], "cycles_completed": 2, "cycles_requested": 2, "run_id": "example", "seed": 7}
```

The JSONL artifact contains events similar to:

```json
{"cycle": null, "data": {"cycles_requested": 2, "scenario": "bootstrap-smoke", "seed": 7}, "kind": "run_started", "run_id": "example"}
{"cycle": 0, "data": {"observation_data": {"scenario": "bootstrap-smoke", "value": 0}, "observation_kind": "tick"}, "kind": "observation", "run_id": "example"}
{"cycle": 0, "data": {"action_data": {"reason": "bootstrap-runtime-only"}, "action_kind": "noop", "state": {"cycles_completed": 1, "last_observation_kind": "tick", "observations_seen": 1, "seed": 7}}, "kind": "step_completed", "run_id": "example"}
```

The exact record format is intentionally human-readable during the bootstrap phase.

This example demonstrates execution and observability only. It does not demonstrate cognition or support a scientific conclusion.
