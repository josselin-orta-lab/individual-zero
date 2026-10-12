# Stage 12 / issue #132 : résultats eau, poursuite de plan et profil w_C=0 (12 octobre 2026)

**Statut : correctif logiciel ciblé PASS sous Python 3.11 et 3.12 ; validation opérateur et scientifique globale NON accordées.**

## Décision opérateur, source de vérité et protocole

L'opérateur a autorisé un profil de développement temporaire `consolidation_weight=0.0` dans P-40. **La pression de consolidation `p_cons` reste calculée** et les passes de consolidation ne sont pas désactivées par cette valeur. La règle normative v1.3.1 reste inchangée ; les vies historiques à w_C=0,5 ne sont pas réécrites. Les campagnes #132 de cette PR utilisent le nouveau profil par injection à la naissance. Il ne s'agit pas d'une décision définitive de calibrage scientifique.

Préenregistrements, par ordre :
1. [Modèle d'équipement contrôlé](stage12-issue132-water-prereg-2026-10-12.fr.md), commit `9201b90341e85c30642cd313876eb26e13fc2385`.
2. [Horizon 1 vs 2](stage12-issue132-horizon-prereg-2026-10-12.fr.md), commit `9b7a6412fa73b960bb0340500c6423801332f82d`.
3. [Continuité du plan engagé](stage12-issue132-continuation-prereg-2026-10-12.fr.md), commit `0ee74d76e19ce2f34488c190d9d527c591bc19b8`.

Les trois préenregistrements précèdent leurs essais respectifs ; aucun résultat antérieur n'est rebaptisé confirmatoire.

## Résultats, par version Python

| Scénario à 50 pas, individu distinct | Plans de but | Boire appliqué | Fatigue / sommeil | Audit |
| --- | ---: | ---: | --- | --- |
| Équipement ancien, w_C=0, h_eff=1, sans correctif de continuité | 0 | 0 | 14 dormir | PASS |
| Équipement d'exemples physiques nord/sud/boire, w_C=0, h_eff=1, sans correctif | 17 | 0 | 14 dormir | PASS |
| Même équipement enrichi, h_eff=2, **avant** correction | 17 | 0 | 14 dormir | PASS |
| Même équipement enrichi, h_eff=1, **après** correction | 17 | 0 | 14 dormir | PASS |
| Même équipement enrichi, h_eff=2, **après** correction | 2 | **1 au pas 3** | 12 dormir | PASS |

Les nombres de plans sont des événements de planification, **pas** des vies indépendantes. Les essais sont déterministes et répliqués sous Python 3.11 et Python 3.12, sans multiplication artificielle du nombre de configurations testées.

## Mécanisme effectivement isolé

Le but `drink` est actif dès le pas 1, cycle 2. Le modèle d'équipement historique possède une table exacte très étroite, qui ne couvre pas le retour vers la source après l'exploration initiale. Les exemples supplémentaires sont des **transitions effectivement appliquées** dans un monde d'entraînement de Lab, observées par la même interface accessible, avant naissance. Ils ne sont ni un Oracle dans I0 ni une récompense post hoc. Le modèle doit continuer de refuser les entrées inconnues.

Avec ce modèle enrichi, Stage6 propose le plan `[se_deplacer(south), boire]`. Sous `h_eff=1`, seule la première commande est simulée pour l'évaluation ; elle ne produit aucune amélioration de la déviation corporelle, et Exploration gagne la Competition. Sous `h_eff=2`, la conséquence du second pas est valorisée et l'option dirigée vers le but gagne au pas 2.

Avant le correctif logiciel, Stage8/Stage10 réévaluait au pas 3 **le plan complet à partir de l'état déjà atteint après le premier pas**, au lieu de son suffixe encore inexécuté, ce qui rendait la prédiction indisponible. Après correctif, l'évaluateur utilise le curseur d'Action Control **uniquement** si option et plan sont encore les mêmes et engagés. Un nouveau plan, une option non engagée ou un curseur illégitime n'obtient aucun crédit pour les pas déjà exécutés. Le simulateur, Competition, les enveloppes UC et l'autorité d'Action Control sont conservés.

Preuves du journal après correction :
- Pas 2 : `command_admitted` pour `se_deplacer`, option `option:goal:drink:water:1:2:sim:boire`.
- Pas 3 : `command_admitted` pour `boire` sous **la même option**, avec une transition WorldBody réellement appliquée.
- Pas 4 : `stage12_goal_progress_followup` pour l'intention du pas 3 avec `criterion_outcome=success`, eau initiale **20**, eau observée **60**. Le critère de progrès de déplacement du pas 2 est correctement `failure` pour l'eau : aucune amélioration fictive n'est comptée.
- Deux exports causaux indépendants et WAL correspondants, audits offline passés, exécution identique sous les deux versions Python.

## Interprétation honnête et limites

**Résolu au niveau logiciel ciblé** : la panne de continuité d'un plan de deux actions et l'absence d'équipement de développement pour cette trajectoire sont corrigées et testées. Un véritable comportement de consommation d'eau apparaît, sans commande imposée.

**Non démontré** : que l'individu aurait acquis ce modèle de transition seul, que la politique boit dans un monde non entraîné, ou que la régulation optimale du sommeil a été établie. La source du corpus a été enregistrée *hors de l'individu* avant sa naissance. Une campagne held-out avec apprentissage strictement vécu et mondes non vus reste nécessaire pour une affirmation scientifique plus générale.

**Non certifiés** : biais d'attribution #110, régulation et utilité de consolidation #133, atomicité M-11/Stage12, réception opérateur Stage12, validation scientifique finale du MVP. Stage 9 reste NO-GO.

## Reproduction

- [PR #135](https://github.com/josselin-orta-lab/individual-zero/pull/135)
- [Campagne avant correctif logiciel](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38307489417)
- [Campagne après correctif logiciel](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38308106830)
- ZIP par version : logs des vies `life-result.json`, WAL, exports et empreintes dans l'onglet Artifacts des Actions.

Conserver les résultats négatifs et conserver le profil w_C=0 comme option de développement réversible ; tout changement global de paramétrage demande ses propres tests de régression.
