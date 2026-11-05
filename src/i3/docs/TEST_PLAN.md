# I3 — Plan de test

| Niveau | Contenu | État |
| --- | --- | --- |
| Contrat logiciel | `tests/i3/test_core.py` : génome fermé, physique v4, monnaie vitale, capacités, capture locale, mort irréversible, nouveau-né vierge, rejeu exact, invariance par renommage, pas d'abstention par défaut, `attendre` non privilégié, budget de temps | Implémenté |
| Porte G2 | Falsificateur comportemental préinscrit + rejeu + ≤ 1 ms/pas | Préinscrit |
| P2 | Générateur de familles, sonde de faisabilité, test dynamique d'invariance sur mondes générés | À faire |
| P3 | Lignée, registre, test de non-transmission entre générations | À faire |
| P4 | Plan 2 × 2 et ablations d'enjeu, préinscrits à la porte G4 | À faire |

## Foundation controls

`tests/i3/test_foundation.py` adds software-only checks for valid cognitive
work, explicit payment shortfalls, pending replay bills, sensorimotor updates
independent of learned updates, and full-world/source manifests. Four original
development-fixture hashes check behavioral parity. These are not held-out
scientific evaluations. See [development plan](DEVELOPMENT_PLAN.md) for the
open funding gap and the approved P1.3/P2/P3/P4 sequence.

## Funded substrate v2 (#1004)

`test_funded_cognition.py` adds pre-computation allowance, strict physical debit,
transaction rollback, exhaustion/inactivity, immediate bounded replay and
no-postmortem-work checks. `test_foundation.py` now expects overdraft rejection
and v2 phase evidence rather than the historical observer-only shortfall and
pending-replay behavior. Historical v1 hashes are retained but are not v2 parity
targets. No historical result is rewritten to make tests pass.

Current focused suite: 62 tests. The [funding contract](COGNITIVE_FUNDING.md)
records exact model limits and a development-only adverse differential. Engine
activation, a 1 ms performance guarantee, learning benefit and lineage outcomes
are NOT established by these checks.
