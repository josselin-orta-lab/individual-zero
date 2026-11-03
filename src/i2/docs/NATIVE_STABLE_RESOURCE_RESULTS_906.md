# Stable-world I2, 24-tick observed result and tie diagnosis

**Retrospective exploratory result, 3 November 2026.** Frozen protocol
in [NATIVE_STABLE_RESOURCE_CHOICE_COHORT_906.md](NATIVE_STABLE_RESOURCE_CHOICE_COHORT_906.md)
and issue #906. Exact source merged PR [#916](https://github.com/josselin-orta-lab/individual-zero/pull/916),
head `3b765780deced2b77dcffccd589b194798464baa`.
[Run 41639338144](https://github.com/josselin-orta-lab/individual-zero/actions/runs/41639338144):
Python 3.11/3.12 PASS, each 714 I2 tests; four distinct local
SQLite-born individuals, each 24 paid ticks, successful cold audit,
no biological death. All are technically horizon-censored.

| Born stable world | Learning | Ineffective old drinks | Old drinks total | Collect | Discovered drink | NO_ACTION | Final water | UC spent |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Always ineffective, gain 0 | OFF | 8 | 8 | 1 | 1 | 0 | 35.4 | 114 |
| Always ineffective, gain 0 | ON | 3 | 3 | 0 | 0 | **21** | **25.4** | 123 |
| Always useful, gain 10 | OFF | 0 | 3 | 1 | 0 | 20 | 55.4 | 124 |
| Always useful, gain 10 | ON | 0 | 8 | 1 | 0 | 0 | 93.6 | 128 |

**Positive but narrow:** experience-dependent scoring leads to fewer
genuinely ineffective old-source drinks (3 versus 8) and changes the
motor outcome. The first difference occurs at tick 3 in both worlds,
after the same two actions, physical body and subjective observations.
**Negative integrated behavior:** with ineffective old water the learned
arm *does not* choose the physically available collect option, makes
21 abstentions and ends with less water than innate-only (25.4 versus
35.4). Innate-only finds a useful second source at tick 9 and
drinks it at tick 10; learned never discovers it.

At the first learned/innate divergence in the useless-water world,
the OFF scores are `boire=5, collecter=3, dormir=2, attendre=1`;
learning ON obtains `boire=3, collecter=3, dormir=2, attendre=1`.
Thus there are **two equally highest positive candidates**.
`CompetitionPreview.review` classifies the tie as `AMBIGUOUS`,
returns no suggested candidate, and the existing SQLite owner
commits `NO_ACTION`. The learning arm has not inferred that the
untried source is useful or chosen exploration. This is a
decision-interface interaction, not proof of natural exploratory
learning, superior survival, or a problem of an invisible environmental
quality reversal. In the favorable world, the learning ON arm uses
the useful source more often and ends more hydrated; this also
does not prove generalized adaptive competence.

**Next minimal falsifier:** preserve the third-step positive-score tie
with identical predecision physical evidence as a targeted regression;
then research how a low-abstraction individual should resolve or
tolerate *competing positive equally scored actions* under genuine
physiological need. Do not simply hardcode `collecter` as winner or
force a physical exploration. A legitimate tie-resolution hypothesis
must remain subject to paid competition and current-body reflex,
never consult hidden world quality, and compare harm, abstention,
cost and survival across both stable worlds. Do not rewrite this
frozen cohort or adjust its parameters to get a better outcome.

Scientific status: autonomous integrated ecological learning and
independent M11 remain **NOT_ESTABLISHED**; prototype proposal-only.
