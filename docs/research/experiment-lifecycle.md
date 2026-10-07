# Experiment lifecycle

An EXP preserves the scientific trail from question to decision.

## OPEN

A question has been identified and is ready to be worked on, but research or implementation has not meaningfully started.

Minimum useful content:

- question;
- hypothesis;
- baseline;
- axes;
- initial refutation criterion.

## ACTIVE

Research, RAI, prototype work, or execution is underway.

Keep the README current enough that another contributor can understand what is actually being tested.

## RESULTS

Results are available and documented.

This does not imply that the result is positive.

Record:

- measurements;
- uncertainty;
- anomalies;
- failed runs that matter;
- limitations;
- reproduction information.

## CLOSED

The experiment is complete for now.

A closed EXP may be:

- integrated;
- rejected;
- inconclusive;
- superseded;
- converted into a new question.

Closing an EXP does not delete its evidence.

## Decision states

### reject

The tested path is not justified under the conditions studied.

### retry

The scientific question remains useful, but the protocol, metric, or prototype should change.

### integrate

The evidence supports updating the current reference behavior.

### candidate-I(n+1)

The result suggests an architectural rupture worth investigating beyond the current generation.

## Reference code

Do not copy permanent reference code into every EXP.

Record the commit and configuration used.

This lets future readers reconstruct what was tested while keeping the reference implementation in `src/`.

## Reproducibility target

An experiment record should allow a technically competent contributor to determine:

- exactly what code was used;
- exactly what configuration was used;
- how to rerun the experiment;
- where outputs are produced;
- which result supports the decision.
