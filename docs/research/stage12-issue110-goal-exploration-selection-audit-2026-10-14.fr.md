# Issue #110 : sélection exploration contre objectif alimentaire actif (14 octobre 2026)

**Source instrumentée:** `8d7a4294d8f97cd42b232efabb5962a9eb9c331e`; [workflow #38541347317](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38541347317). Instrumentation uniquement côté évaluateur en lisant les événements déjà présents dans le journal; aucun état, coût, objectif, seuil ni politique d'I0 n'a changé. Le fichier `motive-trace.json` est conservé dans chaque archive CI.

## Constat réellement observé

Les six vies ont **toutes** activé un but `eat` / `food` dès le premier pas (référence `goal:eat:food:1:2`). Il est donc incorrect de déduire « zéro objectif » de l'absence de `stage12_goal_progress_preregistered` : ce dernier est uniquement un *engagement opératoire* de sous-critère d'objectif lorsqu'une commande `active_goal` est effectivement admise.

Sur les six vies de 36 pas, les décisions lisibles sont `cible_exploration` (27 ou 28 par vie) et `sleep_pressure` (4 ou 5 par vie). **Aucune sélection de motif `active_goal`**. Le premier déplacement est un `geographic_frontier:2:1` depuis (2,2), et le deuxième une exploration `geographic_frontier:3:1` alors que la nourriture se trouve à (3,1). Le but alimentaire existe, sa pression augmente, mais les décisions ne sont pas étiquetées ni justifiées par ce but. Pas de refus UC dans les reçus inspectés.

| Profil | Vies | But eat actif | Motifs exploration/vie | Sommeil/vie | Motifs active_goal | Critères Stage12 |
| --- | --- | --- | --- | --- | --- | --- |
| sustained | libre, A2 | oui | 27 / 27 | 5 / 5 | 0 | 0 |
| episodic | libre, A2 | oui | 28 / 28 | 4 / 4 | 0 | 0 |
| marginal | libre, A2 | oui | 28 / 27 | 4 / 5 | 0 | 0 |

La différence est **entre activation d'un but et sélection d'une option au service du but**, pas dans le calcul du détecteur d'attribution. Avant tout correctif, il faut vérifier si les options Stage6 alimentaires sont bien proposées/admissibles ou si Exploration l'emporte dans la compétition. Une option exploration qui arrive physiquement sur la ressource peut être utile mais ne doit pas recevoir rétroactivement le statut `active_goal`, qui reste un motif préengagé vérifiable. Un changement éventuel de priorité/compétition requiert un arbitrage architectural et des régressions trans-stages.

## Contrôle numérique distinct

Le compare-job [#38539808519](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38539808519) a déjà isolé une différence d'ULP IEEE-754 dans `stage8_option_evaluation.learned_value`, sous Python 3.11/3.12. Le calcul `LinearTDValues.q()` utilise `sum(weight * feature for ...)`, qui doit être audité quant à la compatibilité des sommations; **aucun arrondi ni conversion rétroactive des hachages existants n'a été introduit**. La divergence de journal reste réelle et la reproductibilité binaire inter-Python n'est pas démontrée.

**Verdict : PARTIAL**. L'implémentation A2 et les audits précédents restent inchangés, pas de preuve suffisante pour calibrer le détecteur `attribution_bias`. PR #155 en brouillon sans fusion, issue #110 ouverte, Stage12 non reçu.
