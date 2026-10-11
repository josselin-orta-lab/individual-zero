# Stage 11 : admission canonique des cycles et des comptes UC du Scheduler

**Date : 11 octobre 2026. Classification : régression logicielle publique, non held-out, non Golden, non scientifique.** Source normative exclusive et inchangée : `docs/architecture/reference/en/mvp-specification-v1.2.1.md`, notamment §16.3 / P-43, S-11.1 à S-11.3, §17.1–17.2, §17.6, INV-21 et INV-22. **Stage 11 EN COURS. Stage 9 NO-GO scientifique. PR #25 ouverte, Draft, non fusionnée.**

## Point de départ et antériorité du protocole

HEAD de départ : `da97d85b659ad8cd39ca144a01634ae4bea19209`, dernier commit documentaire de l'incrément précédent. La dernière validation antérieure de code était `435fa15a81a54f6a407774a76834e4ef2c6627e7`, [CI #38139076290](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38139076290) : **904/904 tests** sous Python 3.11.17 et sous Python 3.12.15. Elle ne s'applique **pas** au nouveau SHA.

Le [protocole public préalable](stage11-scheduler-uc-input-canonicality-protocol.en.md) a été commité **avant la correction et les tests**, commit **`c2015cf8bafa663efadfd433ea2b029c636b0762`**. Il définit des cas synthétiques publics et n'est pas un préenregistrement scientifique. Les décisions normatives ou les seuils P-43 n'ont jamais été recalibrés à partir des résultats.

## Défaut isolé

Après la sécurisation de `restore_causal_state()`, deux APIs productrices de `CycleComputeBudget` restaient permissives :

- `open_cycle(cycle)` vérifiait seulement `cycle < 1`. Un booléen `True` ou un `float` (y compris NaN ou infini pour les comparaisons) pouvait franchir ce test et ouvrir un cycle avec un identifiant non canonique.
- `charge(module, operation, count)` vérifiait seulement `count < 0`. Un booléen ou une quantité fractionnaire pouvait donc être interprété comme du travail logique, altérant des compteurs normalement entiers ; NaN pouvait échapper aux comparaisons usuelles de dépassement.
- Les identifiants de module ou d'opération non hashables provoquaient un `TypeError` accidentel au lieu d'un rejet contractuel `ValueError`.

Ce défaut concerne les **entrées logicielles du Scheduler**, et non un phénomène observé ou appris par l'individu.

## Correction minimale et frontières conservées

**Code : commit `5d6b3736257417e7a013d4f1ed22331caf15790d`, `src/lab/compute_budget.py`.**

- `open_cycle` n'admet que le type Python `int` exact et une valeur ≥ 1. La validation précède la remise à zéro du compteur de cycle et de la consommation par module. Tous les types non canoniques sont refusés avec `ValueError`.
- `charge` exige que `module` et `operation` soient des chaînes Python exactes présentes dans le registre, et que `count` soit un `int` exact ≥ 0. Aucune coercition silencieuse de `bool`, `float`, NaN, infini, `Decimal`, `Fraction`, texte ou conteneur n'a lieu. Les champs sont validés **avant** calcul du coût ou écriture sur les compteurs.
- L'appel `charge` avant ouverture d'un cycle conserve son erreur `RuntimeError`. Les comptes entiers **0, 1 et 2** restent valides, avec les charges et les `BudgetCharge` originaux ; `count=0` conserve son effet historique de zéro UC et sa clé de module à valeur nulle. Les refus sous enveloppe, plafond global et capacité protégée conservent leurs coûts et motifs.
- `ComputeBudgetConfig.validate`, `quote_operations`, `restore_causal_state`, les coûts UC P-43, les seuils cognitifs, Planning, Exploration, Action Control, le monde, les événements, le journal et la structure des snapshots **ne sont pas modifiés**.

Les APIs de producteur sont durcies ; ceci n'est pas présenté comme une protection contre du code Python hostile accédant aux attributs privés.

## Tests de non-régression

**Tests : commit `ee9aa8803e4e81045c4a2defd5224036eff92de8`, `tests/test_compute_budget.py`.** Quatre nouvelles méthodes ont été ajoutées, passant de **904** à **908** tests de dépôt :

1. **18 valeurs de cycle invalides** : booléens, zéro/négatif, floats entiers et fractionnaires, NaN, ±infini, `Decimal`, `Fraction`, texte, `None` et conteneurs. Chaque échec conserve l'état exact et les `canonical_causal_bytes` d'un cycle déjà débité, ainsi que la lecture `quote_operations`. Un cycle valide peut ensuite être ouvert et renouvelle normalement son enveloppe.
2. **19 comptes d'opération invalides** : booléens, négatifs, floats dont `1.0`, NaN, ±infini, `Decimal`, `Fraction`, texte, `None` et conteneurs. Rejet avant comptabilisation, conservation exacte des UC et du devis Scheduler, puis charge entière ordinaire acceptée.
3. **12 combinaisons d'identifiants invalides** : module ou opération inconnus, booléens, numériques, `None`, mappings et listes non hashables. `ValueError` avec état inchangé ; `RuntimeError` d'un cycle non encore ouvert conservé.
4. **Charges valides + snapshot indépendant** : `count=0`, `count=2`, opération configurée à coût nul, `count=1` implicite, refus `protected_capacity` exact sans consommation, capture périodique avec `SnapshotManager`, progression d'un cycle puis restauration. Deux exécutions indépendantes reproduisent les mêmes reçus `BudgetCharge`, identifiants de snapshot, états propriétaires, octets de journal et hashes. Les reçus `snapshot_taken` et `snapshot_restored` sont conservés et le journal reste append-only.

Ces 49 cas d'entrée malformée sont des **sous-cas synthétiques au sein de trois méthodes** ; il ne faut pas les additionner aux 908 tests comme s'ils constituaient 49 méthodes supplémentaires. Aucune donnée physique du monde ou vérité de danger caché n'est promue en fait cognitif.

## Validation GitHub Actions sur SHA exact

| Contrôle réellement exécuté | Code/tests SHA | Environnement | Résultat |
| --- | --- | --- | --- |
| [CI courte #38139806118](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38139806118) | `ee9aa8803e4e81045c4a2defd5224036eff92de8` | **Python 3.12.15** | **908/908 PASS**, 122,568 s, bootstrap réussi |
| [CI complète #38139987533](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38139987533) | **même SHA** | **Python 3.11.17** | **908/908 PASS**, 92,268 s, job complet **SUCCESS** |
| [CI complète #38139987533](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38139987533) | **même SHA** | **Python 3.12.15** | **908/908 PASS**, 140,171 s, job complet **SUCCESS** |

Le workflow complet comprend **deux jobs exécutés avec succès et aucun échec**, ainsi que **15 artefacts techniques** : journaux de référence Stages 1–8 disponibles, diagnostics Stage 9 et états de préparation scientifique. Son job unitaire supplémentaire a été intentionnellement `skipped` par le contrôle de coûts et ne compte pas comme troisième validation. Les exécutions automatiques ignorées en Draft ne sont pas présentées comme des tests exécutés. Ces diagnostics techniques ne constituent ni un Golden scientifique gelé ni une campagne prospective held-out.

## Portée réelle et travaux restants

**Démontré par les tests exécutés :** sur les valeurs malformées inscrites au protocole, les APIs `open_cycle` et `charge` refusent avant mutation les identifiants de cycle non canoniques, les comptes UC non entiers et les identifiants invalides ; les opérations entières normales gardent le même contrat ; la capture, la restauration et les octets causaux d'exécutions indépendantes restent reproductibles ; les suites intégrées disponibles sous Python 3.11 et 3.12 sont vertes sur le nouveau SHA.

**Non démontré :** défense contre du code Python hostile modifiant les membres privés, validité universelle de tout encodeur externe, amélioration des politiques de besoins ou de danger, planification optimale, reconnaissance de disparition d'un danger, récupération autonome, acceptation Golden historique indépendante ou succès scientifique Stage 9. Les comportements négatifs documentés au Stage 11 ne sont pas modifiés par cet incrément.

**Verrous logiciels distincts identifiés pour investigation future (non modifiés ici) :** `ComputeBudgetConfig.validate` utilise toujours des comparaisons numériques permissives sur les paramètres versionnés (plafonds, enveloppes et coûts) ; la possible réouverture répétée d'un même cycle légitime doit être analysée au regard du Scheduler avant toute modification de la sémantique de cycle. Ces pistes requièrent une recherche d'utilisations et un protocole séparé. Les scénarios comportementaux multi-pas sous besoins concurrents restent incomplets.

### Reproduction

À partir du **SHA de code/tests** `ee9aa8803e4e81045c4a2defd5224036eff92de8` dans un checkout du dépôt installé sous Python 3.11 ou 3.12 :

```sh
python -m pip install -e .
python -m unittest discover -s tests -p 'test_compute_budget.py' -v
python -m unittest discover -s tests -p 'test_stage11_geographic_capacity_guard.py' -v
python -m unittest discover -s tests -p 'test_snapshots.py' -v
python -m unittest discover -s tests -q
```

Le rapport et tout commit documentaire ultérieur sont **postérieurs** au SHA testé ; ils ne changent ni les résultats de celui-ci ni les preuves scientifiques. **Stage 11 EN COURS ; Stage 9 scientifique NO-GO ; PR #25 Draft/non fusionnée ; `main`, permissions, protections et spécification normative v1.2.1 inchangés.**
