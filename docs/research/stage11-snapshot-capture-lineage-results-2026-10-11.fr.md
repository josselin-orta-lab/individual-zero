# Stage 11 : cohérence physique des snapshots géographiques

**Date :** 11 octobre 2026 (Europe/Paris). **Nature :** vérification d'intégrité logicielle sur objets de perception synthétiques, **non held-out, non Golden et non scientifique**. La spécification normative anglaise v1.2.1 n'a pas été modifiée.

## Protocole, code et validation

- [Protocole de contrôle préalablement enregistré](stage11-snapshot-capture-lineage-protocol.en.md), commit `54afcf5552f53179cf6f6e5d76173e53af7b0c8c`.
- Code testé : **`8acba9ce2bd12c97031186dba8e268f901f1bfda`**.
- [GitHub Actions #38122271021](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38122271021) : **846 tests unitaires réussis sous Python 3.12**, sans échec, plus étape smoke. Les campagnes Golden complètes et Python 3.11 restent distinctes et non réalisées ici.
- Nouvelle régression : `tests/test_stage11_snapshot_capture_lineage.py` ; modification limitée de `src/i0/modules/geographic_exploration.py`, méthode `restore_causal_state`.
- Reproduction ciblée : `python -m unittest tests.test_stage11_snapshot_capture_lineage -v`.

## Défaut identifié par inspection

L'export naturel du propriétaire `GeographicExploration` ne peut produire que deux formes cohérentes :

1. Avant la première capture physique : **aucune visite enregistrée** et `last_capture = null`.
2. Après une ou plusieurs captures physiques : **au moins un site enregistré** et une `last_capture` désignant une position physiquement observée du registre.

Avant correction, un snapshot fabriqué contenant `visits=[[2,2,1]]` avec `last_capture=null` et aucune offre ni relevé pouvait être accepté. Cette incohérence n'est pas un état légitime créé par le propriétaire ; elle brouillerait la chronologie lors d'un rejeu ou d'une reprise.

La restauration rejette maintenant explicitement la discordance `last_capture is None` / registre vide, **avant toute affectation de l'état causal**. Elle ne reconstruit ni capture fictive, ni date, ni visite. Aucun algorithme de routage, seuil de sécurité, coût UC, veto d'Action Control ou schéma normalisé n'a changé.

## Portée des tests nouveaux

| Contrat | Local v1 | Relevés v2 | Actualisation v3 |
| --- | --- | --- | --- |
| Snapshot initial vide, export/reprise exacts | PASS | PASS | PASS |
| Capture unitaire réelle-forme, visite datée, reprise exacte | PASS | PASS | PASS |
| Visites non vides mais dernière capture absente : refus atomique | PASS | PASS | PASS |
| Dernière capture forgée alors que les visites sont vides : refus atomique | PASS | PASS | PASS |
| Nouvelle capture au même site, aucune nouveauté fictive | PASS | PASS | PASS |
| Premier relevé local après une capture de l'étape suivante | Sans relevé | PASS | PASS |
| Relevé existant, reprise exacte | Non applicable | PASS | PASS |

Les données utilisées sont des objets **unitaires synthétiques de forme Perception**. Elles ne constituent ni des observations physiques du monde simulé, ni des attestations causales, ni un résultat scientifique. Les tests confirment l'égalité exacte des états avant et après une tentative de restauration rejetée.

## Relation avec le contrôle de capacité contemporain

Le [protocole de saturation des routes](stage11-geographic-capacity-atomicity-protocol.en.md) et son [rapport autonome de 843 tests](stage11-geographic-capacity-atomicity-results-2026-10-11.fr.md) concernent un autre défaut : dépassement de `max_distinct_sites` et mutation partielle d'une offre de transit. La nouvelle campagne à **846 tests** comprend ces contrôles historiques plus trois nouveaux tests de cohérence de `last_capture`.

Les empreintes des campagnes de routage antérieures restent rattachées aux **commits sur lesquels elles ont été mesurées**. La campagne actuelle ne réattribue pas leurs résultats ni leurs décisions au nouveau commit. Elle valide uniquement les contrats logiciels couverts par la suite unitaire.

## Limites

- Le refus atomique du propriétaire face à une arrivée physique qui dépasse sa capacité **ne prouve pas** que la simulation complète puisse continuer sans intervention ou sans rollback. La politique d'exécution globale à la saturation reste un point ouvert.
- Les registres de sites ne prouvent pas à eux seuls la sécurité face aux dangers cachés, la qualité d'un plan long, ni la continuité autobiographique.
- Python 3.11 de référence, Goldens longs, intégration Stage 10/12 et validation scientifique indépendante restent à vérifier séparément.

**Stage 11 : EN COURS. Stage 9 : SOFTWARE IMPLEMENTED / SCIENTIFIC VALIDATION PENDING / NO-GO.** La PR #25 demeure en brouillon, non fusionnée.
