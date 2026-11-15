# I3 Stage6-light: G0 native engineering transport candidate (15 November 2026)

**Status: CODE PROPOSED, NOT_RUN.** This new transport implements a source-locked, prospective G0 engineering-only path under ADR-0022. It is distinct from the synthetic 11,520-original preflights. The original Stage6 method-v1 remains immutable and deny-all.

## Contract

- G0: 16 populations x 24 founder genomes x 3 P2 F0 families x 2 repeats. **96 World opportunities and 2,304 unique native G0 lives** if explicitly launched. G0 is shared once between the later selected and random-parent arms.
- The allocation command alone (no World) generates a new 256-bit OS random root and HMAC-SHA256 domain-separated integers for world indices, generator seeds, life seeds, and 384 founders. All are checked for duplicate integers. Rejection is permanent for that root; no outcome-based reroll.
- The saved plan binds the exact Git commit, native Python source-map SHA-256, frozen-method SHA-256, owner-direction SHA-256, full allocation and plan SHA-256. Operator must publish plan bytes and digest in a durable **pre-exposure internal record outside the checkout**. Matching a supplied hash is not independent timestamp evidence.
- Before importing native World/life, the run checks the source SHA and clean checkout at Python 3.11 or 3.12. An atomic new archive-directory claim is created before the first possible birth. Existing or interrupted directories cannot be retried.
- Each native G0 life calls i3.runtime.life.run_life with the existing P1.3 funded-v2 reference motor, genome v4 and P2 F0 world generators, with complete trace. The existing deterministic gzip-original writer and per-generation SHA manifest are used. Native source, two-currency funding, organism identity, actual WorldSpec digest, terminal and horizon are checked. Failures produce engineering failure, not organism death; no retry. Output to the operator is structural only.
- This code has **no G1, G2, S1/S2, final R or science admission**. It cannot be used to infer any Stage6 scientific result, run the full rehearsal or promote I3.

## Future run (not performed in this PR)

Once merged and pinned to an exact clean SHA, with Python 3.11/3.12, create a new outside-repository plan:

```bash
PYTHONPATH=src python -m i3.lab.stage6_light_native_g0_transport allocate SOURCE_GIT_SHA SOURCE_MAP_SHA256 /custody/stage6-g0-plan.json
PYTHONPATH=src python -m i3.lab.stage6_light_native_g0_transport verify /custody/stage6-g0-plan.json
# Publish the plan and SHA before exposure, then only once:
PYTHONPATH=src python -m i3.lab.stage6_light_native_g0_transport run /custody/stage6-g0-plan.json /custody/stage6-g0-originals PREPUBLISHED_PLAN_SHA256
```

Compute SOURCE_MAP_SHA256 from the exact clean checkout using i3.runtime.provenance.source_snapshot. The archive parent must already exist, and the archive itself must not exist. This command is **not** a CI target; it opens native lives and must only be invoked after completing run-specific operational checks.

## Falsifiers and limits

The focused unittest suite covers full case matrix, disjoint seeds, deterministic allocation test vector, swapped seeds, forged permits, changed root/hash, checkout refusal and atomic no-retry, without running an organism. Python 3.11 and 3.12 exact-head CI must pass before using the new transport. The complete historical-seed disjointness review, live G1/G2 and parent mutation/selection, source-exact **full nine-phase engineering rehearsal**, all-original audit, science run-specific admission and blind reduction are outstanding. Neither unique seeds nor self-hashed plan prove ecological independence, independent witness, or anteriority.

**Scientific status unchanged:** I1 active, I3 development reference only, Stage 2.1 NOT_ISSUED/HOLD_NO_VERDICT. Stage6 G0 engineering NOT_RUN, full-scale rehearsal NOT_RUN, science NOT_RUN.
