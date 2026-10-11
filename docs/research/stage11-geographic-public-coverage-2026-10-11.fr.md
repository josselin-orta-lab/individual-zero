# Stage 11 : exploration géographique autonome, diagnostic public

**Date :** 11 octobre 2026 (Europe/Paris). **Classification :** diagnostic logiciel sur monde public. **Ni expérimentation held-out, ni acceptation scientifique, ni Golden Stage 9.**

[Protocole établi avant les résultats](stage11-geographic-public-coverage-protocol.en.md).

## Provenance exacte

- Code réellement testé : commit `cdebdea67f34036969e0bb9dc139c4fa3c28cf35`, branche `i0/vnext-stages-10-12`.
- [GitHub Actions #38111306583](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38111306583) : **745 tests réussis** sous Python 3.12, contrôle smoke inclus. Campagne complète des Goldens et Python multi-versions **non exécutée**.
- Version du diagnostic : `stage11-public-frontier-coverage-dev-v1`.
- Commande de reproduction : `python -m lab.stage11_geographic_probe`.
- Monde public : `stage4-reference-world-v1`, équipement figé `E-v1-stage6-reference`, position initiale `(2,2)`.
- Corps initial : énergie 50, nourriture 60, eau 60, intégrité 100 ; les besoins de cette fixture sont initialement satisfaits.
- Durée : 8 pas de monde. Aucune graine ou monde dissimulé, hypothèse causale injectée, destination imposée, oracle ou récompense artificielle.

## Résultats observés

| Indicateur | Stage 9 | I0-vNext sans géographie | I0-vNext avec géographie |
| --- | ---: | ---: | ---: |
| Positions distinctes réellement perçues | 1 | 1 | **8** |
| Déplacements autonomes géographiques appliqués | 0 | 0 | **8** |

Dans la variante géographique :
- **8** propositions de déplacement Planning, **8** évaluations intrinsèques et **8** commandes réellement exécutées ;
- **1** déplacement vers le nord, puis une progression latérale vers des cases encore non visitées ;
- **8** destinations proposées avec prédiction numérique Equipment indisponible, sans inventer d'effet attendu ;
- **8** positions effectivement observées dans le journal Perception et **8** sites distincts conservés par Exploration ;
- les pas observés sont, dans l'ordre : `(2,2)`, `(2,1)`, `(3,1)`, `(4,1)`, `(5,1)`, `(6,1)`, `(7,1)`, `(8,1)`.

**Important :** la huitième commande est effectivement envoyée, mais la nouvelle position après ce dernier envoi ne devient une visite confirmée qu'à la prochaine capture. Le diagnostic ne lui accorde donc pas de neuvième site imaginaire.

## Empreintes

- Journal Stage 9 : `958dc306b4feb7c3aa42b6a0383fb385a7887d7028218b2aaf9fd848e7499f93`.
- Journal I0-vNext sans géographie : `79ea747c91398819c32255d7090cd348f0f8b6301d3a706ced063183a0ada1d7`.
- Journal I0-vNext avec géographie : `7fd0c888a91032d3a8f9f70f5ff156218c316915243ade67ceb03a4773784c5a`.
- Diagnostic canonique : `d956c91d871dc12c875d0cbd2a37696efc9d1208dddfcae081bb01b1619b8b1c`.

Le test compare deux réexécutions identiques du protocole et vérifie les journaux. Les empreintes sont des contrôles d'intégrité logicielle, **pas** une attestation scientifique indépendante.

## Corrections et garde-fous

La première campagne de ce sous-ensemble ([CI #38110842287](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38110842287)) a détecté deux échecs d'intégration : l'Equipment E-v1 à corpus exact n'avait pas de prédiction pour le mouvement proposé. Le correctif permet à Planning de proposer une action locale vérifiée comme adjacente et praticable avec le statut de prédiction **indisponible**, sans valeur numérique fictive. Le contrôle d'admissibilité et le veto restent inchangés.

Le dernier contrôle couvre également les effets E-v1 qui ne prédisent que l'axe modifié, l'invalidation des faux motifs d'exploration et la suppression des nouvelles cibles lors d'un cycle dégradé. Le registre de visites est inclus dans le snapshot versionné du propriétaire unique Exploration ; le mode désactivé conserve le schéma antérieur.

## Limites explicites

Une augmentation de couverture de 1 à 8 sites, dans un seul monde connu et une fenêtre de 8 pas, ne constitue ni une généralisation, ni une preuve que la politique exploratoire est optimale ou sûre à long terme. La fixture n'évalue pas les menaces, le sommeil, les obstacles rares, les environnements cachés ou les effets d'une fatigue prolongée. L'absence de prévision Equipment complète n'est pas une réussite de prédiction.

Le Stage 11 reste **EN COURS** : restent notamment la couverture sur plusieurs cartes publiques, l'habituation sur des classes d'activités, les transitions de modulation menaces/récupération en conditions réelles, les contraintes du budget dégradé et les réexécutions Golden étendues.

Le Stage 9 demeure **SOFTWARE IMPLEMENTED / SCIENTIFIC VALIDATION PENDING / NO-GO** ; aucune campagne held-out n'est autorisée par ce résultat.
