# I3 documentation entrypoint

I3 is an independent **research proposal**, not a registered or activated engine. The [engine contract](../engine.json) declares no entrypoints, and [the registry](../../../config/engine-registry.json) continues to identify I1 as active. A green software test does not establish a scientific GO.

Read these in order, consulting the original git commit pinned in each preregistration:

1. [Current proposal status](STATUS.md): P1.3 adopted on v2, P2 methodology and P3 selection pilot documented; **P4 still NOT_RUN**.
2. [ADR-0014](../../../docs/decisions/ADR-0014-i3-lignee-enjeu-de-soi.md): selection on individual persistence and self-relevant vital accounting.
3. [Specification](SPECIFICATION.md) and [architecture](ARCHITECTURE.md): generation-owned physical and cognitive boundaries.
4. [Test plan](TEST_PLAN.md): focused software checks and open P4 scientific validation.
5. Original G2 [preregistration](G2_FIRST_FALSIFIER_PREREG.md) and [observations](studies/g2-first-falsifier/RESULTS.md).
6. Original G2b P1.1 [preregistration](G2B_P11_HELDOUT_PREREG.md) and [observations](studies/g2b-p11-heldout/RESULTS.md).
7. Original G2c P1.2 [preregistration](G2C_P12_HELDOUT_PREREG.md) and [negative result](studies/g2c-p12-heldout/RESULTS.md).

The non-adopted P1.2 implementation is preserved on branch `i3/p1.2-variant`. Do not retroactively change existing held-out gates, reuse their evaluation seeds for model selection, or describe an engineering PASS as scientific confirmation.

The first I3 lineage pilot is [prospectively preregistered](P3_PILOT_PREREG.md) and its
[complete mixed results, frozen G2 genomes and unaltered evidence](studies/p3-mutation-pilot/RESULTS.md)
are archived. Selection outcomes are **not** held-out validation and do not
prove an evolutionary advantage. P4 must use fresh, independently reserved
validation conditions under a new frozen protocol.

The existing focused tests are `python -m unittest discover -s tests/i3 -p 'test_*.py' -v`. Any future scientific study needs a prospective preregistration and newly reserved environments.
