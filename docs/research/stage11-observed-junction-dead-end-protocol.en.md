# Stage 11: observed junction and multistep dead-end baseline

**Registered before code or runs, 11 October 2026.** Class: public software-development diagnostic, *not* independent held-out science. Normative: `docs/architecture/reference/en/mvp-specification-v1.2.1.md` (especially §14, §9.4, DC-07, DC-11, INV-08, physical observation boundary). Stage 9 scientific status remains NO-GO. Existing Stage 11 8-step straight-corridor diagnostic remains intact.

## Experimental question

Does the currently implemented opt-in local geographic Exploration revisit a physically visited junction when its first chosen branch ends at a dead end, even though an **alternative passable branch was available in the first ordinary local Perception capture**? This diagnostic must not inject an exploration goal, mark a visited tile as novel, use hidden layout truth to select options, or alter canonical Action Control. A null result is expected to be retained rather than repaired by test-specific scripting.

## Fixed public layouts and controls

The actual physical world is the standard Stage 11 reference, with neutral body `energy=50, food=60, water=60, integrity=100`, origin (2,2), frozen Equipment E-v1, empty water/resources/creatures/dangers and ordinary P-48 geography ON, max one target per cycle. A fixed eastward cul-de-sac comprises (2,2) → (3,2) → (4,2). At the origin, north and west are blocked. Each intermediate eastern position has north and south blocked; the eastern endpoint has east blocked and can return only west.

- `junction_open`: a second southward branch of passable positions (2,3) → (2,4) exists, with walls to its east, west and south. The origin's south passability is **locally observable at the first capture**; it is not a goal inserted into the individual.
- `junction_sealed`: same source configuration but (2,3) is also an obstacle, creating a true cul-de-sac with no alternative passage. Used as a negative control, not to retune agent behavior.

Run exactly 10 consecutive physical steps for each independently created runtime, with no authored action schedule, external repositioning, new safety knowledge or hidden oracle-to-agent channel. A third public diagnostic may later add an opt-in **general** visit-history routing mechanism, but it requires a separate prospective protocol, code version, snapshot scheme, budget accounting and tests. Do not declare it already implemented.

## Frozen measurements and falsifiable checks

- Hash all declared world/layout, config, and initially accessible local capture inputs. The sole Lab-only layout scorer must not feed a hidden destination or branch flag into Exploration/Planning.
- Record per-step ordinary executed primitive and option ref, real `perceptual_capture` positions, physically observed next-step arrivals, confirmed visit ledger, and safety journal verification.
- Extract first local passability of south versus east from a **separate read-only public capture** before execution, and never reuse it as agent input. Do not count a world-layout branch as observed merely because the Lab knows the cells.
- Report first eastward advancement, reached dead-end endpoint, return to physically observed junction (only if subsequently captured), and confirmed arrival in the alternate branch (2,3) or (2,4). Distinguish command sent in final step from next-step arrival.
- Compare to sealed layout and independently rerun each condition: identical config and seed must produce exactly matching canonical output and journal bytes. Preserve SHA-256 for source, input, output, journal.
- Do not define PASS to require backward motion, alternative exploration or learned risk; failures to do those are the *subject* of measurement. Tests must only assert epistemic isolation, valid physical visits, deterministic replay and truthful accounting.

A locally observed alternative is an opportunity, not proof that the agent has a long-range planner. No Stage 9 held-out evidence, Stage 11 scientific GO, Python 3.11 full suite or Golden can be inferred from this software fixture.
