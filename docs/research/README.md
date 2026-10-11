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

### MVP v1.3.0 migration preparation (not executed)

- [Post-Stage-10/11 mortal-world and journal-removal audit](audits/post-stage10-11-mortal-mvp-audit.md): read-only dependency inventory, operator approval gates, lossless memory/consolidation requirements and staged migration plan. No final audit result is asserted while the agents are still developing.

### Stage 9 independent held-out evaluation

- [Complete independent evaluator and operator manual (English)](stage9-independent-heldout-evaluation-manual.en.md): step-by-step isolated setup, actual file schemas, sealed protocol, commands, expected machine results, evidence review and signed verdict.
- [Manuel complet d'évaluation indépendante (français)](stage9-independent-heldout-evaluation-manual.fr.md) : même procédure, avec commandes et modèles.
- [Stage 9 operator runbook](stage9-independent-heldout-operator-runbook.md) and [prelaunch NO-GO decision record](stage9-heldout-prelaunch-decision-record.md) remain the scientific governance references.

**Software integration is not scientific acceptance.** The manuals do not authorize the held-out campaign or freeze a Stage-9 Golden. Held-out seeds and oracle truth belong outside developer-accessible Git history.


### Stage 9 development behavior (not held-out)

- [Guide minimal d'observation locale (français)](stage9-behavioral-test-quickstart.fr.md): prérequis Arch Linux/Proxmox LXC, installation Python 3.12, lancement des 8 cellules, lecture des métriques et conservation des preuves sans GitHub Actions.
- [Local behavioral checkpoint (English)](stage9-development-behavior-2026-10-10.en.md) and [compte rendu français](stage9-development-behavior-2026-10-10.fr.md): user-reported Arch Linux/LXC terminal observations, cross-checked against an archived Stage-9 CI diagnostic; 163 unscored proposal emissions, 0 executed causal-test interventions. Raw user excerpts and the structured CI diagnostic are kept separately under `evidence/`.
- **Evidence classification:** existing development fixtures and a known implementation limitation, **not** an independently held-out result, an EXP acceptance, INV-25 certification or Stage-9 Golden. The independent scientific prelaunch decision remains NO-GO.

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
