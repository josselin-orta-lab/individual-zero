# Stage 9: independent held-out pre-launch decision record

**Status: TEMPLATE / NO-GO / NOT APPROVED.** This document contains no independent appointment, witnessed data, scientific sign-off, executable authorization, successful held-out result, INV-25 acceptance or Stage-9 Golden. It must never be filled with invented people, retrospective dates or development-agent approvals.

The normative source remains `docs/architecture/reference/en/mvp-specification-v1.2.1.md`, especially §§9.6, 13.2, 19.5, 20.3 (Stage 9) and INV-25. The [scientific preregistration template](stage9-scientific-preregistration-template.md) defines the existing machine protocol; the [operator runbook](stage9-independent-heldout-operator-runbook.md) gives the execution and review sequence. This decision record adds procedural accountability, **not new normative acceptance thresholds**.

## Known development checkpoint, not a scientific freeze

- Last inspected development candidate: `74bf90414d8fae3bffd782fbfa97a1a82711c156` (2026-10-10); it is **not** an approved freeze. Replace this reference with the **actual full 40-character implementation commit** selected by the owner and evaluator, after any further software change.
- PR #18 is a **draft**, not merged. No Stage-9 Golden exists.
- The last recorded narrow CI at that candidate passed 638 unit tests and CLI smoke on Python 3.12; a new exhaustive Python 3.11/3.12 run and archived reference checks have **not** been claimed for this handoff.
- Current independent review, prospectively sealed worlds/seeds, original physical witness and protocol approval: **NOT VERIFIED**.

## A. Named responsible people and incompatible access

Fill each field with the actual accountable person, their organization/contact reference, their acceptance date and signed evidence location. Store confidential contact details in access-controlled custody, not public Markdown. **UNSET is not an appointment.**

| Responsibility | Named individual | Accepted scope and date | Evidence / conflicts |
| --- | --- | --- | --- |
| Research/protocol owner | UNSET | UNSET | UNSET |
| Independent world **and seed** custodian | UNSET | UNSET | UNSET |
| Frozen-run execution operator | UNSET | UNSET | UNSET |
| Independent scientific evaluator / INV-25 reviewer | UNSET | UNSET | UNSET |

The development agent is **not** the independent evaluator. Document each affiliation, prior exposure to development results and potential conflicting role. A role combination requires independent justification and compensating oversight. In particular, no single unchecked actor may choose the hidden cases, tune the executable after seeing results, and approve the interpretation.

**Conflicts reviewed by (independent person):** UNSET  
**Review date / signed record reference:** UNSET  
**Role separation outcome:** NOT VERIFIED

## B. Hidden-world and seed custody, before any reveal

The current `stage9-preregistration-schema-v2` requires an explicit `holdout_seeds` numeric array. **Those seed numbers are plaintext**, not encrypted or committed secrets. Therefore, merely committing the complete preregistration to a Git branch visible to developers would expose them; a SHA-256 of a short predictable seed list is also vulnerable to guessing. An ordinary private repository is not independent custody when the developers have read access.

The independent custodian must prepare the real registration and its descendant Git history in an **isolated, access-controlled clone/fork or offline repository**, rooted in the selected frozen implementation. Do not push that branch or registration JSON to this development PR, developer-readable forks, Issues, chat logs or GitHub Actions before the outcome-exposure boundary. A non-sensitive custody receipt may be shared without disclosing seeds, world files, oracle truth or low-entropy commitments. Preserve an independently witnessed timestamp and signer, because Git commit author/committer dates and ancestry alone cannot establish real-world chronology.

| Protected object / condition | Custodian's verifiable receipt, not secret values | Status |
| --- | --- | --- |
| Original calibration world/layout/scenario manifests | UNSET | NON VÉRIFIÉ |
| Distinct original held-out world/layout/scenario manifests | UNSET | NON VÉRIFIÉ |
| Disjoint calibration and held-out seeds; secret selection record | UNSET | NON VÉRIFIÉ |
| Frozen world generator / Equipment / parameter / ontology bytes | UNSET | NON VÉRIFIÉ |
| Bench-only oracle access separated from individual/developers | UNSET | NON VÉRIFIÉ |
| Access roster, storage location and custodian signed receipt | UNSET | NON VÉRIFIÉ |
| Independent, prospectively dated seal of the complete registration | UNSET | NON VÉRIFIÉ |

No benchmark result, seed number, hidden positive/null label, candidate observation or true oracle answer is permitted in this document. The recorded receipt should use a high-entropy private commitment or independently signed sealed metadata when needed, not publish guessable hashes as a substitute for secrecy. This register cannot itself prove custody.

## C. Prospective protocol and experimental release

| Evidence or approval | Immutable ID / custodian-controlled location | Status |
| --- | --- | --- |
| Selected complete implementation commit and frozen `src/` / `pyproject.toml` / English specification | UNSET | À APPROUVER |
| Frozen equipment, parameters, ontology, world-generator versions | UNSET | À APPROUVER |
| `stage9-preregistration-schema-v2` JSON with every required field | UNSET | À APPROUVER |
| Protocol digest and **registration** commit after implementation freeze | UNSET | À APPROUVER |
| Preregistered positive/null controls, metrics, denominators, confidence, counts, exclusions, stopping and INV-25 comparisons | UNSET | À APPROUVER |
| Research owner approval, signed and independently dated **before any result** | UNSET | BLOQUÉ |
| Custodian attests seed/world isolation and no earlier exposure | UNSET | BLOQUÉ |
| Named operator accepts runbook, raw/replay archive, failed-run retention and source preflight | UNSET | BLOQUÉ |
| Named evaluator accepts blinded review and independence disclosures | UNSET | BLOQUÉ |
| Actual frozen checkout byte-preflight receipt in execution environment | UNSET | NON VÉRIFIÉ |
| Critical full software CI (both configured Python versions and exact reference replay), where required before release | UNSET | NON VÉRIFIÉ |
| **Explicit, prospective signed release-to-run / GO** from the authorized owner and independent oversight | UNSET | BLOQUÉ |

The selected code commit must be reevaluated if `src/` or the environment changes after freeze. A protocol revision requires a new dated approval **before result exposure**, with the earlier version preserved. An approval entered later is not retrospective proof of prospectivity.

The held-out procedure is **not** authorized by a machine-readable JSON draft, a successful validation command, Git chronology alone, a normal PR approval, a passing CI job or the creation of this document.

## D. Gate decision

**Decision: NO-GO (default, pending independent evidence and signatures).**  
**Decision maker / independent countersignature:** UNSET / UNSET  
**Date/time and independent timestamp evidence:** UNSET  
**Protocol digest / registration commit:** UNSET / UNSET  
**Frozen implementation commit:** UNSET  
**First permitted exposure / execution conditions:** UNSET  
**Disqualifying issues / exceptions:** UNSET

Only a real prospective, attributable and independently witnessed approval can release the operator. No GitHub workflow, shell script or AI development agent may turn this template into GO by inferring identities, filling fictitious signatures or manufacturing an independent hold-out set.

## E. Permitted work while NO-GO

Continue development-only unit tests, static checks, mock-world adversarial custody tests, code review, preregistration-format drafts **without withheld secrets**, documentation and control rehearsal on publicly designated development worlds. Keep PR #18 draft and unmerged; retain candidate commits and unfavorable test results.

**Forbidden until authorized:** opening the sealed world/seed material in the development environment, running a held-out evaluation, adjusting thresholds after results, creating a scientific Golden, publishing bench-only oracle truth or declaring Stage 9 scientifically closed.

For any later external execution, preserve original journals and closed Memory/causal states, replay separately, obtain independent physical/oracle witnesses and run the full read-only custody/chronology/handoff tools. Their output is a **machine receipt only**, never an independent verdict. The independent reviewer must record **PASS, FAIL or INCONCLUSIVE** with the full failures and counterexamples, including INV-25 paired safety-only versus `etablie` differential tests.
