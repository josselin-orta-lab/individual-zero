# Stage 1 cost-reduced development: post-hoc zero-information audit

**READ-ONLY AUDIT OF ORIGINALS. ZERO NEW LIVES. NO ENGINE REPLAY.**

This audit uses only the immutable originals from run `42359611338`, artifact
`13568698920`, ZIP SHA-256
`74fc93075a22254cf94490126b3e8853faa7a11745661af6da9e61f9c2786de3`,
also committed at
`5f244f33e540e1832a6442cd21f5028fae6bc8bb`.

It does not reconstruct unarchived branch values or conditional-choice arrays.
Where the originals do not support a distinction, this document leaves it open.

## What is directly observed

Across the 12 candidate lives:

- 8666 paid `local_expected_distress` option scores;
- **0** information increments above 1e-12;
- 8224/8666 (**94.90%**) scores with zero unsupported-history queries;
- 4255/8224 (**51.74%**) fully supported scores introduced at least two new
  exact payoff-cell keys into that decision's cache.

The last point means the all-zero information increment cannot be explained
solely by every supported score collapsing to one identical payoff cell.
It does **not** by itself distinguish two remaining kernel cases: observable
signals may still alias, or different observations may leave the same
continuation optimal. The archived observer intentionally did not retain
`branch_values` or `conditional_choices`, so claiming which case dominates
would exceed the evidence.

The kernel itself is not algebraically hard-coded to zero. Existing synthetic
software tests require a positive information value when observable outcomes
make different continuations optimal, and exactly zero when signals are
indistinguishable or the same continuation remains optimal. Those tests are
mechanism checks, not evidence about these lives.

## Sleep dominates funded local choice

There are 1389 candidate decisions with complete paid option scores.

- `dormir` has the highest raw local score on 1308/1389 (**94.17%**) of them.
- sleep is the final chosen option on 1241/1389 (**89.34%**) funded-score
  decisions;
- those 1241 sleeps are **69.25%** of all 1792 candidate lived steps.

This is not a passive funding failure. Most of these decisions complete the
paid comparison and actively choose sleep.

## The spatial boundary is visible in the originals

The implemented local prototype offers actions only from its current personal
location/map and carried inventory. Its hypothetical movement deliberately
reveals **no new map cell**. Therefore an unseen resource cannot contribute a
hidden discovery reward to a move.

That boundary is visible behaviorally:

### Stable + pulse

Across all eight stable/pulse candidate lives:

- 804 funded-score decisions;
- **0 scored `boire` options**;
- 0 positive water uptakes;
- 707 chosen sleeps and only 48 movement commands;
- sleep is raw-top on 760/804 (**94.53%**) decisions.

At personally sensed water <=20, there are 400 funded-score decisions in these
families. A drink option is available in **0/400**; sleep is chosen in 381/400
(**95.25%**) and raw-top in 390/400 (**97.50%**).

At water <=10, there are 200 such decisions: again 0 drink options; sleep is
chosen 184/200 (**92.00%**) and raw-top 193/200 (**96.50%**).

This does not prove that a particular spatial algorithm would survive. It does
show that the current local value calculation has no candidate water action to
prefer when the individual becomes critically thirsty away from a known local
source.

### Depletion

The four depletion candidate lives do score `boire` 195 times:

- 189/195 (**96.92%**) drink scores are fully empirically supported;
- drink's raw score is above sleep only 5/195 (**2.56%**) times and below sleep
  190/195 (**97.44%**) times;
- drink is raw-top among all options only 2/195 (**1.03%**) times;
- Competition ultimately chooses drink 12 times, matching the 12 positive water
  uptakes.

The raw drink-minus-sleep score margin has median about -0.02523 and mean about
-0.05932 on those 195 opportunities. These are descriptive score comparisons,
not a Competition defect claim: final Competition can and sometimes does admit
drink despite another raw local score.

## What this changes

The first Stage-1 diagnostic mainly exposed an unaffordable comparison loop.
The cost-reduced diagnostic shows that this is no longer a sufficient
explanation:

- stable/pulse die while their candidate decisions remain fully funded;
- the local policy overwhelmingly chooses sleep;
- water never becomes a local offered action in those families;
- even when the model is empirically supported, contingent information value
  remains zero throughout the panel.

The current prototype therefore reached the boundary already documented in its
design: it is a **local mechanism falsifier**, not a clean Stage-1 architecture
comparison. Its repertoire, memory partition and stationary ignorance prior all
differ from P1.3.

The next scientifically useful Stage-1 slice should reduce those confounds:
retain P1.3's existing first-person spatial repertoire and learned state, and
isolate the replacement of additive curiosity/relevance/prudence by the paid
information-value computation. This recommendation follows from the archived
evidence plus the current source boundary. It is not a claim that spatial
information has already been shown beneficial.

Do not rerun 44/45 or 46/47, do not force resource actions, and do not advance
to a Stage-2 budget heuristic merely to rescue the local candidate. Stage 2
should remain the separate question of **how much unique computation is worth
buying** once the Stage-1 mechanism is attached to an otherwise comparable
behavioral repertoire.
