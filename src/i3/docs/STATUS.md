# I3 — Statut d'ingénierie

**PROPOSITION. NON ENREGISTRÉ. AUCUN POINT D'ENTRÉE. AUCUN GO SCIENTIFIQUE.** I1 reste le seul moteur actif.

Décision : [ADR-0014](../../../docs/decisions/ADR-0014-i3-lignee-enjeu-de-soi.md) (accepté le 5 novembre 2026). Spécification : [SPECIFICATION.md](SPECIFICATION.md).

| Phase | État |
| --- | --- |
| P0 Décision | Fait : ADR-0014 accepté, invariant de naissance reformulé |
| P1 Noyau | Implémenté : monde séparé, corps à cinq canaux, monnaie vitale, capacités vulnérables, génome, cognition, rejeu exact |
| G2 Porte | **Franchie** le 5 novembre 2026 : 30/30 vies ont bu, rejeu exact, 0,40 ms par pas ([résultat](studies/g2-first-falsifier/RESULTS.md)). Deux défauts relevés pour P1.1 |
| P1.1 | Adopté (porte G2b, [résultat](studies/g2b-p11-heldout/RESULTS.md)) : non inférieur à P1, sans gain mesurable |
| P1.2 | **Rejeté** par la porte G2c ([résultat](studies/g2c-p12-heldout/RESULTS.md)) : révision bien meilleure (69 contre 46, p = 0,0007) mais non-infériorité générale manquée d'une vie. Variante conservée dans la branche `i3/p1.2-variant` |
| P1.3 | **Adopté sur le substrat v2** par la porte G2e sous sélection ([résultat](studies/g2e-p13-v2/RESULTS.md)) : 478 survies sur 1 000 contre 364 (p = 4 × 10⁻⁹) ; révision après tarissement dans 60 % des vies contre 23 %. Cognition de référence : génome `i3-genome-v3` |
| P2 Mondes | Implémentation d'ingénierie en revue : 3 écologies, partitions étanches, audit de coûts et tarif fixe scellé ; pas de validation scientifique ni de pilote P3 |
| P3 Lignée | Non commencé |
| P4 Étude | Non commencé |

Tests : `python -m unittest discover -s tests/i3 -p 'test_*.py' -v`. Une suite verte valide le logiciel au SHA exact, pas un comportement adaptatif.

## Validated continuation (5 November 2026)

[Development plan](DEVELOPMENT_PLAN.md), tracking
[#1002](https://github.com/josselin-orta-lab/individual-zero/issues/1002).
The first technical slice separates sensorimotor bookkeeping from learning,
adds observer-only life provenance and exposes requested/paid/unpaid cognition.
Negative work counters are rejected; normal P1.1 decision rules are unchanged.

**Gap identified by the first slice (historical v1):** zero-clamping hid
unfunded work, and replay could remain unbilled at death/censoring. The v2
correction below addresses these defects; merely reporting them in #1003 did
not. No new held-out result or lineage experiment is claimed. Historical
results above remain tied to their original v1 source.

## Funded physical substrate v2 (#1004)

Current execution uses [the v2 cognitive funding contract](COGNITIVE_FUNDING.md):
advance decision allowances, strict reserve debits, post-action learning/replay
prepaid in the same tick, no cognition after death, and transactional motor
admission. Exhaustion can produce passive inactivity, never forced sleep.
P1.1 cognitive score rules remain the reference, but its old v1 measurements
cannot certify this changed substrate. Historical G2/G2b/G2c files stay intact.

Development comparison (not a held-out study): 4/4 short lives survive in both
versions; at 400 steps, 8/16 survive versus 14/16 in v1. All v2 declared work is
settled with no pending replay. This adverse outcome is retained. The focused
suite had 62 tests at #1004; exact CI status belongs to the implementation PR.

Laboratory probes (`lab/probes.py`) now execute under v2 with the individual's
payment rules; they previously raised on most development worlds. They are still
not validated or cost-matched comparators: that remains P2 work. See
[COGNITIVE_FUNDING.md](COGNITIVE_FUNDING.md). Focused suite: 66 tests.

P1.3 has since been compared on the same v2 substrate in both arms (G2e, ADR-0015)
and adopted; see the P1.3 row above. P2 engineering work is described in
[P2_ECOLOGY_AND_PROBE_CONTRACT.md](P2_ECOLOGY_AND_PROBE_CONTRACT.md).
It freezes stable/depletion/pulse ecologies, physically separated cohorts,
paid probe receipts and a development-derived static cost profile.
Actual full-horizon cost equivalence is not assumed; unmatched probes are
reported explicitly. P3 is not running. No scientific GO.
