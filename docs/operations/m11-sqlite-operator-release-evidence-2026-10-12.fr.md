# M-11 | Rapport de campagne de réception logicielle | 12 octobre 2026

## Décision et portée

**Résultat technique Stage 10/11 : PASS ciblé.** **M-11 du MVP v1.3.1 : INCOMPLETE, pas de PASS global.** Le périmètre testé se limite au coordinateur SQLite opt-in de Stage 10 et Stage 11. Stage 12 conserve son propre WAL fsyncé non transactionnellement coordonné. Aucune réception opérateur ni validation scientifique finale n'est attribuée à cette campagne.

Source normative : `docs/architecture/reference/en/mvp-specification-v1.3.1.md`, §§4, 5, 7 et 9 (M-11/M-12). Aucun changement de physique, de la spécification ou du verdict Stage 9.

## Provenance immuable

- PR de validation : [#125](https://github.com/josselin-orta-lab/individual-zero/pull/125)
- SHA de branche validé : `a18602c78029736b23c74d7d93e44aff040d7407`
- Commit éphémère de fusion effectivement exécuté : `29d9e267826b30de95cf404b960cf030e6285a90`
- **Les deux commits ont exactement le même Git tree** : `fa99b6679c9fe731a01503b4beade604dfb6fa6f`; le code testé est identique.
- [GitHub Actions M-11 complet](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38283811030) : SUCCESS Python 3.11 / 3.12.
- [CI rapide](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38283811108) : SUCCESS Python 3.12 ; validation exhaustive générale non exécutée par ce workflow.

## Résultats contrôlés

| Critère | Python 3.11.17 | Python 3.12.15 |
| --- | ---: | ---: |
| Tests unitaires SQLite | 36 PASS | 36 PASS |
| Tests pytest M-11 / crash / CLI / frontière Stage 12 | 22 PASS | 22 PASS |
| Transitions physiques enregistrées et fermées | 600 | 600 |
| Stage 10 / Stage 11 | 300 / 300 | 300 / 300 |
| Naissances indépendantes | 12 | 12 |
| Reprises à froid entre processus | 12 | 12 |
| Décès dans les trajectoires longues | 0 | 0 |
| Occurrences causales auditées | 34 614 | 34 614 |
| Correspondance export JSONL / table SQLite | OUI | OUI |
| Temps du runner pour la campagne (secondes) | 256,014 | 184,906 |

Chaque vie expérimentale comporte 50 transitions, scindées en deux sessions de 25. Les identités sont uniques et les reprises ciblent la génération courante, non une génération historique. L'audit relit la base avec ses événements et compare SHA, identifiant, génération, compte, horloge et journal. Une inspection additionnelle des ZIP confirme les événements `step_opened`, `command_admitted`, `command_experienced`, `world_transition_experienced` et `step_closed` pour chacun des 600 pas, ainsi que la correspondance octet pour octet de chaque export avec sa table SQLite. Le test de décès irréversible et les six fenêtres `os._exit` sont couverts par les tests ciblés, pas par les 600 pas de cette campagne.

### Artefacts

- [Preuves Python 3.11](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38283811030/artifacts/11762871970) : SQLite, JSONL, manifest. SHA-256 canonique du manifeste : `098f1a27b0ef4977f5aeb5c1a8387f09b479ecd020b600401af5b30529e65af9`.
- [Preuves Python 3.12](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38283811030/artifacts/11762816868) : SQLite, JSONL, manifest. SHA-256 canonique du manifeste : `15fd2742bc02c27bfef9e82abc67f1f5fcc7fdde173577f6aef5f08356701f46`.

## Défaut reproduit et corrigé

La première campagne sur PR #125 a échoué dans les deux versions Python avec `invalid sleep-recovery chronology`. Le validateur refusait une véritable récupération de sommeil antérieure à un calcul ultérieur de pression pendant la veille. `src/i0/modules/sleep_health.py` accepte désormais la chronologie normale, tout en rejetant une récupération prétendument effectuée sur le même pas que le gel de pression de veille. Régression ajoutée dans `tests/test_stage10_health_runtime.py`, repassée dans CI.

## Limites non masquées

1. **Stage 12 non atomique** : `M11TransactionalMortal.birth` refuse explicitement le runtime Stage 12 avec WAL indépendant. Ne pas déclarer M-11 global PASS ; intégrer tous ses propriétaires dans une même génération durable avant de permettre sa reprise.
2. **Diversité des trajectoires** : les 12 vies donnent seulement **deux empreintes distinctes de journaux**, une par runtime, répétées six fois sur la même configuration déterministe. Les 600 pas sont physiques et comptables, mais il n'y a pas six scénarios indépendamment contrastés par runtime. Ce résultat est une hypothèse logicielle, pas une preuve scientifique de comportement ni une campagne held-out.
3. **Pannes adversariales additionnelles** : les résultats ne démontrent pas la maîtrise exhaustive de toutes les défaillances de disque, systèmes de fichiers hétérogènes, injections de vérité indépendante, ni tous les états Stage 10/11/12 combinés.
4. **Réception** : le responsable opérateur seul peut approuver le périmètre du stage ; `operator_acceptance=null` et `scientific_validation=null` dans les manifestes. Stage 9 demeure NO-GO et l'issue Stage 12 #110 reste distincte.

**Avis de revue :** fusionner le correctif sommeil et le protocole de collecte dans `main` en tant que renforcement logiciel. Garder le verdict M-11 global **IN_PROGRESS / NOT ACCEPTED** tant que Stage 12 et la réception opérateur ne sont pas résolus.