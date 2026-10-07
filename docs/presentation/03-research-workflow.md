# Research workflow

Individual Zero is organized around a small pipeline that turns a question into evidence and, sometimes, a reference change.

## 1. Question / hypothesis

Start with:

> What are we trying to learn?

A useful question identifies:

- a hypothesis;
- a baseline;
- something observable;
- a criterion that could count against the hypothesis.

Example:

> Does replaying recent episodic traces during an offline consolidation phase improve delayed recall compared with the current baseline?

This is stronger than:

> Let's add replay.

The first asks something measurable. The second only proposes implementation.

## 2. RAI

Before significant implementation, ask whether the needed mechanism already exists.

**RAI = Reuse, Adapt, Implement**

- **REUSE** when an existing solution fits.
- **ADAPT** when it is useful but needs a thin integration or limited change.
- **IMPLEMENT** when no satisfactory solution exists or the mechanism itself is the research target.

RAI should save time, not become a literature-review swamp.

## 3. Minimal plan

Ask:

> What is the smallest prototype that can answer the question?

Define:

- interfaces touched;
- dependencies;
- instrumentation;
- baseline;
- scenario;
- metrics.

Do not build a complete subsystem if a narrow prototype can already falsify the idea.

## 4. Prototype

Build only what the EXP needs.

Experimental code does not automatically become reference I0 code.

It can remain local to the experiment until evidence supports integration.

## 5. Test conditions

Document:

- commit;
- configuration;
- data;
- seeds;
- metrics;
- environment;
- exact reproduction command.

A result that cannot be reproduced later is much less useful to the project.

## 6. Results

Record what happened, not what was hoped for.

Include:

- measurements;
- anomalies;
- uncertainty;
- failure cases;
- negative results;
- limitations.

## 7. Decision

Choose what happens next.

### Retry

The question is still useful, but the prototype, metric, or protocol needs revision.

### Reject

The tested approach is not supported under the tested conditions.

### Integrate

The evidence supports updating the current I0 reference.

### Candidate I(n+1)

The evidence suggests a broader architectural rupture that may require a new generation.

## When an ADR appears

An ADR is needed only when the result becomes a **shared architectural decision**.

Example:

One EXP locally uses a new memory cache.

No ADR is necessarily needed.

Several EXPs establish that all cognitive modules should use a new shared memory contract.

An ADR may now be appropriate.

## Feedback loops are normal

The pipeline is not a conveyor belt.

A test may reveal that:

- the question was too broad;
- the RAI choice was wrong;
- the metric was misleading;
- the prototype affected an unexpected subsystem.

Going backward is part of the method.

## Example path

```text
Question
  |
  v
RAI Scan
  |
  v
Minimal prototype
  |
  v
Experiment
  |
  +--> inconclusive --> revise protocol
  |
  +--> negative ------> reject / new hypothesis
  |
  +--> positive ------> integrate
                         |
                         +--> local change: I0
                         |
                         +--> structural rupture: candidate I1
```

See [experiments/README.md](../../experiments/README.md) for the experiment record format.
