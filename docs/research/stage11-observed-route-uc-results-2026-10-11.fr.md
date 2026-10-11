# Stage 11 : routage observé, carrefour et budgets UC, résultat de développement

**Date :** 11 octobre 2026. **Classification :** diagnostic logiciel public, non held-out, non Golden, non scientifique. **Norme immuable :** `docs/architecture/reference/en/mvp-specification-v1.2.1.md`. Stage 9 reste **NO-GO scientifique**.

## Protocole, implémentation et résultat positif borné

- [Protocole de routage déclaré avant modification](stage11-visited-frontier-route-protocol.en.md), commit `9c83f6d8`.
- Premier code opt-in intégré : `c7eb9f69e346a0377bf804f9092380b8fc78f8e1`, [CI #38118627781](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38118627781) : **806 tests Python 3.12 PASS** et smoke PASS.
- Sur le carrefour physique ouvert de dix pas, positions observées : **(2,2), (3,2), (4,2), (3,2), (2,2), (2,3), (2,4), (2,4), (2,4), (2,4)**. L'individu exécute deux transits vers des lieux déjà observés avant de découvrir la branche sud. Le test est réellement opt-in ; les alternatives et les sites visités proviennent des captures Perception, non de la carte privée Lab.
- Le contrôle sans branche sud ne revient pas au carrefour et ne déclare aucune branche sud explorée. Les tests valident également le budget Planning nul, la réexécution exacte des journaux et l'absence d'offre résiduelle sur refus.

## Campagne de la matrice UC : échec de test archivé, seuil physique conservé

[CI #38118919050](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38118919050), commit `d1720b26` : **811 tests exécutés, 1 échec** dû à une *assertion de test* stipulant à tort que la recherche consomme 0 UC dès lors que 3 UC ne suffisent pas pour exécuter le transit. Aucun mécanisme n'a été retouché pour satisfaire cette attente. Correction des seules assertions dans `d0583668`, en attente de sa validation CI séparée.

Observations brutes, 10 pas par variante, avec source et empreintes disponibles dans les journaux de l'exécution GitHub :

| Configuration | UC recherche Planning acceptées cumulées | UC préflight acceptées cumulées | UC build acceptées cumulées | Transits physiques appliqués | Branche sud observée |
| --- | ---: | ---: | ---: | ---: | --- |
| Carrefour ouvert, budget de référence | 25 | 8 | 16 | 2 | Oui |
| Carrefour scellé, budget de référence | 40 | 2 | 4 | 0 | Non |
| Carrefour ouvert, Planning 0 | 0 | 0 | 0 | 0 | Non |
| Carrefour ouvert, Planning 1 | 0 | 49 | 0 | 0 | Non |
| Carrefour ouvert, Planning 2 | 0 | 49 | 0 | 0 | Non |
| Carrefour ouvert, Planning 3 | 40 | 41 | 4 | 0 | Non |
| Carrefour ouvert, Planning 4 | 25 | 8 | 16 | 2 | Oui |

**Les UC du tableau sont des sommes entre cycles cognitifs, pas un budget disponible pour un seul cycle.** À 3 UC par cycle, la recherche d'itinéraire (1 UC) et le préflight canonique (1 UC) sont finançables, mais la construction de l'option (2 UC) est refusée : 40 UC de recherche sont consommées pendant les répétitions et **aucun transit n'a lieu**. À 4 UC, la chaîne complète est financée et la trajectoire réussit dans ce scénario. Les résultats `planning_1` et `planning_2` illustrent également des préflights payants qui n'aboutissent pas à l'exécution.

## Limites et suite

- Le retour sur deux pas est **une capacité logicielle locale bornée, observée une fois sur un carrefour public** ; aucune généralisation ni planification de long horizon, apprentissage d'un danger, ou acquisition de connaissances causales n'est démontrée.
- Il reste à tester séparément, sans oracle, le **blocage actuel d'un transit connu** et sa **reclassification létale par les faits canoniques**, avec journalisation de la prévalidation, de Competition et du veto Action Control. Les changements de danger inconnus ne deviennent jamais des connaissances initiales.
- Le routage est **désactivé par défaut**. La suite complète Python 3.11 et les Goldens demeurent **NON EXÉCUTÉS**. La PR #25 reste brouillon, dépôt privé, Stage 11 **EN COURS**, Stage 9 **NO-GO scientifique**.

Reproduction de développement :

```sh
python -m pip install -e .
python -m unittest tests.test_stage11_observed_route_integration tests.test_stage11_routed_junction_budget_matrix -v
python -m lab.stage11_routed_junction_probe
```
