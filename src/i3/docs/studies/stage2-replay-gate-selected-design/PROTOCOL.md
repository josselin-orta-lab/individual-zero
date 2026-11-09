# Stage 2.1 selected-population gate: prospective design candidate

**DRAFT FOR OWNER REVIEW, SOFTWARE ONLY. NOT PREREGISTERED, NOT AUTHORIZED FOR WORLD EXPOSURE.** Base `main` at `1921badf32e5ecafa08980011bf197dfb3d6ade0`. Context: [Stage 2 replay gate](../../STAGE2_REPLAY_GATE.md), [original first-exposure results](../stage2-replay-gate-development-80-81/RESULTS.md), [frozen control parameter](../stage2-replay-gate-development-80-81/RANDOM_EQUAL_MEAN_PARAMETER.md). I3 remains unregistered; P1.3 funded-v2 remains reference. Stage 1 is closed negative. DEVELOPMENT 80/81 is closed without retry, with no survival non-inferiority shown. No further scientific World is authorized.

## Question

Can the individual's own D-priced selection of sleep replays reduce physical cognitive energy/vigilance per lived step **without an unacceptable survival or inactivity cost**? Does choosing memories based on personal relevance outperform simply reducing replay *amount*, given genuinely equal cognitive overhead?

## RANDOM-EQUAL-MEAN, prospective proposed implementation

- Parameter obtained from **DEVELOPMENT only**, exactly **5532 paid GATE replays / 867 GATE sleep steps = 1844/289**. Never re-estimate from selection/validation or from closed 68/69.
- For each *reached and actually executed sleep step*, independently draw scheduled budget 6 with probability **179/289**, or 7 with probability **110/289**. The nominal expected budget equals 1844/289. Draw once at zero-based *executed sleep ordinal*, not world timestep.
- `i3.lab.stage2_random_equal_mean.scheduled_replays(life_seed, sleep_ordinal)` uses a domain-separated SHA-256 counter-derived stream independent of P1.3, world and global RNG; rejects modulus bias. It has **no World, Mind, hidden stock, future event, score or motor access**. Identical life seeds induce common randomness across matched interventions, not new independent replicates.
- The **future separately authorized runtime** must replay the existing top-priority P1.3 memories in descending |TD error|, attempting **at most min(K, eligible, P1.3 maximum)**. Each actual replay and all metareasoning must be physically prepaid. An ineligible, unfunded or postmortem opportunity is not re-drawn, made up or settled later. The actual replay mean can fall below 1844/289.
- The RANDOM arm must **perform and prepay** GATE's genuine one-cycle residual audit and the same two sleep forecast simulations and gate cycle, while ignoring the computed gain for its random count budget. This is actual overhead, not fictitious debiting. A failed audit/gate funding attempt must fail closed. Zero-perceived-cost still pays all computations, setting only perceived `c=0`. Changing physical tariffs is forbidden.
- These helper functions **do not implement runtime, payment, replay selection, action control or admission**. Exact transport, funding parity, no postmortem effects, seed independence, renaming invariance and identical reference behavior still require focused prospective integration tests **before** any live panel.

## Selected multi-population design candidate (F0 only)

Reuse the unopened Stage-0 F0 identifier plan from [STAGE0_DESIGN.md](../../STAGE0_DESIGN.md): **8 distinct G0 founder pools**, **40 unique founders per population**, **5 selected per architecture per population**. Selection independently ranks complete FIXED and GATE original receipts by horizon-censored count, total lived steps and ascending seed. Do not select favorable lives only; do not change genome birth semantics or inherit memory.

| Phase | Existing P2 indices | Planning ceiling | Scope |
| --- | --- | ---: | --- |
| Selection | `selection` **72–119** | **3,840** lives | 8 × 40 × 6 worlds × 2 architectures |
| Validation | `validation` **120–167** | **1,200** lives | 8 × 5 selected × 6 worlds × 5 conditions |
| Reserve | 1200000–1200199 | **0** lives | Sealed, no access |

Total planning ceiling **5,040 lives or 2,016,000 horizon steps**, NOT execution funding. In each population use two independently seeded worlds per existing P2 family, stable/depletion/pulse, in each phase; no new ecological transfer is established. All indices require fresh collision search and explicit owner authorization before opening. All originality/selection and genotype identity must be source-locked, not inferred from a summary.

**Validation conditions:** `FIXED_on_FIXED_selected`, `GATE_on_GATE_selected` (primary architecture-under-selection contrast), `FIXED_on_GATE_selected` (same-genome reference), `RANDOM_on_GATE_selected`, `ZERO_PERCEIVED_COST_on_GATE_selected`. The same five GATE-selected genomes in conditions 2–5 let the observer separate genetics, quantity of replay and gate sensitivity. Never mistake matched lives for eight times more independent populations. Each population has 30 assigned lives per condition. World slots and seeds remain paired across conditions.

## Primary endpoints and falsifier, all **proposed margins for owner review**

Four co-primary population-level endpoints, with delta = selected GATE minus selected FIXED per population, and all required to pass the **one-sided exact directional sign tests** at alpha 0.05:

| Endpoint | Favorable sign on each independent population |
| --- | --- |
| Physically paid cognitive energy per actually lived step | delta **< 0** |
| Physically paid cognitive vigilance per actually lived step | delta **< 0** |
| Survival proportion at 400 steps | delta **> -0.05** (proposed 5 percentage-point margin) |
| Inactive fraction of actually lived steps | delta **< +0.05** (proposed 5 percentage-point margin) |

Use one complete predeclared population aggregate for each endpoint, eight populations total, and the exact one-sided tail `sum(C(n,j), j=wins..n)/2**n` with exact ties excluded and effective n reported. **7/8 favorable signs gives p=9/256=0.03515625**, 6/8 fails. All four criteria jointly form an intersection-union composite at 0.05; no separate confirmatory claim for an endpoint or secondary control without a multiplicity plan. This exact sign test concerns **directional median-population performance, not mean non-inferiority** and does not guarantee performance in a new family. The 5% bounds, units, strict inequalities, power and actual sample ceiling are **proposals**, not a settled scientific authorization. Eight populations may be underpowered for non-inferiority.

Report total cognitive expenditure per assigned life, time alive, actual per-phase charges, deaths, family heterogeneity, full original life traces, inactive-step fraction and exact survival counts. A zero-lived-step denominator or missing population/original returns `NO_VERDICT`, never zero cost, an excluded death or a fabricated surrogate. Fixed-at-horizon censoring differs from death on step 400. Full two-phase G/R custody, no retries, sealed originals, blind reduction repairs and every adverse/null outcome apply. The earlier software R3 was non-discriminating: do not post-hoc redesign its fixtures.

Controls (GATE vs RANDOM; GATE vs ZERO-PERCEIVED-COST; GATE vs FIXED on GATE-selected genomes) are **secondary descriptive** unless separately allocated alpha before World opening. Any cost saving with earlier deaths must be reported as such. No change to the replay-gate equation, P1.3 reference, body laws, Competition, perception, Stage 1 or reserve.

## Explicit blockers before a new scientific exposure

1. Independent review of the candidate sampling design, inferential estimand, primary margins, uncertainty and **power**; freeze before first selection World.
2. New source-locked implementation of RANDOM and equal actual audit/gate charges, with no observer-to-Mind leakage; full focused funded-cognition and motor-parity tests.
3. Repair the **operational admission gap**: the existing owner-lift fingerprint guard does not track the exhausted 80/81 authorization. New scientific index/cohort admissions must be fail-closed and consume explicit prospective permissions; old owner lift cannot be recycled.
4. Fresh engineering-only exact-transport rehearsal on a sealed G/R path, with approved source fingerprint, complete original custody and zero structural failures.
5. Separate owner approval for **selection**, then an explicitly frozen, distinct **validation** release; none is inferred from this document, code, passing tests or historical ADR-0017 lift.

No new World, living individual, experiment, validation or scientific promotion was performed or authorized by this intervention. Failed/null/adverse scientific results retain the reference and prevent silent Stage-2.2 adoption. The helper `stage2_gate_design.directional_gate` performs arithmetic only, never scientific adjudication.
