# Références scientifiques externes pour I1

**Créé le 26 octobre 2026** : [issue #545](https://github.com/josselin-orta-lab/individual-zero/issues/545). Ce registre est destiné aux **agents de recherche et développement**, non à la mémoire d'un I1 vivant.

## Autorité, provenance et usage
La théorie d'I1, les contrats actifs et les effets physiquement observés restent l'autorité. Un article ne constitue ni une connaissance innée pour I1 ni la preuve qu'une capacité fonctionne chez lui. La bibliographie est **non normative**, non chargée au démarrage ; aucune importation d'algorithme, de données d'entraînement, de vérité du simulateur, de récompense ou de priorité motrice n'est autorisée par le seul fait qu'une référence existe.

Séparer : **SOURCE INSPECTÉE**, **RÉSULTAT RAPPORTÉ PAR LES AUTEURS**, **INFÉRENCE I1**, **HYPOTHÈSE À TESTER**, **EFFET SCIENTIFIQUE NON DÉMONTRÉ**.

## Catalogue
| Famille | Source figée à la collecte | Utilité potentielle | Licence / réserve |
| --- | --- | --- | --- |
| Soar | [source](https://github.com/SoarGroup/Soar/tree/3fc337a1ab2d04b9e5183335c1496d7dcdc57c1c) | mémoire épisodique, crédit différé, compilation | BSD |
| MicroPsi2 | [source](https://github.com/joschabach/micropsi2/tree/74a2642d20da9da1d64acc5e4c11aeabee192a27) | besoins, urgence, intentions | MIT sauf exceptions |
| LIDA | [source](https://github.com/CognitiveComputingResearchGroup/lida-framework/tree/26bc3b2b34bf7ccfe2c62e1f12314db27d9719ec) | attention, accès contextuel à la mémoire, procédures | non commerciale |
| DreamerV3 | [source](https://github.com/danijar/dreamerv3/tree/e01491fad6434b2245a3b8ca201dd7faedcc458c) | prévision et anticipation de transitions | MIT |
| OpenCog Hyperon | [source](https://github.com/trueagi-io/hyperon-experimental/tree/3f76dc460da6961f57f69f6c3e550c59c74ada83) | représentations de relations et attention | MIT, pré-alpha |
| iSEED | [article](https://doi.org/10.3389/fnbot.2026.1920808) | organisation et stabilité des épisodes | article accessible ; source et données brutes non confirmées ouvertes |

- [Étude comparative datée](COGNITIVE_ARCHITECTURES.md) : hypothèses, limites et rapprochements.
- [Questions et protocoles](RESEARCH_QUESTIONS.md) : 12 hypothèses proposées, liées aux owners d'I1.
- [Index de sources CSV](sources-2026-10-26.csv) : **36 entrées**, dont les fichiers I1 de la comparaison.
- [Manifeste de collecte JSON](research-data-2026-10-26.json) : SHAs, données publiées et inventaire des scores.
- [Handbook I1](../README.md) et [matrice des preuves](../EVIDENCE_MATRIX.md).

**Distinction des versions :** l'analyse historique du moteur concerne le SHA `972aac6ca64a8517dbbee8604f7a1e5108474473`. La base de cette intégration documentaire est `9dd992e6f49bb9de3b7236f4728c76e039327f46` ; les modifications éventuelles survenues entre les deux ne sont **pas** réévaluées par la collecte.

**Données externes non importées :** 27 fichiers de scores DreamerV3 inventoriés, mais binaires non téléchargés ni réanalysés ; résultats iSEED recopiés depuis les tableaux publiés, sans données brutes.

## Procédure de recherche ultérieure
1. Partir d'un défaut ou d'une question falsifiable d'I1, puis identifier l'owner et l'issue existants.
2. Utiliser le CSV pour retrouver la source primaire, et lire le code à son SHA quand elle est vérifiable.
3. Distinguer méthode documentée, résultat publié, limite de l'implémentation et simple proposition pour I1.
4. Réexaminer le **HEAD actuel** du dépôt, les PR ouvertes et les obligations UC/M11/Competition avant tout développement.
5. Prédéfinir une expérience contrôlée, avec négatifs, ablation, contre-exemple et attribution ; ne pas reprendre des connaissances externes comme règles de naissance.
6. Déposer une nouvelle note datée à côté des précédentes sans réécrire a posteriori les conclusions historiques.
