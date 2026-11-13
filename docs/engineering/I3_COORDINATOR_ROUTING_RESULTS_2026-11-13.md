# I3 owner-selected research coordination: source-pinned software results (13 November 2026)

**Result:** `I3_REFERENCE_ROUTING_SOFTWARE_PASS`. This changes the **research agent's task selection guidance**, not the mind, genome, body, action policy, scientific admission or registered engine. It does **not** constitute a Stage-2 scientific advance or independent review. P1.3 funded-v2 remains I3's scientific reference, Stage 2.1 `NOT_ISSUED`; I3 is the **development reference**, while I1 remains the **active engine**.

## Evidence and integration

- Exact baseline main: `8c668baa3869cc5ac0ec7699cdffd319645c8d67`. The [methodological scope](I3_COORDINATOR_ROUTING_PREFLIGHT_2026-11-13.md) was frozen **before the source changes**, first commit `daa098ff42844be56478def69fefa6331f48ee91`.
- [PR #1361](https://github.com/josselin-orta-lab/individual-zero/pull/1361), exact tested head `eea54a0e0e4d8cc65b27acc52d222bc7a9ea9944`; merged by squash as `b87a030b641f2122c95e560d6e138c2221c16d39`.
- [Actions #43401527327](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43401527327): repository navigation and focused routing checks **PASS**.
- [Actions #43401527430](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43401527430): Python 3.11, exact source job `131805280154`: **1,303/1,303 I3 software tests PASS**, duration 179.069s. Python 3.12 job `131805280625`: **1,303/1,303 PASS**, duration 145.143s. Six new `test_research_coordinator_i3_routing.py` tests passed. Neither CI opened new scientific Worlds or executed the exhausted original cohort jobs. This report was written after those exact-source checks; it does not claim CI was run on this later documentation commit.
- Modified [global coordinator](../../tools/research_coordinator.py) and its [manual](RESEARCH_COORDINATOR.md), [I3 current navigation](../../src/i3/docs/README.md), plus six [focused tests](../../tests/i3/test_research_coordinator_i3_routing.py). Original I1/I2 curated `config/research-program.json` and its pinned sources, original studies, `ACTIVE_SURFACE.json`, registry, `Mind`, `World`, `BodyLaws`, genome, scientific policies and simulation runners remain untouched.

## Concrete prior drift and corrected behavior

**Before:** root `AGENTS.md` directs agents to `python tools/research_coordinator.py recommend` before selecting next work, yet the coordinator knew only I0/I1/I2 and favored the historical I2 `G3-CONTRACT` path by default, despite ADR-0020 selecting **I3** as the development reference.

**Now:**

1. `status` and `recommend` explicitly distinguish `active_generation=I1` from `development_reference_generation=I3`. I3 contract metadata is included without registering/executing it.
2. `recommend --generation I3` and the **default** `recommend` when I3 is selected show a **single non-executable, blocked C01 independent methods/futility review** for [I3 Stage-2 issue #1062](https://github.com/josselin-orta-lab/individual-zero/issues/1062). This is a routing **HOLD**, not authorization to implement another optional-cognition predictor, rerun E3 or open a scientific World.
3. The I3 route reads the **mutable live** `src/i3/ACTIVE_SURFACE.json` and contract only to check present permissions and status. The observed **Git blob SHA** is a byte-identity hint, **not a source pin**, independent provenance, preregistration, scientific verdict or third-party review. It accepts the established **specific** Stage 2.1 reference/hold with all scientific World and new-cohort permissions false; absent, malformed, inconsistent or newly permissive input returns `I3_SOURCE_REVIEW_REQUIRED` and **no suggested intervention** instead of silently falling back to I2.
4. Explicit `--generation I1` and `--generation I2` retain old **curated historical** recommendations. The new I3 route is deliberately **not** inserted into the I1/I2 research-claim graph and cannot mint `PIN_MATCH`, `GO`, an external methods signature, registration or a scientific experiment.

## Falsifiers and remaining gates

The focused tests verify I3 selected while I1 remains active, the proposed I3 non-executable contract, every forbidden permission flip, missing/malformed active surface, deterministic correct Git blob header, explicit CLI selection, manual independent-review requirement, no new I3 source/graph proof and no implicit I2 fallback. The full unchanged I3 software regression suite succeeded on two Python runtimes.

This solves a **research governance/routing defect** only. It does not solve the unresolved C01 *independent* methodological adjudication, missing prospective personal-information value -> native self-chosen paid calculation -> actual World action -> net post-paid-learning body chain, external ecological source/index/power, or independently deployed M11 witness. Until those are separately addressed, do not claim Stage-2 closure, evolved generalization or I3 production activation.

**Next cost-effective action:** secure a genuine, source-bound external C01 decision for Stage 2, including a valid scoped negative closure or justified HOLD; in parallel, test R2.4 on a truly protected independent remote M11 authority with attested signer and rollback-resilient storage. Do not replace these with another internal guard or a larger synthetic grid.
