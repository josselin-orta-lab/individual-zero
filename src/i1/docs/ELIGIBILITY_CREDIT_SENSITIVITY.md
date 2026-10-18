# Instrumental learning: prospective TD eligibility sensitivity

## Preregistered physical experiment (2026-10-18)

Follow-up to [#305](https://github.com/josselin-orta-lab/individual-zero/issues/305) and the complete 32-life NO-GO in `ONE_RESOURCE_32_RESULTS.md`. New cohort [GitHub Actions #39124968808](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39124968808), physical run SHA `26d98c47421d5047ceda37994b9faf61cb1a1aac`.

**Single isolated parameter:** prebirth `TDLearningConfig.lambda_e` in I1, values `0.0 / 0.8 / 0.95 / 1.0`. Both Stage11/Stage10 configurations receive the same newly versioned Stage9/Stage8 TD subtree. Runner records `effective_td_eligibility_lambda` and refuses mismatches with the declared arm. Canonical I1 uses 0.8 and is not edited. Physical reward, food/water consumption, action selector, safety checks, UC budget, learning updates and irreversibility remain unchanged.

**Factorial:** `learning-cell-one` with one locally reachable unknown berry, gain `0` vs `+10`, λ in the four arms, three matched seeds `411/412/413`. 24 independently born I1 individuals, horizon 300 each, same physical world within lambda contrasts, no scripted commands, all deaths in denominator. Cognitive fatigue/consolidation/night sleep pressure is zero **only in this laboratory** to isolate the mechanism; ordinary physiological fatigue and mortality remain. This new cohort must never be pooled as if it shared engine SHA and birth identity with the previous 32 lives.

### Falsifiable causal predictions

- If the collection penalty from immediate metabolism is the principal blocker, increased λ may permit the later real feeding reward to reinforce earlier `collecter`, increasing repeated collection/eating and mean food in the +10 arm.
- A higher λ might instead propagate irrelevant consequences to unrelated past actions. The zero-gain control is essential for observing over-attribution and harmful persistence.
- An effect on food survival must be attributed to actual postexperience Q reads and chosen actions, not simply to an earlier TD update receipt. Track first collection, first real ingestion, TD returns and learned `collecter` proposal evidence, then actual subsequent collection/ingestion, hunger, water and mortality.
- If high λ has no benefit, investigate temporal credit, option ranking, association of prerequisite/action pairs and ongoing passive-metabolism reward rather than inventing an eat-first rule.

### Decision gates

Technical PASS = eight independently complete arms (three born WAL per arm), exact source SHA, born parameter equal to declared value, all hash-chained WALs intact. Scientifically meaningful relative improvement = paired increase in postexperience useful collections and ingestion in +10 with no corresponding indiscriminate increase in the neutral 0 world; correct attribution to positive delayed reward. A 3-seed pilot cannot establish survival non-inferiority or general learning GO. Death remains terminal; no recovery or replay of an identity. **GO for the complete learning agenda requires further reversed two-resource replication and delayed-choice performance.**

Status: `IN_PROGRESS`; no positive causal result is claimed before completed archive audits. I0 and main unchanged.
