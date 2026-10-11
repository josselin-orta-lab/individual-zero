# Stage 11 : diagnostic public longitudinal, danger inconnu et budget Planning

**Date :** 11 octobre 2026. **Statut :** résultat logiciel reproductible de développement, non held-out et non scientifique. **Stage 9 : NO-GO scientifique inchangé.**

## Antériorité et exécution

- [Protocole déclaré avant l'implémentation et les essais](stage11-multistep-unknown-danger-budget-protocol.en.md), commit `e464bf6c7e64b49103f6bbb91f9f2d18dd20c782`.
- Sonde versionnée `src/lab/stage11_multistep_probe.py`, protocole `stage11-public-longitudinal-corridor-dev-v1`, et régressions `tests/test_stage11_multistep_probe.py`.
- **Code testé :** `bff8a289c8a6d562891314e0b3ee30a0540d8a2e`. [GitHub Actions #38115727012](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38115727012) : **783 tests unitaires réussis sous Python 3.12.15**, puis bootstrap smoke réussi. La suite complète Python 3.11 et les Goldens n'ont PAS été exécutés.
- La sonde a été invoquée et ses trois lignes `stage11_longitudinal_public` conservées dans les logs de la CI. Les deux exécutions identiques par variante ont produit des résultats et journaux canoniques exactement égaux, vérifiés par les tests. Aucun résultat held-out ni évaluation scientifique n'a été produit.

## Résultats observés sur 8 pas physiques consécutifs

| Variante | Positions Perception successives | Commandes géographiques appliquées | Dommages de zone observés | Intégrité finale | Planning préconsultation / construction : UC acceptées | UC Planning refusées |
| --- | --- | ---: | ---: | ---: | --- | ---: |
| `corridor_clear` | (2,2), (3,2), (4,2), puis (4,2) répété 5 fois | 2 | 0 | 100 | 2 / 4 | 0 |
| `corridor_unknown_danger` | même trajectoire que témoin | 2 | 5 (une transition) | 95 | 2 / 4 | 0 |
| `corridor_unknown_danger_planning_0` | (2,2) aux 8 captures | 0 | 0 | 100 | 0 / 0 | 39 |

Les deux premières variantes ont **3 sites distincts effectivement perçus**, contre **1** pour Planning 0 UC. La première décision physique est exactement la même dans les variantes témoin et danger inconnu : déplacement vers l'est, de (2,2) à (3,2). Les empreintes de l'observation locale initiale sont identiques : `ea38f29c9a8144ea8a774f2160dc90a6debc1dbcb8c82a00d76e32f3b181a694`. Le danger réel n'a donc pas fuité dans la première observation ou la première décision de ce dispositif.

En fin de parcours, les deux variantes mobiles restent sur (4,2) après avoir visité les trois cases successives. **Aucun retour arrière autonome ni évitement prospectif démontré**. Après la transition qui inflige 5 points de dommage, le statut canonique de la zone (3,2) reste `unknown` : aucune reconnaissance causale du danger ne peut être attribuée à cet essai. À Planning 0 UC, **39 demandes UC ont été refusées** mais non consommées ; aucune cible géographique n'a survécu ni été exécutée. Ces refus ne sont ni une preuve de danger ni une preuve d'absence de nouveauté.

## Provenance canonique des résultats

| Variante | SHA-256 du résultat | SHA-256 du journal | Tête du journal |
| --- | --- | --- | --- |
| Corridor témoin | `7a4b9f02af74bc55fdc1b6399584cb8824b16c0fd7229548e1638e5c1f798292` | `2d8998f7bb3ae1fdd25b844aeda0b7176bfa2e24f5edf302583665088c06ca75` | `767ab267046e4448fb9f23151cacbfd67b34c947f26bf4cb8372949bf0f3e8a2` |
| Corridor dangereux inconnu | `6d12a752d734022000a642935f6912083771374317c7b15f37ec343344645f17` | `a13c6081ceb79a1021b80303891da609ba27e5044d989ac2d00f93eba41f5250` | `c839597422593bc24613a7334375492c02ccc659096037ad04fb8cac2d983b70` |
| Danger inconnu, Planning 0 | `9f2dae62511b5ee94b27c3dd44599f3f9d301cea150e80322938c24e8c8643c5` | `f1e55bb14ee77ad2f002df6d0a991b3804d96ce86238334ba4311f94975b7ce5` | `a7a0589d4460f67db24e0d8ed6028e58c7ece25b13517ff349e6d209d3c03160` |

SHA-256 des configurations : témoin `5705581e4ebc484e7665513c2c55e1e03b9d42a2f2c0b8aa1c3305a63eadfd22` ; danger inconnu `4f2d2eab643d8a85bfe573b05af0457a3f3725a7399396b8a41e8996db8f883c` ; budget zéro `34be4faaeb5664b493b05aebec054c18c0171c14c40f51ae05e0aa5dc7fbf4b3`.

## Reproduction minimale pour observateur

Depuis le checkout exact du commit de code ci-dessus, avec le paquet local installé (`python -m pip install -e .`), exécuter :

```sh
python -m unittest tests.test_stage11_multistep_unknown_danger_budget tests.test_stage11_multistep_probe -v
python -m lab.stage11_multistep_probe
```

Les trois lignes JSON du diagnostic portent les identifiants de protocole, les transitions subies, les positions réellement capturées et l'empreinte `evidence_sha256`. Les chemins sources de physique et de sûreté sont inchangés. Ces vérifications ciblées ne sont ni la campagne complète sous Python 3.11 ni une campagne Golden.

**Interprétation prudente :** ce dispositif public montre une impasse locale sur plusieurs pas et une non-interférence initiale du danger caché ; il ne prouve ni généralisation, ni planification à long terme, ni apprentissage du risque. Les prochaines extensions doivent isoler les embranchements avec une véritable solution alternative et les coûts de décision à horizon décalé. **Stage 11 reste EN COURS.**
