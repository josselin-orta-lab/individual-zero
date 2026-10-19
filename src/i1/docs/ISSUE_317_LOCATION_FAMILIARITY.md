# Issue #317: separating spatial familiarity from learned usefulness

**Experimental architecture correction.** This is not a survival guarantee or a scientific GO.

## Evidence motivating the change

The untouched held-out matched cohort (seeds 3011, 3023, 3041, 3067, 3083, 3109, 3121, 3137) produced, on each of the previously pinned engines, 1,103 registered out-of-perception multi-hop proposals, none crossing Competition and none carrying relevant learned Stage8 value. Meanwhile, 238 physically certified memory actions accompany 261 reversals over 281 physical movements, many oscillating between only two known cells. The original WALs are immutable: [audit run #39200154369](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39200154369). These numbers establish an important failure mode, not the behavioural effectiveness of a prospective repair.

The Stage11 memory evaluator previously provided the same positive intrinsic motivation to return to a sighted place even if its location was physically visited already. More confident/frequent observation could make a familiar location more attractive purely due to recognition, independently of learning a beneficial consequence. This is an architectural conflation of *spatial information novelty* and *learned utility*.

## Correction and scope

Stage11 now consults only GeographicExploration's own recorded first-person physical visit ledger (constant-time `has_recorded_site(target.observed_position)`) while evaluating an already valid and funded memory option. If the individual has **personally visited that location**, informational novelty of that *location* is exactly zero. An as-yet-unvisited previously sighted location retains its existing confidence-weighted intrinsic interest unchanged. This is **generic across entities**. There is no innate relation between water and thirst, berry and hunger, or any object and an outcome.

Stage8's original, truly learned/simulated evidence passes through unchanged, even for revisited sites. The memories, their confidence, route proofs, TD updates, Competition thresholds, motor vetoes, physiological parameters, death and M11 state are untouched. This does **not** classify sites as beneficial or dangerous, nor prevent a learned positive value from overcoming zero spatial novelty.

The existing paid memory evaluation already has access to Exploration's owner; no extra world read, map oracle, phase-1 prediction, new UC charge, memory state, mutable cache or serialized field has been introduced. The Stage8 evaluation signal records whether its site interest was previously visited, enabling physically verifiable attribution.

## Falsification gates

- Generated current I1 unit test: identical result for water, berries, wood and unknown objects; *first* observed site retains previous intrinsic interest, a witnessed previous visit removes **only** location interest, learned extrinsic Stage8 value still contributes.
- CI, parity, M11 cold recovery, all four native preset worlds, corridor motor and authenticated WALs.
- Compare 1141/1142/2027/2028 development worlds first, without changing parameters based on held-out seeds 3011..3137.
- After the code is frozen, validate against **new independent** seeds. Count remotely unseen first hops and complete returns separately, physical swings and actual UC, consolidation, sleep, drinks, death, TD and actual entity interactions.
- If useful learned returns disappear, any vital need degrades or oscillations persist from apparently positive TD, audit temporal credit attribution rather than forcing coefficients or lowering the Competition threshold.

No merge or issue closure until scientific robustness is demonstrated; I0 and PR #316 remain untouched.
