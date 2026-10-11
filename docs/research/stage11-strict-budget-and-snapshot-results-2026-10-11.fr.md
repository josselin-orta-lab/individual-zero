# Stage 11 : dégradation du budget UC et restauration de sécurité canonique

**Date :** 11 octobre 2026 (Europe/Paris). **Classification :** diagnostic public logiciel et test unitaire de restauration. **Aucune validation scientifique, aucun held-out.**

## Antériorité technique et validation

- [Protocole de contrôle déclaré AVANT les modifications et résultats](stage11-strict-budget-and-snapshot-protocol.en.md).
- **Code réellement testé :** `3c114154db3625ad09f20808bbe1bb4c067e72a5`.
- [GitHub Actions #38113832695](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38113832695) : **773 tests unitaires réussis sous Python 3.12**, vérification smoke réussie. La matrice Python 3.11 et les Goldens longs n'ont PAS été exécutés ici.
- Code : `src/lab/stage11_runtime.py`. Banc public : `src/lab/stage11_degraded_budget_probe.py`. Contrôles : `tests/test_stage11_strict_budget_and_snapshot.py`.
- Commande de diagnostic : `python -m lab.stage11_degraded_budget_probe`.
- Classification des sorties : `development_only_not_heldout`, `scientific_verdict = null`, `heldout = false`.

## Modifications fonctionnelles

Une impossibilité de payer `exploration_observe`, `geographic_admissibility_preflight` ou `planning_build` retire maintenant explicitement les cibles géographiques offertes par le propriétaire Exploration. Le runtime écrit `stage11_geographic_budget_deferred` avec le nom de l'opération qui manque, la position de la capture Perception et le motif `incomplete_budget`.

Ce retrait **ne modifie pas** la liste des sites physiquement visités : la capture reste valide même lorsque la cognition est dégradée. Une cible refusée faute de budget n'est ni une case dangereuse, ni une absence démontrée de nouveauté, ni une prédiction numérique.

Le veto d'Action Control, les catégories de sécurité et la source canonique Causal Model ne sont pas modifiés. Le mode géographique demeure désactivé dans les fixtures de référence Stage 9.

## Quatre variantes publiques (3 pas de monde)

| Version de configuration | UC de préconsultation acceptées | Refus `preflight` | Refus `planning_build` | Refus `exploration_observe` | Actions géographiques appliquées | Sites perçus | Cibles encore offertes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Planning 0 UC | 0 | **14** | 0 | 0 | **0** | 1 | **0** |
| Planning 1 UC | **14** | 0 | **14** | 0 | **0** | 1 | **0** |
| Planning 3 UC | **3** | 0 | 0 | 0 | **3** | 3 | 1 |
| Exploration 0 UC | 0 | 0 | 0 | **15** | **0** | 1 | **0** |

Dans le cas Planning 3 UC, `planning_build` consomme 6 UC cumulées (trois constructions acceptées à 2 UC chacune) ; les trois déplacements ont été réellement appliqués. Les trois sites distincts sont uniquement les positions observées dans les captures Perception. Le dernier déplacement ne devient pas une quatrième visite sans capture ultérieure.

Dans le cas Planning 1 UC, les 14 préconsultations sont financées, mais les 14 constructions de plans échouent faute de 2 UC supplémentaires dans leur propre cycle ; les 28 UC **demandées et rejetées** ne sont pas comptées comme consommées. Dans le cas Planning 0 UC, 14 UC de préconsultation sont demandées et rejetées. Dans le cas Exploration 0 UC, 15 UC de traitement sont demandées et rejetées.

Tous les événements de suspension respectent la structure déclarée ; les sorties des quatre configurations sont exactement identiques entre deux exécutions neuves de la même fixture.

## Snapshot et propriétaire unique des faits de sécurité

Le test `Stage11CanonicalSnapshotTests.test_snapshot_restores_live_admissibility_and_geographic_owner` utilise le vrai `SnapshotManager` et le jeu complet des propriétaires causaux du runtime. Le point de contrôle est vérifié cryptographiquement.

Un jeu **synthétique, uniquement unitaire** de deux attestations DC-05 fait apparaître temporairement une règle `lethal_zone` pour `(2,1)` dans le propriétaire `CausalModel`. L'adaptateur en lecture seule `CanonicalSafetyFacts` transmet alors `known_lethal` à Action Control : une cible vers le nord est exclue.

La restauration vérifiée du snapshot remet le Causal Model et l'Exploration à leur état antérieur. Action Control lit aussitôt le statut `unknown` et la cible nord redevient candidate `indeterminate`, sans recopier ou purger un cache de zones interdites. Le journal append-only conserve ses événements de snapshot et n'est pas rembobiné. **Ces deux attestations sont fictives et servent exclusivement à tester des règles logicielles : elles ne proviennent pas du monde physique et ne satisfont aucune exigence de preuve scientifique.**

## Empreintes SHA-256 de diagnostics publics

| Variante | Résultat canonique | Tête du journal |
| --- | --- | --- |
| Planning 0 UC | `81e8e573f7f4a5ebf1fdbdc14b19ddbd50a1317969cb0ba3b3288f88f464ca35` | `de36767249785690dfef9c27d92df5b6373b3c82e5f6a0eed6eb2ffd8bde70dd` |
| Planning 1 UC | `839385b0a92779ecae55de3da14f8c02d96ce4721d5c637dd7a19e35144dfcdb` | `281574265ab2d9818a3cb649c9e65377ed1f43e5cc8a9c58eb3147c376573f2d` |
| Planning 3 UC | `7a672854ae59b4e4cfb8d070cce452c66acae0eb5c649c0f95b7315aa3d9134f` | `df13f5e0787744691266e21aaae6d41bb58a8932f56bd7ba86550df6d65fc257` |
| Exploration 0 UC | `5e90e0b33bfa4abfb72cf5ed1ebff06dfa2a80fc2cc3f25b17f44893c8b95c80` | `2eb1f511b24d72cfca1b62458ee7bb804875301b7b09182faea7df2195da1b01` |

Les empreintes constatent l'intégrité et la reproductibilité des exécutions logicielles du code et des paramètres déclarés ; elles ne certifient pas une campagne de recherche indépendante.

## Limites et incidents à traiter

1. **Ordonnancement de la consultation anticipée.** Le préfiltrage en lecture seule interroge actuellement Action Control pendant la préparation des hooks, AVANT la tentative de charge Planning en phase 1. Dans un scénario Planning à 0 UC, une consultation préliminaire peut donc avoir eu lieu même si sa charge est rejetée. Le présent test vérifie la suspension avant toute option appliquée, **pas** l'absence de travail anticipé non facturable. Un correctif d'ordonnancement devra conserver les frontières d'ownership des phases et la validité de l'évaluation intrinsèque.
2. **Volume des traces.** Une exploration à budget nul produit un marqueur `exploration_observe` puis souvent un second `upstream_cognitive_charge` dans le même cycle. Cela reste véridique, mais redondant. Ne pas masquer la limitation par un compteur de "récompense" ou en altérant les UC.
3. **Recherche de multi-pas absente.** Lorsqu'aucune case voisine inédite n'est disponible, les propositions géographiques s'arrêtent localement ; aucun contournement, plan global ni preuve de couverture d'une carte inconnue n'est présent.
4. **Validation scientifique inchangée.** Les périmètres de modélisation/sommeil Stage 10, Stage 12, dangers invisibles, longues trajectoires, replay Python 3.11 et suites Golden doivent encore être validés. La campagne held-out du Stage 9 demeure distincte et non autorisée.

**Stage 11 : EN COURS. Stage 9 : SOFTWARE IMPLEMENTED / SCIENTIFIC VALIDATION PENDING / NO-GO. La PR reste en brouillon, non fusionnée.**
