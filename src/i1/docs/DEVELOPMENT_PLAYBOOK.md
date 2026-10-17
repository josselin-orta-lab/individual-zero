# I1 development playbook

A change is acceptable only if it preserves autonomous, UC-priced, mortal and first-person cognition. Never write a target behavior and retroactively call it emergent.

## Before editing

1. Fetch current `main`, PR #251 → #252 → #253 → #254 dependencies, target HEAD and GitHub CI. Identify the active engine via `config/engine-registry.json`.
2. Read [THEORY.md](THEORY.md), [COGNITIVE_FLOW.md](COGNITIVE_FLOW.md), [EVIDENCE_MATRIX.md](EVIDENCE_MATRIX.md) and affected source. Separate intended mechanism from an unproven theory.
3. Write a falsifiable statement: observation → candidate mechanism → possible alternative explanations → negative test that can distinguish them.
4. Record the boundaries: physical state, subjective projection, technical journal, causal owners, UC, persistence and terminal state.

## Investigation and implementation

5. Capture the issue in a seeded living scenario when possible (see [WORLD_PRESETS.md](WORLD_PRESETS.md)). Preserve the individual's uncertainty, its own choices, and the fact of death. The observer is external and cannot feed back privileged data.
6. Track the full decision chain: bodily level → local perception → needs → goal → proposed plan → admission/competition → admitted command → physical change → experienced event → learning/consolidation.
7. Patch the *lowest real cause*, never force `manger`, `boire`, `dormir`, travel or a historically expected H1/H2 action. Avoid hidden danger or prebirth knowledge.
8. Test positive, negative and uncertainty cases. A plausible death is not automatically a failure; a hidden-knowledge leak, free UC or resurrected step is.
9. For M11: verify refusal on pending intent, identity mismatch, corrupt roster, bad publication and terminal state. No living rollback is available.
10. For Stage10: demonstrate nonempty actually published owner-specific forms when claiming consolidation improvements; verify provenance, UC and stable cold state separately.

## Proof and handoff

11. Run `python scripts/check_engine_repository.py --json`, `python scripts/check_engine_contracts.py --json`, I1 structural tests, smoke/full, owner and M11 suites, and artifact parity where affected. Check Python 3.11/3.12 on the exact pushed commit.
12. Attach world/seed, SHA, new evidence and limitations. Update [EVIDENCE_MATRIX.md](EVIDENCE_MATRIX.md) *only for evidence actually measured*, [STATUS.md](STATUS.md) for outstanding risks, and the code/doc references where mechanics changed.
13. Report clearly: code modified; tests passed/failed/not observed; observed live behavior; scientific gate; remaining unknowns. Do not merge dependent PRs out of order.

## Worked diagnostic: berries collected but not eaten

**Do not** append a food-first action. Inspect whether collection changed inventory but not physiological food, whether inventory is perceptible, whether need pressure reached the Goal Manager, whether `manger` was a permissible candidate and whether competition or gatekeeper excluded it. Verify actual command and `ate` outcome separately, then that a lived effect updates the appropriate memories or models without an oracle. Reproduce with `oasis` or `foraging` and vary only predeclared physical conditions.

## Stop conditions

Stop and report a blocker for missing ground truth provenance, hidden observation injection, compromised mortality, noncanonical M11 commit, incorrect owner publication, unaccounted UC or test omission. Do not mask those failures with replaying a life, relaxing tests or calling an inconclusive trace a scientific success.
