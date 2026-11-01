# ADR-0005 - Authorize one integrated non-living I2 G1-LAB prototype

**Status: ACCEPTED by project owner, 1 November 2026.**
**Scope: G1-LAB research sandbox only. G1-LIVE, G0, G3, M11 and G4-G6 remain unchanged.**

## Context and decision

After ADR-0004 stopped the open-ended G2 patch/test campaign, there were no
independent architecture or science verdicts on the proposed living I2 owner.
The owner explicitly authorized one **bounded integrated G1-LAB demonstrator**
so that the first closed-loop learning claim can be *falsified* before the
external witness and living trust boundary are accepted. This is not a
retroactive G1 approval or a withdrawal of the G2 stop rule.

G1-LAB may exercise the existing **inert SQLite v5 cognitive fixture**, one
lab-owned internal deterministic body, observation of prior consequences,
paid synthetic Competition and Action Control, and an independently
initialized no-learning ablation. Put the lab body and its per-cycle record
in the **same local SQLite connection and transaction** as the paid cognitive
cycle. Do not add a parallel persistent cognition, world or UC owner. At most
one **internally simulated** action is selected by the paid advice; no
experimenter-forced second action, no imported I1 source or state. A fresh
lab capture only sees the *previously committed* body and personally
experienced earlier results; never expose its next hidden environment regime.

## Explicitly allowed technical increment

- A research-only `src/i2/lab/integrated_loop.py` with a deterministic,
  disposable collect/eat/drink world and modelled energy, inventory,
  resources, terminal and no-action metabolism. The existing v5 cognition
  owner can invoke a **private in-transaction lab callback**, after its
  paid review and **before COMMIT**. Default cognition/test behaviour remains
  unchanged when the callback is absent.
- One SQLite file per synthetic individual; no external WorldBody executor,
  second state owner or living Scheduler. Both body effect and existing
  synthetic UC charges roll back together on an injected pre-COMMIT failure.
- Fixed no-learning versus chosen-outcome observational valuation through
  the current paid Competition. Priors and score offset from earlier G2
  are explicitly labelled **researcher-authored and post-hoc**, not claims
  of learned natural value. Actual costs, abstentions, vetoes, terminal
  trajectories and negative outcomes are retained, not optimized away.
- Five small scenarios: stable, adverse, neutral, role reversal, recovery.
  All are exploratory G1-LAB software evidence. Preserve the important
  negative control that the same collect/eat sequence arises with learning
  disabled. If end-to-end learning cannot be distinguished, report
  `NOT_ESTABLISHED` instead of changing the criterion.

## Unchanged hard boundary: G1-LIVE

1. **No I2 birth or activation.** Keep `src/i2/engine.json` proposal-only,
   without birth/runtime entrypoints, and leave the engine registry/I1
   untouched. A lab CLI is a deliberately invoked research experiment,
   NOT an engine runtime.
2. **No living motor rights.** The existing Action Control output must still
   say `motor_authority=NONE` and `REVIEWED_NOT_ADMITTED`; the lab's private
   deterministic computation is explicitly **not** real motor admission or
   an external physical effect.
3. **No M11 claim.** SQLite hashes, local replay, local terminal and any
   mock witness cannot authenticate an independently born identity, prove
   global monotonicity, prevent coordinated whole-domain rollback or permit
   postmortem recovery. Lab bodies are disposable and may be discarded.
4. **Independent gate unchanged.** Two distinct, attributable independent
   architecture/science G1-LIVE reviews on exact source (R1-R8/C0-C11),
   independently governed monotone witness/fencing, M11 and G0 custody
   remain prerequisites for `#664` living G3 implementation and any
   registration, motor authority or birth. G4/G5 confirmatory protocols
   require their separate reviews and preregistration.
5. **Stop rule:** only this one end-to-end G1-LAB vertical increment is
   authorized, not an open-ended family of score heuristics, synthetic
   owners or guard PRs. Fix reproducible defects and report failures,
   but do not tune priors against observed trajectories to get a PASS.

## Falsifiers and evidence boundaries

- **H2/H3 candidate only:** if a newly chosen action's consequence is used
  before its next capture, if an unchosen world outcome changes valuation,
  if a controller inserts an eat action, or if a vetoed option acts,
  reject the loop. If learning and fixed-prior arms behave identically,
  report the *null* result, not a learning GO.
- **Atomic local cut:** failure before COMMIT must leave paid synthetic UC,
  cognition journal, body/inventory and lab transition unchanged. A local
  `after_commit` lost-ack is **not** an authorization to reissue physical
  action; the disposable prototype must not be used to claim crash-safe
  living retry/recovery.
- **Terminal:** a modelled zero-energy endpoint blocks subsequent G1-LAB
  cycles, but is not independently attested irreversible physiological death.
- **Metrics:** source/PR SHA, actions and non-offers, advice/veto/abstention,
  result energy and resources, synthetic UC actually spent, learned-vs-fixed
  comparator, model terminal, all negative and null trajectories.

## Follow-up

This ADR supersedes ADR-0004's prohibition **only for this explicitly
approved, non-living integrated G1-LAB demonstration**. It does not change
ADR-0001/0002/0003, the scientific goal, or any independent living gate.
Report the demonstrator's falsifiable observations and residual uncertainty,
then prioritize the independent G1-LIVE review (#662) and the narrowly scoped
living implementation (#664) **after** that review is accepted.