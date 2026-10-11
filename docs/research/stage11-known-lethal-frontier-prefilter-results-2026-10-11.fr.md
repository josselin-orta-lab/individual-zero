# Stage 11 : préfiltrage des frontières interdites par Action Control

**Date :** 11 octobre 2026 (Europe/Paris). **Classification :** diagnostic de développement logiciel public, non held-out. **Verdict scientifique : aucun.**

## Source et protocole

- **Code testé :** `f2279d543f50ab19d1a5afea2d92f80dcc97aa53` ; [GitHub Actions #38112524964](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38112524964), **756 tests réussis** sur Python 3.12, plus vérification smoke.
- [Protocole v3 enregistré avant les tests](stage11-known-lethal-frontier-prefilter-protocol.en.md).
- Exécution ciblée : `python -m lab.stage11_geographic_robustness_probe` et `python -m lab.stage11_geographic_probe`.
- Variante du diagnostic cartographique : `stage11-public-frontier-layout-robustness-dev-v3`.
- Le contrôle porte exclusivement sur les mondes physiques publics de développement, chacun avec un clone I0-vNext sans géographie, sur **6 pas**. La matrice des Goldens, l'autre version Python et tout held-out restent hors de ce résultat.

## Correctif

La spécification anglaise v1.2.1, §9.4, autorise Planning à demander à `Action Control.verifier_admissibilite` si une option est admissible, avant de la finaliser. Les seules directions supprimées sont celles que ce service déclare explicitement **inadmissibles** pour la perception locale du moment.

Une direction dont le statut est `indeterminate` demeure un candidat ; elle n'est pas classée artificiellement sûre, dangereuse ou interdite. La suppression intervient **avant** la limite de cibles Exploration et avant une simulation ou facturation `planning_build`. Les faits de sécurité ne sont jamais dupliqués dans Exploration : la décision est relue lors de chaque cycle et le veto final Action Control reste actif.

Le contrôle préliminaire est borné aux **quatre cellules adjacentes perçues**, et sa charge a été ajoutée explicitement à la configuration vNext activée : `geographic_admissibility_preflight = 1 UC` du budget ordinaire de Planning par cycle accepté. Le mode géographique désactivé ne possède pas cette nouvelle opération.

Un événement `stage11_geographic_admissibility_prefiltered` par pas physique concerné consigne la direction, la destination, la source `action_control.verifier_admissibilite`, le caractère `inadmissible` et le coût logique du contrôle. Cet événement n'est ni une preuve causale, ni une découverte d'un site inconnu.

## Résultats comparatifs publics

| Carte | Rejets Planning dus à une cible impossible | Frontières filtrées par admissibilité | UC de préfiltrage acceptées | Sites perçus, avec géographie |
| --- | ---: | ---: | ---: | ---: |
| Obstacle nord | 0 | 0 | 22 | 3 |
| Couloir est | 0 | 0 | 6 | 6 |
| Créature au nord | 0 | 0 | 8 | 5 |
| Zone létale connue au nord | **0** | **4** | **22** | **3** |

Le scénario létal connu précédent, dans [le rapport v2](stage11-local-modulation-geography-results-2026-10-11.fr.md), produisait **21 rejets Planning**. Le nouveau diagnostic v3 n'en produit **aucun**, sans visite de zone létale connue. Les quatre exclusions concernent les pas physiques **3, 4, 5, 6**.

La couverture observée reste identique à la campagne v2 sur les quatre cartes, et les trajectoires publiques ne contiennent toujours **aucune visite de case occupée par la créature ni d'une zone létale connue**.

Une vérification de contrat supplémentaire, indépendante du monde physique, confirme qu'avec une seule cible autorisée par cycle, si le nord est explicitement interdit, une autre direction praticable est choisie. Lorsqu'un service Action Control simulé requalifie le nord en `indeterminate`, la direction redevient candidate à la consultation suivante : aucun cache d'interdictions permanent n'est créé.

**Attention à l'UC :** le coût propre aux préconsultations est réel, y compris pendant des cycles sans mouvement choisi. La disparition de 21 rejets coûteux ne suffit pas à démontrer une **diminution du coût total** de Planning, car la correction peut aussi ouvrir d'autres options admissibles et entraîner d'autres évaluations. Un profilage global UC de la même trajectoire avec et sans optimisation reste à faire.

## Empreintes SHA-256 du diagnostic v3

| Carte | Entrées publiques | Résultat canonique | Journal géographique |
| --- | --- | --- | --- |
| Obstacle nord | `639b9545f68cb9dccc063a77e0637cfc28634e146dba5dbe056c01e17a2360e9` | `b96b1c80020646c8afdcfd77c0f7de787e905fabd04ffa3d8b276428f673b10f` | `a3428f7fe314e8452e2b763e1e5f381c6c5e778f426fcc61a2e1d7ef89a11525` |
| Couloir est | `8fafa578d35887d2780e9457653ea1c9de3d451b94e1ca8268f6805671e7ed42` | `4462a8182f29f479ea2a6f87b57673364315e800bae2591bb42123db3304efab` | `26347aed49705312e93dd3fe4530e2fae5db004ffc567403410273feb6e493cb` |
| Créature nord | `78e495a720c980aa326cd3da1728301b6cb19e3a8585c3ae700cf70addb4a673` | `4c8a8a904eaca93bff1eab23d6a4ef7754d79039e4c770a46e0fdeec58727827` | `171c2150f0e614235ad813c20c64cbb15b33199510c2598ee3b2ae60b7aa04d8` |
| Létal connu nord | `20826aac98c84c0e269ca1f4799c4d201dec9d8ae5382c26508958e4274277db` | `553cf4bbfbf5de7af36060e2d187dfe2ebdc3eca2ab1370af948d9e7ef26a14a` | `a24efd24bbf076665d9585c94cf73fc875b933ddb457fabd4803e199a7fb8316` |

Le contrôle huit pas de couverture libre garde : Stage 9 = **1** site, I0-vNext sans géographie = **1** site, I0-vNext avec géographie = **8** sites. Ce contrôle conserve l'identifiant de protocole `stage11-public-frontier-coverage-dev-v2` mais son empreinte de diagnostic change, car le code et les opérations UC ont évolué. Empreinte de ce diagnostic à ce commit : `c4dd4c8759971ca6458dda5ef901cfb561270f651a3fc59796c3835e4283d768`.

## Limites et statut

Les exclusions n'utilisent ni une carte cachée ni une classification exacte du danger du monde. Les risques non connus de l'individu demeurent incertains, et le système pourrait encore les rencontrer. La frontière visible, les contrôles sur la mémoire des visites, le mode dégradé et le veto Action Control restent distincts.

La campagne ne valide ni la généralisation à des cartes inconnues, ni la performance longue durée, ni une amélioration globale UC, ni la sécurité scientifique, ni les Stages 10 et 12.

**Stage 11 EN COURS ; Stage 9 SOFTWARE IMPLEMENTED / SCIENTIFIC VALIDATION PENDING / NO-GO.** La PR reste en brouillon et ne doit pas être fusionnée sur cette seule preuve.
