# Stage 11 : canonicalité des paramètres versionnés du budget UC

**Date : 11 octobre 2026.** **Type de preuve : régression logicielle publique, non held-out, non Golden, non scientifique.** Source normative exclusive et inchangée : `docs/architecture/reference/en/mvp-specification-v1.2.1.md`, notamment §16.3, S-11/P-43, INV-21/22 et la relecture exacte des propriétaires causaux (§17). **Stage 11 EN COURS ; Stage 9 scientifique NO-GO ; PR #25 ouverte en Draft, non fusionnée.**

## Antériorité et changements attribuables

- HEAD avant incrément : `ec5f9145c4347a6b51be21124f438a9a95d5beab`, après durcissement des entrées `open_cycle`/`charge`.
- Dernier SHA de code/tests précédemment validé : `ee9aa8803e4e81045c4a2defd5224036eff92de8`, [CI #38139987533](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38139987533), **908/908 PASS** Python 3.11 et 3.12 ; cette ancienne réussite ne prouve pas le nouvel incrément.
- **Protocole prospectif de régression logicielle** [stage11-scheduler-budget-config-canonicality-protocol.en.md](stage11-scheduler-budget-config-canonicality-protocol.en.md), figé **avant** les modifications et essais au commit **`bbd818beaf813e761fdae4896b304422cc798de6`**. Il ne constitue pas un préenregistrement scientifique.
- Correctif source : **`7da9cf60181ac7dcd368f589d38baef5d566129b`**, `src/lab/compute_budget.py`.
- Trois nouvelles méthodes de test : **`92cab509678e92dafa19e6854052c897bd835269`**, `tests/test_compute_budget.py`. **C'est le SHA exact du code et des tests vérifiés en CI.**
- Protocole **séparé, documentaire uniquement**, pour la future distinction des occurrences de cycle : **`4628e557c16cbe9f99ce4da71b82d8cb06e31e5f`**, [stage11-scheduler-cycle-occurrence-custody-protocol.en.md](stage11-scheduler-cycle-occurrence-custody-protocol.en.md). Aucune expérimentation ni correction de réouverture de cycle n'est déclarée par ce document ; son commit est **postérieur au SHA de code testé**.

## Problème technique préexistant

`ComputeBudgetConfig` est une dataclass figée, mais ses annotations de type ne sont pas vérifiées automatiquement à l'exécution. La fonction `validate()` utilisait des comparaisons telles que `value < 0` : des valeurs de type `bool`, `float` ou NaN pouvaient se présenter comme des plafonds, des enveloppes ou des coûts UC. Des registres et identifiants non canoniques pouvaient provoquer des exceptions indirectes plutôt qu'un rejet explicite. Un `count` entier ne suffit pas à garantir une dépense entière si le **coût configuré** vaut une fraction ou NaN.

La situation concerne la **configuration logicielle P-43**, non une observation physique, une proposition d'Exploration ou un résultat scientifique.

## Correction minimale

`ComputeBudgetConfig.validate()` impose désormais, **sans coercition ni arrondi** :

1. Version non vide de type Python `str` **exact**.
2. `cycle_ceiling`, `protected_capacity`, tous les plafonds de modules et tous les coûts par opération : **`int` exact ≥ 0**. Aucun booléen, nombre fractionnaire, valeur non finie, texte ou conteneur n'est accepté. Les valeurs légitimes de **zéro** restent valides.
3. `module_envelopes` et `operation_costs` : mappings non vides, contenant uniquement des clés `str` exactes non vides et des valeurs entières canoniques. Les mappings immuables (`MappingProxyType`) sont conservés.
4. `protected_modules` : `frozenset` exact de chaînes non vides, dont chaque membre possède une enveloppe déclarée. Ensemble vide, un ou plusieurs modules protégés demeurent admis. La capacité réservée ne peut pas dépasser `B_cycle`.
5. Rejet explicite avec `ValueError` dès la validation du modèle, donc **avant la construction d'un propriétaire `CycleComputeBudget`**, l'ouverture d'un cycle ou toute charge.

**Inchangés :** `open_cycle`, `charge`, `quote_operations`, `restore_causal_state`, les montants P-43 existants, l'ordre des refus, les droits des modules protégés, les priorités Planning/Exploration, Action Control, journaux, observations physiques, captures et formats de snapshots. La spécification normative anglaise v1.2.1 n'a pas été modifiée.

## Tests ajoutés et contrôles de déterminisme

Trois nouvelles méthodes de `unittest` portent le total de la suite du dépôt de **908 à 911 méthodes**.

- **85 variantes synthétiques invalides** de configuration : treize valeurs non canoniques appliquées séparément à quatre champs UC (**52** cas), dépassement de réserve (**1**), versions invalides (**6**), mappings/enveloppes invalides (**9**), coûts/opérations invalides (**8**) et collections/identifiants protégés invalides (**9**). Chaque sous-cas doit provoquer `ValueError` aussi bien dans `config.validate()` que dans `CycleComputeBudget(config=config)`. Ces 85 sous-cas ne sont **pas** 85 méthodes supplémentaires.
- **Cinq configurations positives** : budget historique, mappings protégés en lecture seule, budget totalement nul avec opération gratuite explicitement déclarée, deux modules protégés et absence déclarée de module protégé. Validation répétée sans mutation du modèle, charges réelles avec `BudgetCharge.requested_uc` entier, capture et restauration périodiques via `SnapshotManager`.
- Chaque configuration positive est rejouée **deux fois indépendamment**, avec les mêmes pas, points de capture et ordre de restauration. Les reçus, octets des états propriétaires, identifiants de snapshots, octets du journal technique et hash final sont identiques. Les événements `snapshot_taken` et `snapshot_restored` restent append-only.
- Rejet explicite d'un coût `NaN` avant toute naissance de Scheduler, avec contrôle positif immédiat d'une charge `small=2 UC` et d'un état causal entièrement entier et canonique.

Ces vérifications sont **synthétiques et publiques**. Elles ne donnent accès à aucune vérité de danger caché et ne définissent aucun protocole expérimental scientifique.

## Campagnes GitHub Actions exécutées sur le SHA exact

| Exécution | Code/tests SHA | Python | Tests | Statut |
| --- | --- | --- | --- | --- |
| [CI courte #38140736570](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38140736570) | `92cab509678e92dafa19e6854052c897bd835269` | **3.12.15** | **911/911 PASS**, 70,382 s | SUCCESS |
| [CI complète #38140853911](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38140853911) | **même SHA** | **3.11.17** | **911/911 PASS**, 115,760 s | SUCCESS |
| [CI complète #38140853911](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38140853911) | **même SHA** | **3.12.15** | **911/911 PASS**, 119,710 s | SUCCESS |

La campagne complète est **SUCCESS**, avec **deux jobs exécutés**, aucun échec d'étape et **15 artefacts** : journaux techniques de référence Stages 1–4 et 6–8, calibration/benchmark Stage 8 et diagnostics Stage 9. Le job rapide additionnel du workflow complet est volontairement `skipped` par la règle de maîtrise des coûts et n'est pas compté comme une troisième validation. Aucun workflow permanent ni déclencheur de CI n'a été modifié.

Les diagnostics Stage 9 restent **des contrôles de développement**, et **ne constituent ni une campagne held-out ni une acceptation scientifique**. Aucun Golden scientifique indépendant n'a été déclaré.

## Limites et verrous ouverts

**Établi logiciellement :** l'API refuse les configurations P-43 non canoniques incluses dans les tests, sans modifier les configurations valides ; les charges et snapshots demeurent déterministes ; les suites intégrées Python 3.11/3.12 sont vertes sur le SHA effectivement testé.

**Non démontré :** défense contre un code Python hostile accédant à des attributs privés, immutabilité profonde des mappings fournis par l'appelant **après** la validation (la dataclass figée contient encore des objets `dict` mutables), sécurité universelle des entrées futures, arbitrage comportemental optimal, découverte autonome de dangers, récupération autonome, Goldens historiques indépendamment acceptés, ou levée du NO-GO scientifique Stage 9.

**Verrou de chronologie enregistré mais NON RÉSOLU :** `CycleComputeBudget.open_cycle` remet les compteurs à zéro. Une seconde ouverture du **même événement logique** pourrait donc effacer des UC déjà dépensées. Mais un même numéro de cycle (notamment `1`) est légitimement réutilisé au pas physique suivant et peut interagir avec les tentatives de rollback. Il serait erroné de refuser simplement tout numéro déjà vu. Le protocole [stage11-scheduler-cycle-occurrence-custody-protocol.en.md](stage11-scheduler-cycle-occurrence-custody-protocol.en.md) impose un audit par `t_monde`, `attempt_ref` et `cycle`, ainsi que des snapshots comparables, **avant** toute modification de cette sémantique.

**Autre frontière non corrigée :** isoler les mappings P-43 de l'appelant après leur validation, afin qu'une mutation ultérieure non versionnée ne change pas les coûts en cours d'exécution. Ce sujet demanderait un protocole de propriété des données distinct.

### Reproduction

Checkout du code/tests exactement à `92cab509678e92dafa19e6854052c897bd835269`, Python 3.11 ou 3.12 et dépendances de projet :

```sh
python -m pip install -e .
python -m unittest discover -s tests -p 'test_compute_budget.py' -v
python -m unittest discover -s tests -p 'test_stage11_geographic_capacity_guard.py' -v
python -m unittest discover -s tests -p 'test_snapshots.py' -v
python -m unittest discover -s tests -q
```

Les commits de protocoles et résultats postérieurs au SHA testé sont **documentaires** et ne doivent pas être invoqués comme nouvelles validations. **Stage 11 EN COURS ; Stage 9 NO-GO scientifique ; PR #25 Draft et non fusionnée.** `main`, protections, permissions et visibilité de dépôt demeurent inchangés.
