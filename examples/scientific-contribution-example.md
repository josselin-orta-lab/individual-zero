# Scientific contribution example: compare action veto policies

> Fictional example.

## Question

Does policy B reduce irreversible bad actions without reducing task completion relative to policy A?

## Why this is scientific

The change modifies action selection and may alter the individual's trajectory.

## Expected path

1. Open or join a research question.
2. Define baseline policy A.
3. Define measurable outcomes.
4. Perform a RAI scan.
5. Create an EXP.
6. Implement the minimal policy B variant.
7. Run both policies under identical scenarios and seeds.
8. Record results and limitations.
9. Decide: reject, retry, integrate, or broader architectural candidate.

## Placement

- cognitive policy: reviewed active-generation source (currently `src/i1/`) or a non-living isolated experiment; I0 stays frozen and I2 is not activated by implication;
- evidence: `experiments/`;
- reusable scenario: `benchmarks/` if broadly useful;
- software verification: `tests/`.

## ADR required?

Not initially.

An ADR becomes relevant only if the results lead to a shared structural decision, for example redefining the action-selection contract used across several modules.
