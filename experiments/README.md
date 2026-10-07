# Experiments

An EXP groups everything needed to understand what was tested and reproduce the result.

Reference code remains in `src/`. An EXP points to the commit and modules it used rather than keeping a permanent copy of reference code.

Suggested structure:

```text
experiments/EXP-0047/
├── README.md
├── config/
├── run/
└── results/
```

Every experiment README should contain:

1. question / hypothesis;
2. RAI decision;
3. minimal implementation plan;
4. test and reproduction command;
5. results and limitations;
6. decision.

Possible decisions: `reject`, `retry`, `integrate`, `candidate-I(n+1)`.

Statuses: `OPEN`, `ACTIVE`, `RESULTS`, `CLOSED`.

Negative and inconclusive results should remain when they provide reproducible information.
