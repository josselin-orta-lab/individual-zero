# I1 #305 / #304: targeted learned collect-Q Stage8 read, preregistered

Date: 2026-10-28. Base SHA: `e619fe1e10adff48007e012dc6afaac3c947835a`. **Research arm only, defined before birth.** This is a causal *local* follow-up to the bounded natural M11 Oasis B witness of merged PR #597. Do not change canonical I1 policy.

## Established context (discovery, not the prospective result)

On Oasis B identity `i1:304:heldout:oasis:b`, canonically born I1 spontaneously ate at step 11; the personally experienced `manger berry_a` reward was published by TD at step 12 (return +10.7), updating the `collecter berry_a` eligibility trace. Stage8 later read Q(collecter)=0.2814423 at step 12, where the option did not cross Competition, then Q(collecter)=1.6722636 at step 18, when it crossed Competition and was physically applied (inventory 0 -> 1). Neither the necessity of this Q read nor a second nutritional benefit has been established.

## Controlled comparison fixed prospectively

Two genuine independent M11 ledger births, **same preset Oasis, same identity b, same physics v4, same 18-step horizon**, different only by a strictly scoped *prebirth* test-process wrapper of `Stage8OptionEvaluator.evaluate`:

- **Canonical**: unmodified I1, all owned TD updates and genuine Q reads.
- **Targeted arm**: only when Stage8's normal evaluation is at **world step 18** and the *requested owner learning signature* is exactly `i1:affordance:collecter:target=berry_a`, the existing single owner Q read is performed once for audit, but Stage8 is passed a typed `unlearned` result. All other Stage8 Q reads, and all Planning Q reads, remain untouched. No broad Q masking, no cognitive charge relief, no option injection, no force, no artificial learning or map. The intervention is triggered by `t_monde` and the actual normal `learning_signature`, not by outcome, sign or winner; the exact signature is determined before birth.
- Stop each physical life at genuine death or 18 applied steps, never extend the witness retrospectively. Record independent ledger provenance, cold recovery constraints, and both commands, body, state Q and Competition before any divergence.

## Primary causal question

Does suppressing **only** the already-learned Stage8 read of Q(collecter) at step 18 change its paid Competition threshold crossing, Action Control admission or actual `collecter` physical application?

H0: no difference attributable to that targeted Stage8 read. H1: a first physically applied action difference, at step 18, under identical canonical pre-step body, current owner Q, GoalManager, Competition, P-40, fatigue, UC histories, inventory and options. Confirm the single masked read's actual signature and status and identical previous actions. If differences arise before the selective suppression, call `INVALID_PREINTERVENTION_DIVERGENCE`. If no learned read is exposed, call `NOT_EXPOSED`. If Q is read and the same action still crosses the threshold/applies, call `READ_NOT_NECESSARY_IN_THIS_WINDOW`, not « learning is ineffective ». If only ranking/crossing changes without a changed primitive, classify this separately, not physical L3.

A difference here would establish only **the local necessity of one Stage8 Q(collecter) read for the step-18 motor choice**, within this particular physiology and owner history. It would not isolate the causal contribution of the *meal's TD credit alone*, since TD traces and other experiences (especially sleep) can update this signature, and Planning independently reads Q. It would not prove durable reuse or nutritional benefit from the newly collected berry.

## Guardrails and gates

- Canonical code, TD weights and update rules, lambda, rewards, UC, P-40, Competition, world physics, Action Control, mortality and I0 unchanged.
- No assertion requiring a positive scientific outcome; only fail on signature scope, owner provenance, matched birth and preintervention state, costs, ledger integrity or observational schema breaches.
- Record explicit `L1_PASS`, `L2_OBSERVED/NOT_EXPOSED`, `L3_NOT_ESTABLISHED` or bounded `L3_SINGLE_TARGETED_Q_MOTOR_EFFECT`, plus `ADAPTIVE_BENEFIT_NOT_ESTABLISHED`.
- Reproduce Python 3.11/3.12 exact-head structural and natural SMOKE/FULL 4/4, inspect full M11 report, integrate under issue #348 only after verification.


## Protocol correction v2, locked before first applicable trial (2026-10-28)

**Pilot v1 declared invalid:** exact-head `c9b264b8766c83d64e904a2cb979226f7e33c87e`, run [40716885408](https://github.com/josselin-orta-lab/individual-zero/actions/runs/40716885408), failed the *required manipulation fidelity check*. In canonical I1, goal-linked food affordances are produced by `ExperimentalI1Stage12Runtime._consider_uncertain_affordance`: this method consults the genuine owner Q values to rank *naturally available* proposals and records the chosen one's personally learned value/evidence in a paid pending receipt. `I1PartialEvidenceAdapter.evaluate` then supplies that precomputed learned evidence to the real Stage8/Competition path, **without calling Stage11/Stage8's base evaluator for this affordance**. Patching `Stage8OptionEvaluator.evaluate` or `Stage11OptionEvaluator.evaluate` therefore never intercepted the targeted `collecter` evidence, despite positive owner Q in the journal. Prior `NOT_EXPOSED` was an intervention failure, not an empirical negative.

**Prospective research correction:** the fixed world, identity, horizon, signature and step do not change. In the research arm, after canonical physical perception, charged owner Q lookups and natural ranking of the available food candidates have executed **unchanged**, the ephemeral `I1PartialEvidenceAdapter.evaluate` receives a *temporary, research-only* view of its pending receipt in which only `learned_evidence`, `learned_value` and `learned_status` for the exact `i1:affordance:collecter:target=berry_a` proposal at `t_monde=18` are hidden. It calls the existing adapter **once**, delivering the unchanged earlier paid `prior_evidence` instead of the learned mixture. Restore the original adapter view immediately afterwards. No owner Q read is added, suppressed, re-routed or given free UC. In particular, Q continues to affect the prior natural **proposal ranking**, and remains visible to Planning and other proposals. This study isolates the **downstream Stage8/Competition evidence contribution** of the selected collect-Q value only; it does not isolate its upstream proposal-selection effects.

**Fidelity gates:** the canonical Stage8 receipt must actually contain the learned target signature at step 18. In the research arm, an authentic candidate with the same option/signature must be evaluated by `I1PartialEvidenceAdapter`, its genuine source pending receipt must have `learned_status=learned`, and the emitted M11 Stage8 evaluation must instead mark `unlearned` with no Q value. The logged prior evidence, candidate identity and number of options must not be altered. Verify exact applied-command prefix through step 17 and identical body, TD, Competition, GoalManager, P-40 and UC history before the intervention. A missing adapter call, wrong signature or unchanged learned Stage8 receipt **fails the technical manipulation check**, not H0.

**Science classification stays precommitted:** a changed ranking/threshold is reported separately from a changed admitted/action-applied primitive. Unchanged motor action under an authenticated mask means this **one downstream input** is not necessary *in the tested state*; it does not mean Q learned values, instrumental TD or proposer ranking are ineffective. Regardless of outcome, no meal-specific eligibility-credit causality, second nutrition benefit, statistical robustness or global GO is claimed. Both Python versions test the same deterministic birth, not independent populations. No I0 or I1 production file changes.
