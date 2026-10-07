# Research documentation

This directory contains research methods and explanatory documents broader than a single experiment.

Evidence for a specific experiment belongs in `../../experiments/EXP-####/`.

The current scientific map belongs in `../../RESEARCH_MAP.md`.

## Core principle

Keep four distinctions explicit:

1. **hypothesis vs observation**;
2. **software verification vs scientific evidence**;
3. **reference behavior vs experimental variant**;
4. **project-developed mechanism vs reused or adapted external component**.

These distinctions are what make a result understandable after the original contributor has moved on.

## Research documents

- [RAI](rai.md): how to decide whether to reuse, adapt, or implement.
- [Experiments vs tests](experiments-vs-tests.md): when a software test is enough and when an EXP is required.
- [Experiment lifecycle](experiment-lifecycle.md): how a question becomes evidence and possibly reference behavior.
- [Glossary](glossary.md): project terminology used across Issues, EXPs, ADRs, and code.

## Minimal scientific question

A useful research question should make it possible to state:

- what we are trying to learn;
- the current hypothesis;
- the baseline;
- what can be measured;
- what observation would count against the hypothesis.

If those elements cannot yet be stated, the topic may still belong in a Discussion rather than an EXP.

## Avoid premature formalism

Do not create an EXP simply because a topic sounds scientific.

The experiment structure exists to preserve evidence, not to decorate an idea with an experiment number.

Likewise, do not create an ADR before the project has evidence or explicit constraints that require a shared architectural decision.
