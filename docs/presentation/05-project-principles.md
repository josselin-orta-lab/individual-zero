# Project principles

Individual Zero uses a few practical principles to keep the project understandable as it grows.

## 1. Build for inspection

A mechanism that cannot be observed is difficult to research.

Prefer designs that expose enough state, decisions, and timing information to understand what happened.

## 2. Ask before building

Implementation should usually answer a question.

Before adding a cognitive mechanism, ask what it is expected to change and how that change could be measured.

## 3. Reuse before reinvention

Search for credible existing work before implementing an expensive component.

Reuse or adapt when doing so preserves the scientific question and keeps the system observable.

## 4. Keep evidence separate from reference code

Reference behavior lives in `src/`.

Evidence about that behavior lives in `experiments/`.

This prevents old experimental copies from becoming accidental forks of the reference architecture.

## 5. Keep infrastructure neutral

The Lab should help run and observe many possible architectures.

If infrastructure begins deciding how cognition works, the boundary is probably wrong.

## 6. Let negative results survive

A failed hypothesis can save future contributors weeks of repetition.

If the result is reproducible and informative, keep it.

## 7. Architecture follows evidence

Do not use an ADR to make an experiment unnecessary.

Use experiments and explicit constraints first. Record the shared architectural decision afterward.

## 8. Prefer the smallest useful prototype

Research code does not become better merely because it is large.

Build enough to answer the question and no more than needed before evidence arrives.

## 9. Preserve replaceability

When reasonable, keep roles and implementations distinct.

A component that can be replaced is easier to compare, debug, and challenge.

## 10. Make the next contributor's job easier

A contribution is stronger when someone else can answer:

- what was changed;
- why;
- how it was tested;
- what was observed;
- what is still uncertain.

That is part of the research output.
