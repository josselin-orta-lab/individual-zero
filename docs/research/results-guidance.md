# Writing experiment results

The Results section should describe what happened, not merely defend the original hypothesis.

## Include

When relevant, record:

- primary measurements;
- uncertainty;
- distribution across seeds or runs;
- anomalies;
- failed runs;
- observed side effects;
- resource costs;
- limitations;
- known confounds.

## Separate observation from interpretation

Prefer:

> Recall accuracy increased from X to Y under the tested condition.

Then:

> This is consistent with the hypothesis that...

Avoid collapsing both into:

> Replay improves memory.

The second statement may be broader than the experiment supports.

## Negative results

A negative result is not an empty result.

It can establish that:

- an expected effect did not appear;
- a proposed mechanism adds cost without measurable benefit;
- an implementation is not equivalent to a baseline;
- a metric is too noisy;
- an assumption was wrong.

## Inconclusive results

Use "inconclusive" when the experiment cannot distinguish the relevant alternatives.

State why.

Examples:

- confidence interval too wide;
- benchmark too weak;
- hidden confound;
- implementation bug discovered after execution;
- metric does not capture the intended effect.

## Avoid result laundering

Do not move a failed scientific claim into an architectural decision simply because the implementation is already convenient.

Reference changes should be justified by the evidence actually collected.

## Preserve context

A future reader should be able to understand:

- what claim the result supports;
- what claim it does not support;
- under which conditions the result was obtained.
